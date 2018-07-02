import csv
import locale
from datetime import datetime as dt
locale.setlocale(locale.LC_ALL, '')


def makeSide(x):
    t = dt.strptime(x["time"], "%Y%m%d%w%H%M%S")
    s = f"""<li>
    <span class="no">[{x['id']}]</span>
    <a class="title" href="#{x['id']}">{x['title']}</a>
    <span class="author">{x['name']}</span>
    <time datetime="{t.isoformat()}">{t.strftime("%Y年%m月%d日 %H:%M")}</time>
    """
    if "children" in x:
        s += "<ul>"
        for c in x["children"]:
            s += makeSide(c)
        s += "</ul>"
    s += "</li>"
    return s


def writeBody(f, x, ind):
    f.write("<li><section>")
    t = dt.strptime(x["time"], "%Y%m%d%w%H%M%S")
    f.write('<h1 id="%s"><a href="#%s">%s</a><span class="title">%s</span><span class="author">%s</span><time datetime="%s">%s</time></h1>'
            % (x["id"], x["id"], x["id"], x["title"], x["name"], t.isoformat(), t.strftime("%Y年%m月%d日 %H:%M")))
    f.write('<div class="body">' + x["body"] + '</div>')
    f.write("</section><ul>")
    if "children" in x:
        for c in x["children"]:
            writeBody(f, c, ind+1)
    f.write("</ul></li>")


def writeheader(f, x):
    f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><title>" +
            x['title']+"</title><link rel='stylesheet' href='bbs.css' /><body><ul>")


def writefooter(f,):
    f.write('</ul></body></html>')


with open("data.tsv", mode="r", encoding="utf-8", newline="") as tsv:
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
            with open('result/' + x['id'] + '.html', "w", encoding="utf-8") as f:
                writeheader(f, x)
                f.write(makeSide(x))
                writeBody(f, x, 0)
                writefooter(f)
