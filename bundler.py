#!/usr/bin/env python

import argparse
import os

from bundler import Bundler

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description="bundle a HTML file with multiple external (js|css) files " +
                                                     "to one big HTML file ")

    arg_parser.add_argument('-i', '--input-file', metavar='<file>', type=str,
                            help='a file path - if not given, listen on stdin',
                            dest="infile")

    arg_parser.add_argument('-p', '--path-dir', metavar='<dir>', type=str,
                           # help='',
                            dest="path")

    arg_parser.add_argument('-r', '--htroot-dir', metavar='<dir>', type=str,
                            # help='',
                            dest="htroot")

    arg_parser.add_argument('-o', '--output-file', metavar='<file>', type=str,
                            help='a file path - if not given, output is sent to stdout',
                            dest="outfile")


    arg_parser.add_argument('--strip-comments-html',
                            # help='',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS_HTML)

    # strip JS flags
    arg_parser.add_argument('--strip-comments-javascript-block',
                            # help='',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS_JS_BLOCK)
    arg_parser.add_argument('--strip-comments-javascript-endline',
                            # help='',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS_JS_ENDLINE)
    arg_parser.add_argument('--strip-comments-javascript',
                            help='forces --strip-javascript-block AND --strip-javascript-endline',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS_JS)
    arg_parser.add_argument('--strip-comments-javascript-keep-first',
                            # help='forces --strip-javascript-block AND --strip-javascript-endline',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS_JS_KEEP_FIRST)

    # strip css flags
    arg_parser.add_argument('--strip-comments-css',
                            #help='forces --strip-javascript-block AND --strip-javascript-endline',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS_CSS)
    arg_parser.add_argument('--strip-comments-css-keep-first',
                            #help='forces --strip-javascript-block AND --strip-javascript-endline',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS_CSS_KEEP_FIRST)

    # strip flags combined
    arg_parser.add_argument('--strip-comments',
                            help='forces --strip-comments-javascript AND --strip-comments-css',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS)
    arg_parser.add_argument('--strip-comments-keep-first',
                            help='forces --strip-comments-js-keep-first AND --strip-comments-css-keep-first',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS_KEEP_FIRST)


    # optimization
    arg_parser.add_argument('--optimize-js',
                            #help='forces --strip-javascript-block AND --strip-javascript-endline',
                            dest="flags", action="append_const", const=Bundler.FLAG_OPTIMIZE_JS)
    arg_parser.add_argument('--optimize-css',
                            #help='forces --strip-javascript-block AND --strip-javascript-endline',
                            dest="flags", action="append_const", const=Bundler.FLAG_OPTIMIZE_CSS)
    arg_parser.add_argument('--optimize',
                            help='forces --optimize-js AND --optimize-css',
                            dest="flags", action="append_const", const=Bundler.FLAG_OPTIMIZE)

    arg_parser.add_argument('--compress',
                            help='forces --optimize-js AND --optimize-css',
                            dest="flags", action="append_const", const=Bundler.FLAG_COMPRESS)



    source = ""; path=""; htroot=""
    flags=Bundler.FLAG_STRIP_COMMENTS | Bundler.FLAG_COMPRESS
    compress_len=120; encoding="utf-8"
    strip_tags='stripOnBundle'
    strip_inline_js="@stripOnBundle"
    strip_inline_css="@stripOnBundle"

    args = arg_parser.parse_args()

    if args.infile:
        source = open(args.infile).read()
    else:
        pass    # @TODO add stdin

    if args.path:
        path = args.path
    elif args.infile:
        path = os.path.abspath(os.path.dirname(args.infile))

    if args.htroot:
        htroot = args.htroot
    elif args.path:
        htroot = path

    bundled = Bundler(source, path, htroot, flags, strip_tags, strip_inline_js, strip_inline_css).bundle()

    if args.outfile:
        open(args.outfile, 'w').write(bundled)
    else:
        print(bundled)




rep
    echo arg_parser