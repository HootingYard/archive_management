from pathlib import Path
import re

new_head = """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title></title>
  <meta name="author" content="Frank Key" />
  <meta name="description" content="Stories from Frank Key's first website." />
  <meta name="language" content="en-GB" />
  <meta name="generator" content="Scrawled in GreasePencil" />
  <meta name="date" content="2020-12-07T18:03:07" />
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <link href="../Styles/style.css" rel="stylesheet" type="text/css" />
</head>"""

head = re.compile(r"^.*<title>(.+?)</title>.*</head>", re.DOTALL)

dir = Path(
    "/home/glyn/Projects/HootingYard/keyml/books/books-in-keyml/old-book-of-key/Text"
)

for file in dir.glob("*.html"):
    print(file)
    text = file.read_text()

    def sub(match):
        title = match.group(1)
        return new_head.replace("<title></title>", f"<title>{title}</title>")

    newtext = head.sub(sub, text)
    newpath = Path(str(file).replace(".html", ".xhtml"))
    newpath.write_text(newtext)
