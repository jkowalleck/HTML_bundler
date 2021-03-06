#!/usr/bin/env python

from bundler import Bundler

if __name__ == '__main__':

    import sys
    import os
    import argparse
    import codecs
#    import chardet


    arg_parser = argparse.ArgumentParser(description="bundle a HTML file with multiple external (js|css) files " +
                                                     "to one big HTML file ")

    # input
    arg_parser.add_argument('-i', '--input-file', metavar='<file>', type=str,
                            help='a file path - if none given, listen on stdin',
                            dest="infile")

    arg_parser.add_argument('-p', '--path-dir', metavar='<dir>', type=str,
                            # help='',
                            dest="path")

    """ @TODO add support
    arg_parser.add_argument('-r', '--root-dir', metavar='<dir>', type=str,
                            # help='',
                            dest="root")
    """

    # output
    arg_parser.add_argument('-o', '--output-file', metavar='<file>', type=str,
                            help='a file path - if none given, output is sent to stdout',
                            dest="outfile")


    # strip HTML comments
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
                            help='forces --strip-comments-html AND --strip-comments-javascript AND --strip-comments-css',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS)
    arg_parser.add_argument('--strip-comments-keep-first',
                            help='forces --strip-comments-js-keep-first AND --strip-comments-css-keep-first',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS_KEEP_FIRST)

    # strip HTML tags
    arg_parser.add_argument('--strip-tags', metavar='<tags>', type=str,
                            help='comma separated list of HTML tags to strip from the document',
                            dest="strip_tags")

    # strip markers JS
    arg_parser.add_argument('--strip-markers-js', metavar='<markers>', type=str,
                            help='comma separated list of markers. ' +
                                 'entire marked lines will ge stripped of any JavaScript',
                            dest="strip_inline_js")

    # strip markers CSS
    arg_parser.add_argument('--strip-markers-css', metavar='<markers>', type=str,
                            help='comma separated list of markers. ' +
                                 'entire marked lines will ge stripped of any CSS style definition',
                            dest="strip_inline_css")

    # strip markers JS and CSS combined
    arg_parser.add_argument('--strip-markers', metavar='<markers>', type=str,
                            help='comma separated list of markers. ' +
                                 'entire marked lines will ge stripped of any JavaScript or CSS style definition',
                            dest="strip_inline_js_css")

    # compress
    arg_parser.add_argument('--compress',
                            help='compress the output',
                            dest="flags", action="append_const", const=Bundler.FLAG_COMPRESS)

    # parse the args
    args = arg_parser.parse_args()
    del arg_parser

    #defaults and consts
    source = ""
    path = os.getcwd()
    root = os.getcwd()
    flags = 0
    compress_len = 120
    encoding = "utf-8"
    strip_tags = []
    strip_inline_js = []
    strip_inline_css = []

    infile = sys.stdin
    outfile = sys.stdout

    # @TODO add support for encoding argument

    if args.infile:
        infile = codecs.open(args.infile, 'rb', encoding=encoding)
        if not infile:
            raise Exception('can not read input file "' + args.infile + '"')

    source_lines = infile.readlines()
    infile.close()
    del infile

    # join the lines ...
    source = "".join(source_lines)
    del source_lines

    if args.path:
        path = args.path
    elif args.infile:
        path = os.path.dirname(args.infile)

    """ @TODO add support
    if args.root:
        root = args.root
    elif args.path:
        root = path
    """

    if args.flags:
        flags = 0
        for flag in args.flags:
            if flag:
                flags |= flag

    if args.strip_tags:
        strip_tags = args.strip_tags.split(',')

    if args.strip_inline_js:
        strip_inline_js = args.strip_inline_js.split(',')

    if args.strip_inline_css:
        strip_inline_css = args.strip_inline_css.split(',')

    if args.strip_inline_js_css:
        strip_inline_js_css = args.strip_inline_js_css.split(',')
        strip_inline_js.extend(strip_inline_js_css)
        strip_inline_css.extend(strip_inline_js_css)
        del strip_inline_js_css

    if args.outfile:
        outfile = open(args.outfile, 'wb')
        if not outfile:
            raise Exception('can not write output file "' + args.outfile + '"')

    del args

    ## run the bundler at the end ...
    bundled = Bundler(source,
                      path, root,
                      flags, compress_len, encoding,
                      strip_tags, strip_inline_js, strip_inline_css).bundle()

    ## and write to output
    if hasattr(outfile, 'buffer'):  # use buffer if available
        outfile = outfile.buffer
    outfile.write(bundled)
    outfile.close()
    del outfile

    del bundled
