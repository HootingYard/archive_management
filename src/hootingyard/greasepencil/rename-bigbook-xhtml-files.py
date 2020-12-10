#!/usr/bin/env python3.7
""" Bulk rename bigbook XHTML files fron NNNNN_story_name.xhtml to YYYY-MM-DD-story-name.xhtml 
    This also renames internal links in the XHTML files.
"""

from pathlib import Path
import re

Text = Path('/home/glyn/Projects/HootingYard/keyml/books/bigbook/Text')

OLDNAME = re.compile(r'(\d\d\d\d\d)_(.+?\.xhtml)')

DATE = re.compile(r'\[(\d\d\d\d-\d\d-\d\d)\]')

newnames = {}

for path in list(Text.glob('*.xhtml')):
    m = OLDNAME.match(path.name)
    if m:
        postid = m.group(1)
        title = m.group(2)
        xhtml = path.read_text()
        m = DATE.search(xhtml)
        if m:
            date = m.group(1)
            newname = date + '-' + title.replace('_', '-')
            newnames[path.name] = newname
            path.rename(path.parent / newname)

for path in Text.glob('*.xhtml'):
    xhtml = path.read_text()
    def sub(m):
        oldname = m.group(0)
        newname = newnames.get(oldname, oldname)
        return newname
    xhtml = OLDNAME.sub(sub, xhtml)
    path.write_text(xhtml)
