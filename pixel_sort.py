#!/usr/bin/python

###############
# PIXEL SORT: #
###############

# IMPORTS #
import argparse         # To process command line arguments.
import os               # For terminal actions.
from PIL import Image   # Python Image Library.
import sys              # To exit the program, etc.
import numpy as np      # For matrix maths.
from collections import deque   # double-ended queue -  to reduce pop O
from collections import defaultdict #

# FUNCTIONS #

def open_image(image_file):
    """Use PIL to open image and convert to RGB form."""
    print("open_image")

    # open image file
    try:
        img = Image.open(image_file)
    except IOError as ioe:
        print("Error opening the image file: \n", ioe)
        sys.exit(1)

    # convert image to RGB type
    img = img.convert('RGB')

    return img

def luminance(pix_rgb):
    """Given a set of rgb values of a pixel, calculate brightness."""
    r, g, b = pix_rgb
    return 0.299 * r + 0.587 * g + 0.114 * b  # luminance formula

def bfs_search(matrix, start, tol, visited):
    """Breadth First Search algorithm."""

    w, h = matrix.shape
    queue = deque([start])
    init_brightness = matrix[start]
    group = []

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]

    while queue:
        x, y = queue.popleft()

        if visited[x, y]:
            continue

        visited[x, y] = True
        group.append((x, y))

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[nx, ny]:
                if abs(matrix[nx, ny] - init_brightness) <= tol:
                    queue.append((nx, ny))

    return group

def find_shapes(matrix):
    """Use the bfs pathfinder to get subsets of similar brightness."""
    print("find_shapes")

    w, h = matrix.shape
    shapes = []     # list
    visited = np.zeros((w, h), dtype=bool)
    tol = 200

    for x in range(w):
        for y in range(h):
            if not visited[x, y]:
                shape = bfs_search(matrix, (x, y), tol, visited)
                shapes.append(shape)

    return shapes

def sort_pixels_by_brightness(pixels):
    """Sort an array of pixels by their brightness."""
    return sorted(pixels, key=luminance)

def runner(command_line_args):
    """Main function to run all components."""

    # get input arguments
    image_file = command_line_args.image_in
    debug = command_line_args.d

    # open (and preprocess) image file
    image = open_image(image_file)
    file_name, file_extension = os.path.splitext(image_file)

    # get dimensions of original image
    w, h = image.size

    # get pixels from original image
    img_pixs = image.load()

    # initialise new image
    new_image = Image.new('RGB', (w, h))

    # initialise brightness matrix
    bm = np.zeros((w, h))

    # fill out the brightness matrix
    for x in range(w):
        for y in range(h):
            p = (x, y)
            pix = img_pixs[p]
            bm[x, y] = luminance(pix)

    # based on the brightness, find shapes/areas of similar brightness
    shapes = find_shapes(bm)

    ### Processing shapes ###
    for shape in shapes:
        rows = defaultdict(list)
        for x, y in shape:
            rows[y].append((x, y))

        for y, coords in rows.items():
            all_pixels = [img_pixs[(x, y)] for x, y in coords]
            sorted_pixels = sort_pixels_by_brightness(all_pixels)

            for i, (x, y) in enumerate(coords):
                new_image.putpixel((x, y), sorted_pixels[i])

    # save end product
    new_image.save(f"{file_name}_deranged.png")
    # close original image file
    image.close()
    print(":)")

if __name__ == '__main__':
    # PARSE INPUT ARGUMENTS #
    parser = argparse.ArgumentParser(description='Takes an image file and deranges it a la pixel sorting.')

    # Add arguments:
    parser.add_argument('image_in', type=str, help='Image file to process.')  # Required
    parser.add_argument('--d', action='store_true', help='Option to enable debug mode.')   # Optional

    # Parse:
    args = parser.parse_args()

    # START RUNNING MAIN PROGRAM #
    try:
        os.system("figlet THE DERANGER")
        runner(args)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print("Error running: \n", e)
        sys.exit(1)
