#!/usr/bin/env python


import argparse

import __init__.py

if __name__ == '__main__':



    arg_parser = argparse.ArgumentParser(description="bundle a HTML file and multiple external (js|css) files " +
                                                     "to one big HTML file ")
    arg_parser.add_argument('-n', '--no-compress', action='store_true', help='disable compression')
    arg_parser.add_argument('-i', '--input-file', metavar='<file>', type=str, help='a file path - if not given, listen to stdin')
    arg_parser.add_argument('-o', '--output-file', metavar='<file>', type=str, help='a file path - if not given, output is sent to stdout')


    args = arg_parser.parse_args()

    try:
        bundled = bundle(inp, args.nc, path)
        if args.o:
            open(args.o, 'a').write(bundled)
        else:
            print(bundled)
    except :
        pass