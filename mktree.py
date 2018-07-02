import csv
import locale
import sys
import os
from datetime import datetime as dt
locale.setlocale(locale.LC_ALL, '')


def usage():
    print("Usage: python3 mktree.py /path/to/tsvfile.tsv /path/to/resultdir/")
    exit()


def makeSide(x):
    t = dt.strptime(x["time"], "%Y%m%d%w%H%M%S")
    s = f"""<li><div class="list-title">
    <span class="no">{x['id']}</span>
    <a class="title" href="#{x['id']}">{x['title']}</a></div>
    """
    if "children" in x:
        s += "<ul>"
        for c in x["children"]:
            s += makeSide(c)
        s += "</ul>"
    s += "</li>"
    return s


def makeBody(x):
    t = dt.strptime(x["time"], "%Y%m%d%w%H%M%S")
    s = f"""<li id={x['id']}><section><h1>
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


def writeheader(f, x):
    f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><title>" +
            x['title']+"</title><link rel='stylesheet' href='bbs.css' /><body>")


def writefooter(f,):
    f.write('</body></html>')


if __name__ == '__main__':

    if len(sys.argv) < 3:
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

        # write html
        for x in ls:
            if "noroot" not in x:   # only root node
                print(x['id'])
                with open(result + "/" + x['id'] + '.html', "w", encoding="utf-8") as f:
                    writeheader(f, x)
                    f.write(f'<ul class="side">{makeSide(x)}</ul>')
                    f.write(f'<ul class="main">{makeBody(x)}</ul>')
                    writefooter(f)
