#coding=utf-8

#!/usr/bin/python

""" Help I classify images from some folders.

Usage::
    python image_classify.py /source/folder/ /dest/folder/
"""

import os
import sys
import argparse

import Image
from ExifTags import TAGS

EXTENSIONS = ['.jpg', '.jpeg']

def get_exif_data(fname):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        img = Image.open(fname)
        if hasattr(img, '_getexif'):
            exif_info = img._getexif()
            if exif_info != None:
                for tag, value in exif_info.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except IOError:
        raise ValueError()
    return ret

def walk_folder(source_folder, dest_folder):
    os.path.walk(source_folder, on_file_visit, dest_folder)

def on_file_visit(dest_folder, dirname, names):
    for name in names:
        if os.path.splitext(name)[1].lower() in EXTENSIONS:
            path = os.path.join(dirname, name)
            handle_image(path, dest_folder)

def handle_image(path, dest_folder):
    try:
        exif_info = get_exif_data(path)
    except ValueError:
        return
    # TODO many picture don't have exif
    if not exif_info.get('DateTimeOriginal') is None:
        print path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_folder', metavar='source-folder', type=str)
    parser.add_argument('dest_folder', metavar='dest-folder', type=str)
    args = parser.parse_args()
    source_folder = os.path.abspath(args.source_folder)
    dest_folder = os.path.abspath(args.dest_folder)
    if not os.path.isdir(source_folder) or not os.path.isdir(dest_folder):
        print u'Error folder path!\n'
        parser.print_help()
        return

    walk_folder(source_folder, dest_folder)

if __name__ == '__main__':
    main()
