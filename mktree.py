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


def makeThreadHeader(x):
    return f"""<!DOCTYPE html>
<html lang="ja">

<head>
  <meta charset="utf-8">
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta http-equiv="Content-Style-Type" content="text/css">
  <script src='../bbs.js'></script>

  <!-- Global site tag (gtag.js) - Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=UA-120820034-1"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {{ dataLayer.push(arguments); }}
    gtag('js', new Date());
    gtag('config', 'UA-120820034-1');
  </script>

  <link href="../bbs.css" type="text/css" rel="stylesheet">
  <link rel="shortcut icon" href="favicon.ico">
  <title>{ x['title'] } | サクラエディタ過去ログ</title>
</head>
<body>
"""

def makeThreadSide(html, x):
    t = dt.strptime(x["time"], "%Y%m%d%w%H%M%S")
    s = f"""<li><div class="list-title">
    <span class="no">{x['id']}</span>
    <a class="thread-title" href="{html}#{x['id']}">{x['title']}</a></div>
    """
    if "children" in x:
        s += "<ul>"
        for c in x["children"]:
            s += makeThreadSide(html, c)
        s += "</ul>"
    s += "</li>"
    return s


def makeThreadBody(x):
    t = dt.strptime(x["time"], "%Y%m%d%w%H%M%S")
    body = re.sub("<!--.*?-->", "", x['body'])
    body = re.sub(
        "http://sakura-editor.sourceforge.net/cgi-bin/cyclamen/cyclamen.cgi\?log=(.*?)&tree=(?:r|c)(\d*?)",
        lambda m: f"../{m.group(1)}#{m.group(2)}", body)
    body = re.sub(
        "http://sakura-editor.sourceforge.net/cgi-bin/cyclamen/cyclamen.cgi\?log=(.*?)&amp;tree=(?:r|c)(\d*?)",
        lambda m: f"{m.group(1)}#{m.group(2)}", body)
    s = f"""<li><section><h1 id={x['id']}>
    <span class="no">[{x['id']}]</span>
    <a class="thread-title" href="#{x['id']}">{x['title']}</a>
    <span class="author">{x['name']}</span>
    <time datetime="{t.isoformat()}">{t.strftime("%Y年%m月%d日 %H:%M")}</time></h1>
    <div class="body">{body}</div></section>
    """
    if "children" in x:
        s += "<ul>"
        for c in x["children"]:
            s += makeThreadBody(c)
        s += "</ul>"
    s += "</li>"
    return s




def makeFooter():
    return '</body></html>'

# for index.html
def makeIndexHtmlTree(html, x):
    t = dt.strptime(x["time"], "%Y%m%d%w%H%M%S")
    s = f"""<li><div class="list-title">
    <span class="no">{x['id']}</span>
    <a class="thread-title" id="{x['id']}" href="{html}#{x['id']}">{x['title']}</a>
    <span class="author">{x['name']}</span>
    <time datetime="{t.isoformat()}">{t.strftime("%Y年%m月%d日 %H:%M")}</time>
    </div>
    """
    if "children" in x:
        s += "<ul>"
        for c in x["children"]:
            s += makeIndexHtmlTree(html, c)
        s += "</ul>"
    s += "</li>"
    return s

def makeIndexHtmlHeader(title):
    return f"""<!DOCTYPE html>
<html lang="ja">

<head>
  <meta charset="utf-8">
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <meta http-equiv="Content-Style-Type" content="text/css">

  <!-- Global site tag (gtag.js) - Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=UA-120820034-1"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag() {{ dataLayer.push(arguments); }}
    gtag('js', new Date());
    gtag('config', 'UA-120820034-1');
  </script>

  <link href="../../../dsk_sakura.css" type="text/css" rel="stylesheet">
  <link href="../index.css" type="text/css" rel="stylesheet">
  <link rel="shortcut icon" href="favicon.ico">
  <title>旧{ title }掲示板 過去ログ | サクラエディタ</title>
</head>
<body>
  <p>
    [<a href="/">▲HOME</a>]
    [<a href="/intro.html">機能紹介</a>]
    [<a href="/download.html">ダウンロード</a>]
    [<a href="https://github.com/sakura-editor/sakura/issues" target="_blank">GitHub Issues</a>]
    [<a href="https://osdn.net/projects/sakura-editor/forums/" target="_blank">OSDNフォーラム</a>]
  </p>
  <h1>サクラエディタ 旧{ title }掲示板過去ログ</h1>
"""

if __name__ == '__main__':

    if len(sys.argv) < 4:
        usage()
    result = sys.argv[2]

    if not os.path.exists(result):
        os.makedirs(result)


    # copy files
    # shutil.copy(os.path.dirname(__file__) + "/bbs.css", result)
    # shutil.copy(os.path.dirname(__file__) + "/bbs.js", result)
    # shutil.copy(os.path.dirname(__file__) + "/index.css", result)

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
            index.write(makeIndexHtmlHeader(sys.argv[3]))
            # write html
            for x in ls:
                if "noroot" in x:
                    continue # not root node

                print(x['id'])
                with open( f"{result}/{x['id']}.html", "w", encoding="utf-8") as f:
                    text = makeThreadHeader(x)
                    text += f'''<ul class="side">
        <a href="./" class="toindex">◀{sys.argv[3]}トップへ</a>
        { makeThreadSide(x["id"] + ".html", x) }
    </ul>'''
                    index.write(f'<ul>{makeIndexHtmlTree(x["id"] + ".html", x)}</ul>')
                    text += f'<ul class="main">{makeThreadBody(x)}</ul>'
                    text += makeFooter()

                    # p = subprocess.Popen(
                    #    ["prettier", "--parser=parse5"], stdin = subprocess.PIPE, stdout = f, shell = True)
                    # p.communicate(text.encode())
                    f.write(text)
