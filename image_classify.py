#coding=utf-8

#!/usr/bin/python

""" Help I classify images from some folders.

Usage::
    python image_classify.py /source/folder/ /dest/folder/

    This program can classify images with exif info or modified time.

"""

import os
import sys
import argparse
import shutil
from datetime import datetime, timedelta
from dateutil.tz import gettz

import Image
from ExifTags import TAGS
from dateutil.parser import parse

EXTENSIONS = ['.jpg', '.jpeg', '.png']

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
    """handle file action"""
    for name in names:
        if os.path.splitext(name)[1].lower() in EXTENSIONS:
            path = os.path.join(dirname, name)
            handle_image(path, dest_folder)

def _process_datetime(dt):
    """parse 2011:01:01 01:01:01 format"""
    d, t = dt.split(' ')
    d = d.replace(':', '-')
    return d + ' ' + t

def handle_image(path, dest_folder):
    try:
        exif_info = get_exif_data(path)
    except ValueError:
        print 'fail, %s has no exif info' %path
        return
    create_at_str = exif_info.get('DateTimeOriginal')
    if create_at_str is None: # use mtime
        print path
        print 'fail, %s has no exif info' %path
        create_at = datetime.fromtimestamp(os.path.getmtime(path))
    else: # use exif
        now = datetime.now(tz=gettz())
        try:
            create_at = parse(_process_datetime(create_at_str))
            if create_at.date() == now.date(): # get date error
                raise ValueError()
        except:
            print 'fail, %s parse exif error' %path
            return

    dest_dir_path = os.path.join(dest_folder, create_at.strftime('%Y-%m'))
    if not os.path.isdir(dest_dir_path):
        os.makedirs(dest_dir_path)
    #shutil.move(path, os.path.join(dest_dir_path, os.path.split(path)[1]))
    os.system("mv -n '%s' '%s'" %(
        path,
        os.path.join(dest_dir_path, os.path.split(path)[1])
    ))
    print 'success, %s create at %s' %(path, str(create_at))

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

