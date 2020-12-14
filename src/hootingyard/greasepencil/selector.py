""" This extracts pages from the Big Book into the source directory for an anthology """
# -*- coding: utf-8 -*-

# XXX NOT UP-TO-DATE

import codecs
import os
import shutil
from os.path import join

from jinja2 import Environment, FileSystemLoader
from lxml import etree

from grease import identifierize
import grease

Bigbook = 'bigbook'
Anthology = 'brute2'

Contents = ur"""
On Potatoes
On Naming Your Child After Your Favourite Reservoir
On The Falsely Negative Portrayal Of U-Boat Sailors
On Gulls' Eggs
On Skippy The Bush Kangaroo
On Feral Goblins
On Tin Foil
On Control Of The Fiscal Levers
On Babinsky's Idiot Half-Brother
On True Grit
On Barking Up The Wrong Tree
On Government-Controlled Origami
On The Devil In The Detail
On Speed
On Truculent Peasantry
On The Love Song Of Ah-Fang Van Der Houygendorp
On Scree
On The Collapse Of Civilisations
On Groovy Bongos
On Replacement Bus Services
On "The Scottish Play"
On Groaning Minions
On Having The Prize Within One's Grasp
On Nitwits
On The Lambing-Hall Boogie
On The One-Eyed Crossing-Sweeper Of Sawdust Bridge
On Sand Robots
On Birds
On My Own Zona
On The Wellspring Of Debauchery
On Jelly
On Marshy Punting
On A Darkling Plain
On Silent Monkey
On Counting Corks
On The Screaming Abdabs
On The Air
On A Spook's Briefcase
On Etiquette
On And On And On
On Dreams Of Pointy Town
On Mods And Rockers And Widows And Orphans
On The Plains Of Gath
On Pickles And Pluck And Gumption
On Fate
On Reggae For Swans
On A Couple Of Art Exhibitions
On Soviet Hen Coops
On Certain Ants
On Captain Nitty
On The Bad Vicarage
On Sudden Darting Movements In The Insect World
On The Pecking Order
On My Transformation
On Bringing The Good News From Ghent To Aix
On The Naming Of Nuts
On Razzle Dazzle, And Its Avoidance
On The Balletomane Nan Kew
On King Jasper's Castle, Its Electrical Wiring System Its Janitor, And Its Chatelaine
On King Jasper's Bones
On Eggheads
On Fools
On The Brink
On The Livers Of Polar Bears
On Horst Gack
On Failing To Persuade Maud To Come Into The Garden
On What Maud Did Next
On Maud, Again
On The Kitchen Devil
On The Inner Life
On The Report Of Dr Slop
On Wings Of Song
On The Sea, For Those In Peril
On Radical Puppetry
On Ancient Egypt
On The Vilification Of A Totnes Undertaker's Mute
On Flocks Of Birds
On Cocking A Snook
On Hiking Pickles
On Wod & Pym, The Choc Ice Men
On The Picnic Fly
On The Clopping Of Hooves
On Poptones
On Sailing Ships
On Brains
On The Correct Placement Of The Apostrophe In The Title Of Reader's Digest Magazine
On The Underpants Bomber, The U-Boat, And Ted And Sylvia
On Aphinar
On Limping Bellringers
On Life Without Ducks
On Duff
On Tarleton And The Mysterious Affair Of The Buff Envelope
On Tarleton And Pelf
On Natty Dread
On Lothar Preen
On A Plague Of Boils
On The Daily Strangling Of Serpents
On Bohemia
On The Nougat Nozzles Of Neptune
On The Suet Siphons Of Saturn
On The Vinegar Valves Of Venus
On A Stonechat
On A Knock-Knee'd Ingrate
On Knowing Your Shovellers
On Huz And Buz
On Beggar's Farm
On The Antipipsqueak
On The World-Famous Food-Splattered Jesuit
On The Rare Golden Enigmatic Tatterdemalion Corncrake
On A Prang
On Scroonhoonpooge Marshes
"""


def copyfile(src, dst):
    if not os.path.exists(dst):
        shutil.copyfile(src, dst)


def text_only(element):
    """returns just the text in an element, without any tags"""
    s = element.text or u''
    for e in element:
        s += text_only(e) + (e.tail or '')
    return s


def escape(text):
    return text.replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;').replace('"', '&quot;')


def enclosed_xhtml_markup(element):
    """Returns all the contents of element in the form of a text string containing HTML tags"""
    s = escape(element.text)
    for e in element:
        s += etree.tounicode(e)
    return s


def lines(text):
    for line in text.splitlines():
        line = line.strip()
        if line:
            yield line


def main():
    bigbook_index = {}
    toc = etree.parse(codecs.open(join(Bigbook, 'Text', "toc.xhtml"), "r", "utf-8"), etree.HTMLParser())
    for a in toc.xpath("//*[@class='contents']//a"):
        bigbook_index[identifierize(text_only(a))] = a.get('href')

    bookinfo = grease.get_bookinfo(join(Anthology, 'bookinfo.json'))

    bookinfo['index'] = []

    templates = Environment(loader=FileSystemLoader('templates'), autoescape=True)

    page = templates.get_template('chapter.xhtml')
    toc = templates.get_template('toc.xhtml')
    index = templates.get_template('index.html')

    for title in lines(Contents):
        key = identifierize(title)
        if key not in bigbook_index:
            print '*** Not found: ', title, '***'
            continue

        href = bigbook_index[key]
        post = etree.parse(codecs.open(join(Bigbook, 'Text', href), "r", "utf-8"), etree.HTMLParser())
        body = post.xpath('//body[1]')[0]
        p = body.xpath("//p[@class='postwebpage'][1]")[0]
        body.remove(p)

        title = text_only(post.xpath('//h1[1]')[0])
        heading = enclosed_xhtml_markup(post.xpath('//h1[1]')[0])

        chapter = dict(heading=heading, title=title, href=href)

        bookinfo['index'].append(chapter)

        with codecs.open(join(Anthology, 'Text', href), 'w', 'utf-8') as f:
            f.write(page.render(dict(chapter=chapter, book=bookinfo, body=enclosed_xhtml_markup(body))))

        for img in post.xpath('//img'):
            src = os.path.basename(img.get('src'))
            copyfile(join(Bigbook, 'Images', src), join(Anthology, 'Images', src))

    with codecs.open(join(Anthology, 'Text', 'toc.xhtml'), "w", "utf-8") as f:
        f.write(toc.render(dict(book=bookinfo)))

    with codecs.open(join(Anthology, 'index.xhtml'), "w", "utf-8") as f:
        f.write(index.render(dict(book=bookinfo)))


if __name__ == '__main__':
    main()
