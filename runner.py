import os
import sys
import glob
import subprocess

name = {
    "data": "general",
    "dev": "ansi",
    "unicode": "unicode",
    "help": "help",
    "macro": "macro",
    "web": "web"
}
title = {
    "data": "一般",
    "dev": "ANSI版開発",
    "unicode": "Unicode版開発",
    "help": "ドキュメント",
    "macro": "マクロ",
    "web": "Web"
}

if __name__ == '__main__':
    list = glob.glob(sys.argv[1] + '/*')
    me = os.path.dirname(os.path.abspath(sys.argv[0]))
    print(me)
    print(list)
    for d in list:
        subprocess.run(["python3", me + "/mktsv.py", d,
                        f"{d}/../../results/{name[os.path.basename(d)]}.tsv"])
        subprocess.run(["python3", me + "/mktree.py", f"{d}/../../results/{name[os.path.basename(d)]}.tsv",
                        f"{d}/../../results/{name[os.path.basename(d)]}/", title[os.path.basename(d)]])
