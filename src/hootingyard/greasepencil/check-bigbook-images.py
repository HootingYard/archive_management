"""Discover broken or missings images and replace references to scaled images with their originals"""

from os import listdir, unlink
import sys, codecs, re
from os.path import join, exists
from PIL import Image
from typing import Match, Text, Set
from urllib import url2pathname, pathname2url
from glob import glob

DATA = sys.argv[1]  # book text and images

TEXT = join(DATA, 'Text')
IMAGES = join(DATA, 'Images')

UPDATE = True  # actually update the text files
DELETE = True  # actually delete unrequired image files


IMG_SRC = re.compile(r'\.\./Images/([^"]+)')
SCALED  = re.compile(r'^(.*)-([0-9]+x[0-9]+)(\.[A-Za-z]+?)$')


def broken(path): # type: (Text) -> bool
    if exists(path):
        with open(path, 'rb') as fp:
            try:
                image = Image.open(fp)
                image.verify()
                return False
            except IOError:
                pass
    return True


broken_images = set() # type: Set[Text]
replaced_images = set() # type: Set[Text]
required_images =  set() # type: Set[Text]


def report():
    print('Replaced:')
    for name in sorted(replaced_images):
        print '\t', name
    with open(join(DATA, 'required-images.txt'), 'wb') as fp:
        print('Required:')
        for name in sorted(required_images):
            print '\t', name
            fp.write(name + '\n')
    with open(join(DATA, 'broken-images.txt'), 'wb') as fp:
        print('Broken:')
        for name in sorted(broken_images):
            print '\t', name
            fp.write(name + '\n')


def img_url(img_file): # type: (str) -> Text
    return u'../Images/' + unicode(pathname2url(img_file))


def replace_img(match): # type: (Match[Text]) -> Text
    img_file = url2pathname(str(match.group(1)))
    img_path = join(IMAGES, img_file)
    match = SCALED.match(img_file)
    if match:
        orig_name = str(match.group(1))
        orig_ext = str(match.group(3))
        for possible_ext in (orig_ext, orig_ext.upper(), '.jpg', '.jpeg'):
            orig_file = orig_name + possible_ext
            orig_path = join(IMAGES, orig_file)
            if not broken(orig_path):
                replaced_images.add(orig_file)
                required_images.add(orig_file)
                return img_url(orig_file)
    if not broken(img_path):
        required_images.add(img_path)
        return img_url(img_file)
    broken_images.add(img_path)
    return img_url(img_file)


def main():
    for path in sorted(glob(join(TEXT, '*.xhtml'))):
        with codecs.open(path, mode='r', encoding='utf-8') as fp:
            text = fp.read()
        new_text = re.sub(r'\.\./Images/([^"]+)', replace_img, text)
        if UPDATE and new_text != text:
            with codecs.open(path, mode='w', encoding='utf-8') as fp:
                fp.write(new_text)
    report()
    for file in sorted(listdir(IMAGES)):
        if './Images/' + file not in required_images:
            print '-', file
            if DELETE: unlink(join(IMAGES, file))
        else:
            print ' ', file


if __name__ == '__main__':
    main()
