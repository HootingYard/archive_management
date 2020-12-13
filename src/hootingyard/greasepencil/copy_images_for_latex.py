""" Copy a book's images to the LaTeX workspace, checking for broken images.
    GIFs must be converted to PNGs because LaTeX cannot handle GIFS"""

from sys import argv, exit, stderr
from PIL import Image
from os.path import join, splitext
from os import listdir
from shutil import copy

BOOK  = argv[1]  # The book's GreasePencil data directory
CODE  = argv[2]  # The GreasePencil code and template directory
LATEX = argv[3]  # Directory to write Latex files to

IMAGES = join(BOOK, 'Images')

def latex_image_path(path):  # type: (str) -> str
    """GIF are rewritten as PNGs for LaTeX, so this
        redirects GIF file paths to their PNG copies"""
    namepart, ext = splitext(path)
    if ext.lower() == '.gif':
        return namepart + '.png'
    else:
        return path

def main():
    broken = False
    for filename in listdir(IMAGES):
        path = join(IMAGES, filename)
        namepart, ext = splitext(filename)
        if ext in {'.gif', '.jpeg', '.jpg', '.png'}:
            try:
                with open(path, 'rb') as f:
                    image = Image.open(f)
                image.verify()
            except IOError:
                print >> stderr, 'BROKEN IMAGE: %s ' % path
                broken = True
            else:
                dst_path = latex_image_path(join(LATEX, filename))
                if image.format == 'GIF':
                    with open(dst_path, 'wb') as f:
                        image.save(f, format='PNG')
                else:
                    copy(path, dst_path)
    if broken:
        exit(1)

if __name__ == '__main__':
    main()
