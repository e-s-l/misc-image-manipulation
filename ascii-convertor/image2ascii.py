#!/usr/bin/python

############################################################
# image2ascii a.k.a. The Characterizer!
# is based off:
# https://medium.com/@shubham0473/unleash-your-inner-artist-a-step-by-step-guide-to-converting-images-to-ascii-art-using-java-97860464f19a
# and
# https://github.com/isaksolheim/image-to-ascii/blob/master/image_to_ascii.py
# and
# https://www.youtube.com/watch?v=wUQbchYY80U
##################
# imports:
import sys                  # system stuff (to get input arguments)
import os                   # operating system stuff (to get file extensions)
from PIL import Image       # Python Image Library
import numpy as np          # for the usual
import time                 # to wait (when printing shapes to the console)

###################
# control parameters:
# internal:
tolerance = 10              # um this probably shouldnt be hardcoded
debug = False               # print misc. outputs
print_culminative = True    # print the gradually building combo of all shapes
print_shapes = False         # print bfs shapes to console
save_shapes = False         # save bfs shapes to files (careful, can produce LOTS of files)
use_luminance_form = True   # formula for brightness from pixel rgb
print_to_console = True     # show results of bfs shape finder on console
# external (changed by user input):
print_to_file = False         # save final result to file
bfs_grouping = False        # use bfs shape finder or not
# The character array to map brightness to:
ASCII_CHARS = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
WOW_SNR = "123456789ABCDEFGHIJKLMNOPQRSTU"
# light to dark, left to right
char_map = WOW_SNR     # define here but properly initialise after user choice


############################################################
def preprocess_image(img_file):
    """Modify the image size to match the console, plus some minor preprocessing."""

    img = None  # initialise
    file_name, file_extension = os.path.splitext(img_file)

    if debug:
        print(file_name+'\n', file_extension)

    # open image file using PIL
    try:
        img = Image.open(img_file)
    except IOError as ioe:
        print("Error opening the image file: \n", ioe)
        print("Are u sure this is an image file? Better start again...")
        sys.exit(1)
    
    #
    # resize the image according to the output:
    w, h = img.size
    if debug:
        print('Original W, H =', (w, h))

    if print_to_console:
        # use the console to resize the image
        console_width = os.get_terminal_size().columns  # get console size
        aspect_ratio = w/h                              # would H/W be better

        new_width = console_width
        new_height = int(new_width/aspect_ratio/2)      # factor of two to account for character aspect

        img = img.resize((new_width, new_height))       # resize

    if debug:
        w, h = img.size
        print('Resized W, H =', (w, h))

    #######################
    # convert image to RBG type
    img = img.convert('RGB')

    return img, file_name


############################################################
def get_brightness(r, g, b):
    """Given a set of rgb values of a pixel, calculate brightness."""

    if use_luminance_form:
        brightness = 0.299*r + 0.587*g + 0.114*b    # luminance formula
    else:
        brightness = sum([r, g, b]) / 3             # simple average
    return brightness


############################################################
def bfs_search(matrix, start, tol, visited):
    """Breadth first search algorithm."""

    w, h = matrix.shape
    queue = [start]
    init = matrix[start]
    group = []

    while queue:
        x, y = queue.pop(0)

        if not visited[x, y]:

            visited[x, y] = True
            group.append((x, y))

            for i in range(max(0, x-1), min(w, x+2)):
                for j in range(max(0, y-1), min(h, y+2)):
                    if not visited[i, j] and abs(matrix[i, j] - init) <= tol:
                        queue.append((i, j))

    return group


############################################################
def find_shapes(matrix, tol):
    """Use the bfs pathfinder to get subsets of similar brightness."""

    w, h = matrix.shape
    shapes = []
    visited = np.zeros((w, h), dtype=bool)

    for x in range(w):
        for y in range(h):
            if not visited[x, y]:
                shape = bfs_search(matrix, (x, y), tol, visited)
                shapes.append(shape)

    return shapes


############################################################
def get_output(matrix):
    """Formatting for printing the character matrix as plain text."""

    w, h = matrix.shape
    output = ""
    for y in range(h):
        for x in range(w):
            output += matrix[x, y]
        if not y == h:
            output += "\n"

    return output


############################################################
def print_output_to_console(matrix):
    """What it says on the packet."""

    output = get_output(matrix)
    print(output)


############################################################
def save_output_to_file(matrix, file):
    """What it says on the packet."""

    output = get_output(matrix)
    f = open(file, "wt")
    f.write(output)
    f.close()


############################################################
def img2ascii_convertor(img, file):
    """First, convert the image to brightness, then map to characters."""

    # convert image into brightness matrix (averaged rgb values for each pixel)
    W, H = img.size             # get img (new) dimensions (again)
    BM = np.zeros((W, H))       # initialise (dark) matrix

    for X in range(W):
        for Y in range(H):
            pos = (X, Y)                    # get position
            pixel_rgb = img.getpixel(pos)    # get RGB
            r, g, b = pixel_rgb
            BM[X, Y] = get_brightness(r, g, b)
    #
    if debug:
        print("BM")
        print(BM)

    # the bfs tolerance should depend on the max & min of the BM...

    # initialise (empty) matrix of characters
    char_matrix = np.full((W, H), ' ', dtype=str)

    # find the character matrix:
    if bfs_grouping:
        if debug:
            print("finding shapes")

        shapes = find_shapes(BM, tolerance)
        shape_num = 0
        if debug:
            print("num of shapes =", len(shapes))
        for shape in shapes:

            # defn function to get shape matrix ?

            # initialise (empty) matrix
            shape_matrix = np.full((W, H), ' ', dtype=str)
            shape_num += 1
            #
            for x, y in shape:
                # find character for average brightness of the group:
                b_av = np.mean([BM[x, y] for x, y in shape])
                shape_matrix[x, y] = get_char_from_b(b_av)
                # add to the culminative total matrix:
                char_matrix[x, y] = shape_matrix[x, y]

            if print_to_file and save_shapes:
                save_output_to_file(shape_matrix, "shape_%i.txt" % shape_num)
            elif print_to_console:
                if print_shapes:
                    print_output_to_console(shape_matrix)
                    time.sleep(0.1)
                if print_culminative:
                    print_output_to_console(char_matrix)
                time.sleep(0.1)

    else:   # no bfs shape finder...
        for Y in range(H):
            for X in range(W):
                char_matrix[X, Y] = get_char_from_b(BM[X, Y])
    #
    if print_to_file:
        save_output_to_file(char_matrix, "%s_ascii.txt" % file)
    if print_to_console:
        print_output_to_console(char_matrix)


############################################################
def get_char_from_b(brightness):
    """Convert brightness into ascii"""

    index = int((len(char_map) - 1) * (brightness / 255.0))
    return char_map[index]


############################################################
def process_user_input():
    """Process user input."""

    global print_to_console
    global print_to_file
    global bfs_grouping
    global char_map

    # confirm required image file supplied
    if len(sys.argv) != 2:
        print("Try: python image2ascii.py <image_file>")
        sys.exit(1)

    # ask for options:
    # print to file as well as console...
    io_file = {"y", "yes", "file", ""}
    io_no_file = {"n", "no"}
    print("Would u like to print to file [y/n]? (Default is [y].)")
    while True:
        user_in = input().strip().lower()
        if user_in in io_file or user_in in io_no_file:
            print_to_file = user_in in io_file
            if print_to_file and debug:
                print("printing to file.")
            break
            ###
        else:
            print("Please enter y or n...")

    # use BFS to find shapes or not:
    io_bfs = {"y", "yes", "bfs", ""}
    io_no_bfs = {"n", "no"}
    print("Would u like to use BFS shape grouping [y/n]? (Default is [y].)")
    while True:
        user_in = input().strip().lower()
        if user_in in io_bfs or user_in in io_no_bfs:
            bfs_grouping = user_in in io_bfs
            if debug:
                print("bfs grouping", "applied" if bfs_grouping else "not applied")
            break
            ###
        else:
            print("Please enter 1 or 2, or 'bfs' or 'no'...")

    # which character map to use:
    opts_in_ascii = {"1", "ascii", ""}
    opts_in_snr = {"2", "snr", "wow"}
    print("Which character set would you like to map to:")
    print("[1]. Classic Ascii: " + ASCII_CHARS)
    print("[2]. WOW SNR values: " + WOW_SNR)
    print("(Default is [1].)")
    while True:
        user_in = input().strip().lower()
        if user_in in opts_in_ascii or user_in in opts_in_snr:
            if user_in in opts_in_ascii:
                char_map = ASCII_CHARS
            else:
                char_map = WOW_SNR
            if debug:
                print("mapping to ", "ascii" if user_in in opts_in_ascii else "snr")
            break
            ###
        else:
            print("Please enter 1 or 2, or 'ascii' or 'snr'...")


############################################################
def main():
    """Runs the subroutines."""

    os.system("clear")
    os.system("figlet -f future THE CHARACTERIZER")

    # get user choices (defaults are: save to file, use acsii...)
    process_user_input()
    # expected cli usage is: ./image2ascii.py imagefile.png
    image_file, fileName = preprocess_image(sys.argv[1])
    # call the runner
    img2ascii_convertor(image_file, fileName)


############################################################
# call initialisation function with input arg of image name
if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        print(":)")
        sys.exit(0)
    except Exception as e:
        print("There is an error: \n", e)
        print(":(")
        sys.exit(1)

############################################################
