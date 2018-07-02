import glob
import os
import re
import sys


def usage():
    print("Usage: python3 mktsv.py /path/to/cyclamendir /path/to/output")
    exit()


if __name__ == '__main__':

    if len(sys.argv) < 3:
        usage()
    target = sys.argv[1]

    # output file
    f = open(sys.argv[2], "w", encoding="utf-8")

    list = glob.glob(sys.argv[1] + '/**/*.log', recursive=True)
    # sort key == filename == message id
    list.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))

    # header
    f.write("id\ttime\tunique\tname\ttitle\tbody\temail\turl\thost\tagent\tunknown1\tunknown2\tunknown3\tparent\n")

    for x in list:
        print(x)
        with open(x, "rb") as log:
            # "→\
            log = log.read().replace(b"\"", b"\t")
            # unescape
            log = log.replace(b"&#59;", b";").replace(
                b"&#95;", b"_").replace(b"&quot;", b"\"")
            # remove \0
            log = log.replace(b"\0", b"")
            # decode as cp932 ( NOT shift-jis in python )
            log = log.decode("cp932", "replace")
            # remove row number
            log = re.sub(r'\t\[\d*\](\d*)\t', "\t\\1\t", log)

            f.write(os.path.splitext(os.path.basename(x))
                    [0] + "\t" + log + "\n")
    f.close()
