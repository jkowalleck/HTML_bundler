#!/usr/bin/env python

if __name__ == '__main__':

    from bundler import Bundler

    import os
    import argparse
    import fileinput
    import chardet


    arg_parser = argparse.ArgumentParser(description="bundle a HTML file with multiple external (js|css) files " +
                                                     "to one big HTML file ")

    arg_parser.add_argument('-i', '--input-file', metavar='<file>', type=str,
                            help='a file path - if none given, listen on stdin',
                            dest="infile")

    arg_parser.add_argument('-p', '--path-dir', metavar='<dir>', type=str,
                           # help='',
                            dest="path")

    arg_parser.add_argument('-r', '--htroot-dir', metavar='<dir>', type=str,
                            # help='',
                            dest="htroot")

    arg_parser.add_argument('-o', '--output-file', metavar='<file>', type=str,
                            help='a file path - if none given, output is sent to stdout',
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
                            help='forces --strip-comments-html AND --strip-comments-javascript AND --strip-comments-css',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS)
    arg_parser.add_argument('--strip-comments-keep-first',
                            help='forces --strip-comments-js-keep-first AND --strip-comments-css-keep-first',
                            dest="flags", action="append_const", const=Bundler.FLAG_STRIP_COMMENTS_KEEP_FIRST)

    arg_parser.add_argument('--strip-tags', metavar='<tag1[,tag2[,..]]>', type=str,
                            help='comma separated list of HTML tags to strip from the document',
                            dest="strip_tags")

    arg_parser.add_argument('--strip-markers-js', metavar='<marker1[,marker2[,..]]>', type=str,
                            help='comma separated list of markers. ' +
                                 'entire marked lines will ge stripped of any JavaScript',
                            dest="strip_inline_js")


    arg_parser.add_argument('--strip-markers-css', metavar='<marker1[,marker2[,..]]>', type=str,
                            help='comma separated list of markers. ' +
                                 'entire marked lines will ge stripped of any CSS style definition',
                            dest="strip_inline_css")

    arg_parser.add_argument('--strip-markers', metavar='<marker1[,marker2[,..]]>', type=str,
                            help='comma separated list of markers. ' +
                                 'entire marked lines will ge stripped of any JavaScript or CSS style definition',
                            dest="strip_inline_js_css")


    arg_parser.add_argument('--compress',
                            help='compress the output',
                            dest="flags", action="append_const", const=Bundler.FLAG_COMPRESS)


    #defaults and consts
    source = ""
    path = ""
    htroot = ""
    flags = 0
    compress_len = 120
    encoding = "utf-8"
    strip_tags = []
    strip_inline_js = []
    strip_inline_css = []

    args = arg_parser.parse_args()

    if args.infile:
        fh = open(args.infile)
        if not fh:
            raise Exception('can not read input file "' + args.infile + '"')
        source = fh.read()
        fh.close()
        source = str(source)
    else:
        source_lines = []
        for input_line in fileinput.input():
            source_lines.append(input_line)
        source = "\n".join(source_lines)
        del source_lines

    if args.path:
        path = args.path
    elif args.infile:
        path = os.path.abspath(os.path.dirname(args.infile))

    if args.htroot:
        htroot = args.htroot
    elif args.path:
        htroot = path

    if args.flags:
        flags = 0
        for flag in args.flags:
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

    ## run the bundler at the end ...
    del arg_parser

    bundled = Bundler(source,
                      path, htroot,
                      flags, compress_len, encoding,
                      strip_tags, strip_inline_js, strip_inline_css).bundle()

    if args.outfile:
        open(args.outfile, 'w').write(bundled)
    else:
        print(bundled)
