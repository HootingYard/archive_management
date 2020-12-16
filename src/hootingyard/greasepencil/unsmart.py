# -*- coding: utf-8 -*-

import re
from typing import Text
from ftfy import fix_text


QUOTE = re.compile(ur'[‘’“”]')
ESCAPE = re.compile(ur'{[ocOC]}')

quote_map = {u'‘': u'{o}', u'’': u'{c}', u'“': u'{O}', u'”': u'{C}'}
escape_map = {u'{o}': u'‘', u'{c}': u'’', u'{O}': u'“', u'{C}': u'”'}


def fix(text):  # type: (Text) -> Text
    text = QUOTE.sub(lambda m: quote_map[m.group()], text)
    text = fix_text(text, uncurl_quotes=False)
    return ESCAPE.sub(lambda m: escape_map[m.group()], text)
