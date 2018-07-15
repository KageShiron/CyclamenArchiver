import csv
import locale
import sys
import os
import glob
import subprocess
from datetime import datetime as dt
locale.setlocale(locale.LC_ALL, '')


def usage():
    print("Usage: python3 mktree.py /path/to/tsvfile.tsv /path/to/resultdir/ bbsname")
    exit()


def makeSide(html, x):
    t = dt.strptime(x["time"], "%Y%m%d%w%H%M%S")
    s = f"""<li><div class="list-title">
    <span class="no">{x['id']}</span>
    <a class="title" href="{html}#{x['id']}">{x['title']}</a></div>
    """
    if "children" in x:
        s += "<ul>"
        for c in x["children"]:
            s += makeSide(html, c)
        s += "</ul>"
    s += "</li>"
    return s


def makeBody(x):
    t = dt.strptime(x["time"], "%Y%m%d%w%H%M%S")
    s = f"""<li><section><h1 id={x['id']}>
    <span class="no">[{x['id']}]</span>
    <a class="title" href="#{x['id']}">{x['title']}</a>
    <span class="author">{x['name']}</span>
    <time datetime="{t.isoformat()}">{t.strftime("%Y年%m月%d日 %H:%M")}</time></h1>
    <div class="body">{x['body']}</div></section>
    """
    if "children" in x:
        s += "<ul>"
        for c in x["children"]:
            s += makeBody(c)
        s += "</ul>"
    s += "</li>"
    return s


def writeheader(x):
    return "<!DOCTYPE html><html><head><meta charset='utf-8'><title>" + x['title']+"</title><link rel='stylesheet' href='bbs.css' /><script src='bbs.js'></script><body>"


def writefooter():
    return '</body></html>'


if __name__ == '__main__':

    if len(sys.argv) < 4:
        usage()
    result = sys.argv[2]

    if not os.path.exists(result):
        os.makedirs(result)

    with open(sys.argv[1], mode="r", encoding="utf-8", newline="") as tsv:
        # TSV reader

        ls = list(csv.DictReader(tsv, delimiter="\t"))

        # create tree structure
        for x in ls:
            for y in ls:
                if y["parent"] == x["id"]:
                    if "children" in x:
                        x["children"] += [y]
                    else:
                        x["children"] = [y]  # new list
                    y["noroot"] = True

        with open(result + "/index.html", "w", encoding="utf-8") as index:
            # write html
            for x in ls:
                if "noroot" not in x:   # only root node
                    print(x['id'])
                    with open(result + "/" + x['id'] + '.html', "w", encoding="utf-8") as f:
                        text = ""
                        text += writeheader(x)
                        side = makeSide(x["id"] + ".html", x)
                        text += f'<ul class="side"><a href="./" class="toindex">←{sys.argv[3]}トップへ</a>{side}</ul>'
                        index.write(f'<ul>{side}</ul>')
                        text += f'<ul class="main">{makeBody(x)}</ul>'
                        text += writefooter()

                        # p = subprocess.Popen(
                        #    ["prettier", "--parser=parse5"], stdin = subprocess.PIPE, stdout = f, shell = True)
                        # p.communicate(text.encode())
                        f.write(text)
