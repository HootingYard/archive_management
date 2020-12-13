# -*- coding: utf-8 -*-

import re
from fixunicode import fix_bad_unicode
from typing import Text

QUOTE  = re.compile(ur'[‘’“”]')
ESCAPE = re.compile(ur'{[ocOC]}')

quote_map  = {u'‘': u'{o}', u'’': u'{c}', u'“': u'{O}', u'”': u'{C}'}
escape_map = {u'{o}': u'‘', u'{c}': u'’', u'{O}': u'“', u'{C}': u'”'}

def fix(text):  # type: (Text) -> Text
    text = QUOTE.sub(lambda m: quote_map[m.group()], text)
    text = fix_bad_unicode(text)
    return ESCAPE.sub(lambda m: escape_map[m.group()], text)

