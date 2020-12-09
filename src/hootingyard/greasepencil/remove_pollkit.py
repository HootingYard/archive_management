""" Delete Pollkit.com poll boilerplate from the Big Book XHTL files. """

from glob import glob
from re import compile, DOTALL, MULTILINE
import codecs

pollkit = compile(r'<p.*?><!--FREEPOLLKIT.+?CODE END--></p>', DOTALL | MULTILINE)

for path in glob('/home/glyn/Projects/hootingyard/books/bigbook/Text/[0-9]*.xhtml'):
    with codecs.open(path, mode='r', encoding='utf-8') as fp:
        text = fp.read()
    new_text = pollkit.sub(u'<blockquote><p class="center"><em>[An online poll was here. It is now closed.]</em></p></blockquote>', text)
    if new_text != text:
        print path
        with codecs.open(path, mode='w', encoding='utf-8') as fp:
            fp.write(new_text)

