#!/usr/bin/env python

import sys
import os
import re
import subprocess

import bs4
import html5lib   # used by BeautifulSoup


def build(path_to_file):

    ###### config #######

    tag_stripOnBuild = '@striponbuild'

    yuic = "yuicompressor-2.4.8.jar"

    #####################

    def src_is_external(source):
        return source.find('://') > -1

    def preserveHTMLentities(string):
        return re.sub(r"&([a-zA-Z0-9#]+?);", r"~pe{\1}~", string)

    def depreserveHTMLentities(string):
        return re.sub(r"~pe\{([a-zA-Z0-9#]+?)\}~", r"&\1;", string)

    def strip_on_build(string):
        string = re.sub(r".*@striponbuild.*", "", string, flags=re.IGNORECASE)
        return string

    def yui_compress(kind, string, encoding="utf-8"):
        process = subprocess.Popen(["java", "-jar", yuic, "--line-break", "0", "--type", kind, "--charset", encoding],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=os.path.dirname(os.path.realpath(__file__)))

        stdout, stderr = process.communicate(string.encode())
        process.terminate()

        success = stderr == b""
        return success, (stdout if success else stderr).decode(sys.stdout.encoding)


    if not path_to_file and not os.path.isfile(path_to_file):
        sys.stderr.write("no such file")
        sys.exit(1)

    path_to_directory = os.path.dirname(path_to_file)

    doc = bs4.BeautifulSoup(preserveHTMLentities(open(path_to_file, 'r').read()), "html5lib")

    for strip in doc.find_all(tag_stripOnBuild):
        strip.extract()

    for comment in doc.find_all(text=lambda text: isinstance(text, bs4.Comment)):
        comment.extract()

    for script in doc.find_all('script'):
        if script.has_attr('src'):
            src = script['src']
            if src_is_external(src):
                continue

            src_path = os.path.join(path_to_directory, src)
            if not os.path.isfile(src_path):
                # script.extract()
                continue

            del script['src']
            script_file_rh = open(src_path, "r")
            script_content = script_file_rh.read()
            script_file_rh.close()
        else:
            script_content = script.string

        compressed, compress_output = yui_compress("js", strip_on_build(script_content))
        if not compressed:
            sys.stderr.write("error on yuiCompression:\n" + compress_output)
            sys.exit(2)

        script.string = "\n" + compress_output + "\n"

    for link in doc.find_all('link', {'rel': 'stylesheet', 'href': True}):
        src = link['href']
        if src and not src_is_external(src):
            src_path = os.path.join(path_to_directory, src)
            if not os.path.isfile(src_path):
                continue  # link.extract()

            style_file_rh = open(src_path, "r")
            style_content = style_file_rh.read()
            style_file_rh.close()

            compressed, compress_output = yui_compress("css", strip_on_build(style_content))
            if not compressed:
                sys.stderr.write("error on yuiCompression:\n" + compress_output)
                sys.exit(3)

            style_inline = doc.new_tag("style", type="text/css")
            style_inline.string = "\n" + compress_output + "\n"
            link.replace_with(style_inline)

    for style in doc.find_all('style'):
        style_content = style.string

        compressed, compress_output = yui_compress("css", strip_on_build(style_content))
        if not compressed:
            sys.stderr.write("error on yuiCompression:\n" + compress_output)
            sys.exit(4)

        style.string = "\n" + compress_output + "\n"

    doc_string_part_clean = ""
    doc_string_parts_clean = []
    for doc_string_part_raw in doc.prettify().split("\n"):
        doc_string_part_raw = re.sub(r"[ \t\n\r]+", " ", doc_string_part_raw).strip()
        doc_string_part_raw = depreserveHTMLentities(doc_string_part_raw)
        if len(doc_string_part_clean) + len(doc_string_part_raw) > 120:
            doc_string_parts_clean.append(doc_string_part_clean)
            doc_string_part_clean = doc_string_part_raw
        else:
            doc_string_part_clean += doc_string_part_raw
    doc_string_parts_clean.append(doc_string_part_clean)

    print("\n".join(str(part) for part in doc_string_parts_clean))




if __name__ == '__main__':
    file = sys.argv[1]
    build(file)