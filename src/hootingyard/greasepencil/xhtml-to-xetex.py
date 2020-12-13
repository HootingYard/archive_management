# xhtml-to-xetex.py  -- Converts pages in a subset of XHTML to Latex with UTF-8 characters.
# -*- coding: utf-8 -*-

import codecs, os, sys, re
from os.path import join

from lxml import etree
from lxml.html import HtmlElement, parse
from jinja2 import Environment, FileSystemLoader
from typing import Text
from copy_images_for_latex import latex_image_path
import grease

#--------------------------------------------------------------------------------

BOOK  = sys.argv[1]  # The book's GreasePencil data directory
CODE  = sys.argv[2]  # The GreasePencil code and template directory
LATEX = sys.argv[3]  # Directory to write Latex files to


ILLUSTRATION_WIDTH = 0.5  #(of width of page)

# XXX This could be more sophisticated: wide illustrations could be
# allowed more width and tall illustrations could be limited to a
# certain fraction of the page height.


#-----------------------------------------------------------------------------------
# These functions walk down an ElementTree of XHTML text, building a string of LaTeX
# Only a subset of XHTML is handled.


def blocks (surrounding_element):  # type: (HtmlElement) -> Text
    ''' HTML block-level text, i.e. headings, paragraphs, lists, illustrations, etc. '''
    s = ''
    for element in surrounding_element.iterchildren("*"):
        s += block(element)
    return s


def block (element):  # type: (HtmlElement) -> Text
    s = ''
    tag = element.tag
    #print tag
    cla = element.get('class') or ''
    if tag == 'p':
        if 'postwebpage' in cla:
            pass
        elif 'center' in cla:
            s += '\\begin{center}\n' + inline(element) + '\n\\end{center}\n\n'
        elif 'textbreak' in cla:
            s += '\n\\textbreak{}\n\n'  #this macro must be supplied
        elif 'breakabove' in cla:
            s += BLANK_LINE + '\\noindent ' + inline(element) + '\n\n'
        elif 'linebreaks' in cla:
            s += BLANK_LINE + '\\noindent ' + inline(element) + BLANK_LINE
        elif 'verse' in cla:
            s += '\\begin{verse}\n' + inline(element) + '\n\\end{verse}\n\n'
        else:
            s += ('\\noindent ' if 'noindent' in cla else '') + inline(element) + '\n\n'
    elif tag == 'div':
        if 'illustration' in cla:
            s += illustration(element)
        elif 'blockparagraphs' in cla:
            s += BLANK_LINE
            for e in element.iterchildren("*"):
                s += '\\noindent ' + block(e) + BLANK_LINE
        elif 'verse' in cla:
            s += '\\begin{verse}\n' + blocks(element) + '\n\\end{verse}\n\n'
        elif 'newpage' in cla:
            s += '\n\n\\null\\newpage\\null\n\n'
        else:
            s += blocks(element)  #ignore
    elif tag == 'blockquote':
        s += '\\begin{quotation}\n' + blocks(element) + '\\end{quotation}\n\n'
    elif tag == 'ol':
        s += '\\begin{enumerate}\n' + ordered_list_items(element) + '\\end{enumerate}\n\n'
    elif tag == 'ul':
        s += '\\begin{itemize}\n' + ordered_list_items(element) + '\\end{itemize}\n\n'
    elif tag == 'dl':
        s += r'\begin{description}'
        if 'tight' in cla:
            s += r'\tightlist'
        elif 'firm' in cla:
            s += r'\firmlist'
        s += '\n'
        s += definition_list_items(element)
        s += '\\end{description}\n\n'
    elif tag == 'h1':
        s += heading(element)
    elif tag == 'h2':
        s += '\\section*{' + inline(element) + '}\n\n'
    else:
        print >> sys.stderr, etree.tounicode(element)
        raise ValueError("this XHTML block tag is not handled:", tag)
    return s

BLANK_LINE = '\n\n' + r'\addvspace{0.75\baselineskip}' + '\n\n'



def heading (element):  # type: (HtmlElement) -> Text
    ''' Returns a chapter heading. The "squeezeN" and "padN" classes allow a few lines
        to be added or removed above the heading to tweak the pagination.
        That is done by altering the \chapterheadstart macro, see page 82 of the Memoir
        Class manual. '''
    cla = element.get('class') or ''
    center = 'center' in cla
    padding = 0
    
    star = '*' if 'sigilNotInTOC' in cla else ''
    
    m = PAD.search(cla)
    if m: padding = int(m.group(1))
    m = SQUEEZE.match(cla)
    if m: padding = -int(m.group(1))
    
    s = ''
    if center: s += '\\renewcommand{\\printchaptertitle}[1]{\\begin{center}\\normalfont\\operafontfamily\\huge{#1}\\end{center}}\n'
    if center: s += '\\setlength\\afterchapskip{-0.5em}\n'
    if padding: s += '\\renewcommand{\\chapterheadstart}{\\vspace*{\\beforechapskip}\\vspace*{%i\\onelineskip}}\n' % padding
#    s += '\\chapter%s{%s}\n' % (star, inline(element))
    s += '\\chapter%s{%s}\n' % (star, inline(element).replace(u'—', u'---'))  # no — in Opera Lyrics Smooth font
    if padding: s += '\\renewcommand{\\chapterheadstart}{\\vspace*{\\beforechapskip}}\n'  # restore to default
    if center: s += '\\renewcommand{\\printchaptertitle}[1]{\\normalfont\\operafontfamily\\huge\\MakeUppercase{#1}}'  # restore to default
    return s

PAD     = re.compile(r'pad([0-9]+)')
SQUEEZE = re.compile(r'squeeze([0-9]+)')



def inline (surrounding_element, footnotes=True):  # type: (HtmlElement, bool) -> Text
    ''' HTML text inlines, i.e. characters within paragraphs etc.
        Links are represented by footnotes showing the URL.
    '''
    s = text(surrounding_element.text)
    for element in surrounding_element.iterchildren("*"):
        tag = element.tag
        if tag == 'br':    s += r'\\{}'
        elif tag == 'em':    s += '\\emph{'   + inline(element, footnotes) + '}'
        elif tag == 'tt':    s += '\\texttt{' + inline(element, footnotes) + '}'
        elif tag == 'small': s += '{\\small ' + inline(element, footnotes) + '}'
        elif tag == 'sup':   s += '\\textsuperscript{' + inline(element, footnotes) + '}'
        elif tag == 'del':   s += '\\sout{'   + inline(element, footnotes) + '}'  #from LaTeX package 'ulem'
        elif tag == 'a':      s += link(element, footnotes)
        elif tag == 'strong': s += '\\textbf{' + inline(element, footnotes) + '}'
        elif tag == 'small':  s += '{\\small ' + inline(element, footnotes) + '}'
        else:
            print >> sys.stderr, etree.tounicode(surrounding_element)
            raise ValueError("this XHTML inline tag is not handled:", tag)
        s += text(element.tail)
    return s


def text (s):  # type: (Text) -> Text
    ''' Escape Unicode text for Xetex/Latex, if necessary. '''
    # Use non-breaking spaces to prevent "I", "A" or "An" at the end of lines, which looks weird
    if s is None:
        return u''
    else:
        s = re.sub(r'([\\&%$#_{}~^])', ur'\\\1', s)
        s = re.sub(r'\b(I|A|An)\s', r'\1' + NBSP, s)
        s = re.sub(r' : ', '~: ' + NBSP, s)
        return s.replace(NBSP, u'~')

NBSP = unichr(0xA0)


def link (a, footnotes=False):  # type: (HtmlElement, bool) -> Text
    ''' A link is represented by a page reference or URL in the footnotes '''
    href = a.get('href')
    cla = a.get('class')
    title = text(a.get('title'))
    s = inline(a, footnotes)

    if href == "http://www.hootingyard.org":
        pass # don't footnote the Hooting Yard URL
        
    elif cla == "internal" or ('http://' not in href):
        if title:
            title = r'\emph{%s,} ' % title
        s += r'\footnote{%spage~\pageref{%s}}' % (title, href[:href.index('.')])

    elif cla == "hootingyard":
        if title and "Hooting Yard" in title:
            title = r'\emph{%s,} ' % title
        elif title:
            title = r'\emph{Hooting Yard~: %s,} ' % title
        else:
            title = r'\emph{Hooting Yard,} '
        s += r'\footnote{%s%s}' % (title, URL(href))
        
    else:
        if cla != "external":
            print >> sys.stderr, 'no class for link to %s' % s
        if title:
            title = r'\emph{%s,} ' % title
        s += r'\footnote{%s%s}' % (title, URL(href))

    return s


def URL(href):  # type: (Text) -> Text
    return ur'\url{%s}' % re.sub(r'([\\%${}^])', ur'\\\1', href)


def ordered_list_items (surrounding_element):  # type: (HtmlElement) -> Text
    s = ''
    for li in surrounding_element.iterchildren("*"):
        assert li.tag == 'li'
        s += r'\item ' + inline(li) + '\n'
    return s


def definition_list_items (surrounding_element):  # type: (HtmlElement) -> Text
    s = ''
    for e in surrounding_element.iterchildren("*"):
        if e.tag == 'dt':
            s += r'\item[%s] ' % inline(e)
        elif e.tag == 'dd':
            s += inline(e) + '\n'
        else:
            print >> sys.stderr, etree.tounicode(e)
            raise ValueError("does not belong a <dl> list:", e.tag)
    return s


def illustration (div):  # type: (HtmlElement) -> Text
    ''' One or more illustrations and their caption in a figure environment.
    '''
    assert len(div) == 1 or len(div) == 2

    cla = div.get('class') or ''
    if 'small' in cla:
        width = ILLUSTRATION_WIDTH / 2
    elif 'fullwidth' in cla:
        width = 1.0
    else:
        width = ILLUSTRATION_WIDTH

    if 'here' in cla:
        s = '\\begin{figure}[H]\n\\centering\n'
    else:
        s = '\\begin{figure}[h]\n\\centering\n'

    assert div[0].get('class') == 'imagerow'
    if len(div[0]) > 1:
        width = width / len(div[0])
    for img in div[0]:
        assert img.tag == 'img'
        src = latex_image_path(os.path.basename(img.get('src')))
        s += '\\includegraphics[width=%0.2f\\textwidth]{%s}\n' % (width, src)
       
    if len(div) == 2:
        assert div[1].get('class') == 'caption'
        s += '\\caption*{' + inline(div[1], footnotes=False) + '}\n'
       
    s += '\\end{figure}\n'
    return s


#--------------------------------------------------------------------------------


# TeX-friendly macros:
JingaEnv  = Environment( loader = FileSystemLoader(join(CODE, 'templates', 'latex')),
                         block_start_string    = '<%',
                         block_end_string      = '%>',
                         variable_start_string = '<<',
                         variable_end_string   = '>>',
                         comment_start_string  = '<#',
                         comment_end_string    = '#>',
                         autoescape = False )

def expand_template (template, outpath, bookinfo):
    template = JingaEnv.get_template(template)
    with codecs.open(outpath, "w", "utf-8") as f:
        f.write(template.render(bookinfo))


def translate (xhtmlfile, texfile):  # type: (str, str) -> None
    page = parse(xhtmlfile).getroot()  # type: HtmlElement
    body = page.xpath('body')[0]  # type: HtmlElement
    with codecs.open(texfile, "w", "utf-8") as tex:
        tex.write(blocks(body))


def main():
    bookinfo = grease.get_bookinfo((join(BOOK, 'bookinfo.json')))

    bookinfo['texfiles'] = []   # Tex files that will be \included into 'book.tex'

    # Convert all the XHTML files referenced in the book's table of contents into tex files:
    toc = etree.parse(join(BOOK, 'Text', "toc.xhtml"), etree.HTMLParser())
    for a in toc.xpath("//a"):
        name = grease.filenamepart(a.get('href'))
        translate(join(BOOK, 'Text', name + '.xhtml'), join(LATEX, name + '.tex'))
        bookinfo['texfiles'].append(name)

    # Use the book data's copyright page, if it has one, else make a boilerplate one:
    copyright = join(BOOK, 'Text', 'copyright.xhtml')
    if os.path.exists(copyright):
        translate(copyright, join(LATEX, 'copyright.tex'))
    else:
        expand_template('copyright.tex', join(LATEX, 'copyright.tex'), bookinfo)

    # ...and this is the main latex file:
    expand_template('book.tex', join(LATEX, 'book.tex'), bookinfo)
   
main()
