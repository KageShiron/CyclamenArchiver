import csv
import locale
import sys
import os
import glob
import re
import subprocess
import shutil
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
    body = re.sub("<!--.*?-->", "", x['body'])
    body = re.sub(
        "http://sakura-editor.sourceforge.net/cgi-bin/cyclamen/cyclamen.cgi\?log=(.*?)&tree=(?:r|c)(\d*?)", "../\\1/#\\2", body)
    body = re.sub(
        "http://sakura-editor.sourceforge.net/cgi-bin/cyclamen/cyclamen.cgi\?log=(.*?)&amp;tree=(?:r|c)(\d*?)", "\\1/#\\2", body)
    s = f"""<li><section><h1 id={x['id']}>
    <span class="no">[{x['id']}]</span>
    <a class="title" href="#{x['id']}">{x['title']}</a>
    <span class="author">{x['name']}</span>
    <time datetime="{t.isoformat()}">{t.strftime("%Y年%m月%d日 %H:%M")}</time></h1>
    <div class="body">{body}</div></section>
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

# for index.html
def makeIndex(html, x):
    t = dt.strptime(x["time"], "%Y%m%d%w%H%M%S")
    s = f"""<li><div class="list-title">
    <span class="no">{x['id']}</span>
    <a class="title" id="{x['id']}" href="{html}#{x['id']}">{x['title']}</a></div>
    """
    if "children" in x:
        s += "<ul>"
        for c in x["children"]:
            s += makeSide(html, c)
        s += "</ul>"
    s += "</li>"
    return s


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
        shutil.copy(os.path.dirname(__file__) + "/bbs.css", result)
        shutil.copy(os.path.dirname(__file__) + "/bbs.js", result)
        shutil.copy(os.path.dirname(__file__) + "/index.css", result)
        with open(result + "/index.html", "w", encoding="utf-8") as index:
            index.write(f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>サクラエディタ 旧" + sys.argv[3]+"掲示板</title><link rel='stylesheet' href='index.css' /><body><h1>サクラエディタ 旧" + sys.argv[3]+"掲示板過去ログ</h1>")
            # write html
            for x in ls:
                if "noroot" not in x:   # only root node
                    print(x['id'])
                    with open(result + "/" + x['id'] + '.html', "w", encoding="utf-8") as f:
                        text = ""
                        text += writeheader(x)
                        side = makeSide(x["id"] + ".html", x)
                        text += f'<ul class="side"><a href="./" class="toindex">←{sys.argv[3]}トップへ</a>{side}</ul>'
                        index.write(f'<ul>{makeIndex(x["id"] + ".html", x)}</ul>')
                        text += f'<ul class="main">{makeBody(x)}</ul>'
                        text += writefooter()

                        # p = subprocess.Popen(
                        #    ["prettier", "--parser=parse5"], stdin = subprocess.PIPE, stdout = f, shell = True)
                        # p.communicate(text.encode())
                        f.write(text)
