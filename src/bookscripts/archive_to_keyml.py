#!/usr/bin/env python3
""" Transforms the 2003-2006 Archive into KeyML format and places in the Big Book of Key.
    This code does 99.5% of the necessary formatting, but some editing will still be required.

    This script is awful, but should only have to be run once. If you want to re-do a file
    in the big book, delete *only* that file and re-runt this script.

    NOTES:
        * The LaTeX book version of 'Unspeakable Desolation Pouring Down From the Stars'
          will have a more up-to-date and edited version of the text.
        * The Quote List (quotelist.htm) really should have links back to the actual
          quotes, but I'm tired, just so tired.
"""

import datetime
import re
from collections.abc import Iterator
from datetime import datetime
from html import escape
from itertools import chain
from mimetypes import guess_type
from pathlib import Path
from shutil import copyfile
from typing import Literal, NamedTuple

from lxml.html import HtmlElement, fromstring, parse, tostring  # pip3 install lxml
from lxml.html.builder import CLASS, H1, H2, A, P
from unidecode import unidecode  # pip3 install Unidecode

from src.hootingyard.utils import pants, update_bigbook_toc

ADD_NEW_RESOURCE_FILES = True
OVERWRITE_EXISTING_PAGES = False  # DON'T set this if you have edited the pages

Archive = Path("/home/glyn/Projects/HootingYard/keyml/archive-2003-2006")
ArchiveURL = "http://hootingyard.org/archive/"
UnhelpfulIndex = Archive / "unhelpfulindex.htm"

OldBook = Path(
    "/home/glyn/Projects/HootingYard/keyml/books/books-in-keyml/old-book-of-key"
)
BigBook = Path("/home/glyn/Projects/HootingYard/keyml/books/bigbook")
Text = BigBook / "Text"
Images = BigBook / "Images"
Media = BigBook / "Media"


class PostData(NamedTuple):
    date: datetime.date
    kind: Literal["post", "quote", "preamble", "miscellaneous"]
    title: str
    name: str  # Soup Committee identifier
    href: str  # local URL within the archive


def text_surgery(s: str) -> str:
    """Replace punctuation that looks bad in print form."""
    s = s.replace(" - ", "—")  # Replace dashes that look horrible in print
    s = s.replace(" – ", "—")
    s = s.replace(" :", FrankColon)  # If it's worth doing, it's worth doing right :-|
    s = NonApostrophe.sub(
        r"'\1", s
    )  # Replace single-quotes inside words with true apostrophes
    s = DateDash.sub(r"\1–\2", s)  # en dashes inside date ranges
    return s


FrankColon = chr(0xA0) + ":"  # non-breaking space, colon
NonApostrophe = re.compile(r"’([A-Za-z])")
DateDash = re.compile(r"([0-9])-([0-9])")


def extract_iso_date(text: str) -> datetime.date:
    match = re.search(r"\d\d\d\d-\d\d-\d\d", text)
    if match:
        return datetime.strptime(match.group(), "%Y-%m-%d")
    else:
        raise ValueError(f"No YYYY-MM-DD date found: {text}")


def soup_committee_id(date: datetime, title: str) -> str:
    """Create a canonical identifier for one of Frank Key's works.
        An ISO date followed by the title, in lowercase with accents
        and punctuation removed, with all words separated by dashes.
        Example: "2004-03-19-what-is-hooting-yard".
    :param date: date of first publication
    :param title: title of work
    :return: the identifier
    """
    s = unidecode(title)  # remove accents
    s = re.sub(r"\b'\b", "", s)  # remove apostrophes
    s = s.lower().replace("&", "and")  # keep  the "&" sign
    s = re.sub(r"\W+", " ", s)  # remove punctuation, shrink whitespace
    s = s.strip().replace(" ", "-")  # replace spaces with "-"
    return date.strftime("%Y-%m-%d") + "-" + s  # prepend ISO date


def strip(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def elements(html: HtmlElement, xpath: str) -> Iterator[HtmlElement]:
    for result in html.xpath(xpath):
        assert isinstance(result, HtmlElement)
        yield result


def element(html: HtmlElement, xpath: str) -> HtmlElement:
    results = html.xpath(xpath)
    if len(results) == 1:
        assert isinstance(results[0], HtmlElement)
        return results[0]
    else:
        raise ValueError(f"XPath {repr(xpath)}: {len(results)} results")


def html_to_string(html: HtmlElement) -> str:
    return tostring(html, pretty_print=True, encoding="unicode", method="xml")


def relative_to(link: str, base: str) -> str:
    # XXX not smart about full URLs, but that's not important here
    if link.startswith("#"):
        if "#" in base:
            base = base[0 : base.index("#")]
        return base + link
    else:
        return link


def upto(limit: str, text: str) -> str:
    """return all the text up to the limit string"""
    return text[0 : text.find(limit)]


def xhtml(div: HtmlElement, data: PostData) -> str:
    title = escape(data.title)
    date = data.date.strftime("%Y-%m-%d")
    url = ArchiveURL + data.href
    div.tag = "body"
    div.append(
        fromstring(f'<p class="postwebpage"><a href="{url}">[{date}]</a></p>\n\n')
    )
    body = html_to_string(div)
    if data.kind == "miscellaneous":
        body = pants.process(body)
    return f"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>{title}</title>
        <meta name="author" content="Frank Key" />
        <meta name="description" content="Indiscriminately collected works of Frank Key." />
        <meta name="language" content="en-GB" />
        <meta name="generator" content="Scrawled in GreasePencil" />
        <meta name="date" content="{date}" />
        <meta http-equiv="content-type" content="text/html;charset=utf-8" />
        <link href="../Styles/style.css" rel="stylesheet" type="text/css" />
    </head>
    {body}
</html>
"""


MiscellaneousIndex: dict[str, PostData] = {
    "terms.htm": PostData(
        datetime(2003, 1, 1),
        "miscellaneous",
        "Terms & Conditions",
        "2003-01-01-terms-and-condtions",
        "terms.htm",
    ),
    "quotelist.htm": PostData(
        datetime(2006, 12, 31),
        "miscellaneous",
        "Quote List",
        "2006-12-31-quote-list",
        "quotelist.htm",
    ),
    "starsfront.htm": PostData(
        date=datetime(2004, 6, 21, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Contents",
        name="2004-06-21-unspeakable-desolation-pouring-down-from-the-stars-contents",
        href="starsfront.htm",
    ),
    "stars01.htm": PostData(
        date=datetime(2004, 6, 21, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter One",
        name="2004-06-21-unspeakable-desolation-pouring-down-from-the-stars-chapter-one",
        href="stars01.htm",
    ),
    "stars02.htm": PostData(
        date=datetime(2004, 6, 28, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Two",
        name="2004-06-28-unspeakable-desolation-pouring-down-from-the-stars-chapter-two",
        href="stars02.htm",
    ),
    "stars03.htm": PostData(
        date=datetime(2004, 7, 6, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Three",
        name="2004-07-06-unspeakable-desolation-pouring-down-from-the-stars-chapter-three",
        href="stars03.htm",
    ),
    "stars04.htm": PostData(
        date=datetime(2004, 7, 12, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Four",
        name="2004-07-12-unspeakable-desolation-pouring-down-from-the-stars-chapter-four",
        href="stars04.htm",
    ),
    "stars05.htm": PostData(
        date=datetime(2004, 7, 19, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Five",
        name="2004-07-19-unspeakable-desolation-pouring-down-from-the-stars-chapter-five",
        href="stars05.htm",
    ),
    "stars06.htm": PostData(
        date=datetime(2004, 7, 26, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Six",
        name="2004-07-26-unspeakable-desolation-pouring-down-from-the-stars-chapter-six",
        href="stars06.htm",
    ),
    "stars07.htm": PostData(
        date=datetime(2004, 8, 2, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Seven",
        name="2004-08-02-unspeakable-desolation-pouring-down-from-the-stars-chapter-seven",
        href="stars07.htm",
    ),
    "stars08.htm": PostData(
        date=datetime(2004, 8, 9, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Eight",
        name="2004-08-09-unspeakable-desolation-pouring-down-from-the-stars-chapter-eight",
        href="stars08.htm",
    ),
    "stars09.htm": PostData(
        date=datetime(2004, 8, 16, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Nine",
        name="2004-08-16-unspeakable-desolation-pouring-down-from-the-stars-chapter-nine",
        href="stars09.htm",
    ),
    "stars10.htm": PostData(
        date=datetime(2004, 8, 23, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Ten",
        name="2004-08-23-unspeakable-desolation-pouring-down-from-the-stars-chapter-ten",
        href="stars10.htm",
    ),
    "stars11.htm": PostData(
        date=datetime(2004, 8, 31, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Eleven",
        name="2004-08-31-unspeakable-desolation-pouring-down-from-the-stars-chapter-eleven",
        href="stars11.htm",
    ),
    "stars12.htm": PostData(
        date=datetime(2004, 9, 6, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Twelve",
        name="2004-09-06-unspeakable-desolation-pouring-down-from-the-stars-chapter-twelve",
        href="stars12.htm",
    ),
    "stars13.htm": PostData(
        date=datetime(2004, 9, 13, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Thirteen",
        name="2004-09-13-unspeakable-desolation-pouring-down-from-the-stars-chapter-thirteen",
        href="stars12.htm",
    ),
    "starsafterword.htm": PostData(
        date=datetime(2004, 9, 20, 0, 0),
        kind="miscellaneous",
        title="Unspeakable Desolation Pouring Down From the Stars, Chapter Afterword",
        name="2004-09-20-unspeakable-desolation-pouring-down-from-the-stars-afterword",
        href="starsafterword.htm",
    ),
}

# These will be indexed with the date that they first appear in the Archive
MiscellaneousFiles = {
    "aerostat.htm": "By Aerostat to Hooting Yard",
    "agree.htm": "The Dobson Übertoolbar User's Agreement",
    "albatross.htm": "The Albatross",
    "aviary.htm": "Mister Scrimgeour's Aviary",
    "belshazzar.htm": "Belshazzar",
    "birds.htm": "A Catalogue of 53 Birds",
    "bogenbroom.htm": "Lines Written Upon First Listening to Doctor Bogenbroom by Jethro Tull",
    "broth.htm": "The Phial of Broth",
    "build.htm": "Build Your Own House of Turps",
    "dobson.htm": "The Glue In The Palace Was Rarefied; The Putty Was Dreadful",
    # 'donation.htm': 'How to Donate Money to Hooting Yard',
    "duckpond.htm": "The Immense Duckpond Pamphlet",
    # 'friends.htm': 'Become a Friend of Hooting Yard',
    "gigantic.htm": "Gigantic Bolivian Architectural Diagrams",
    "gruel.htm": "A Recipe for Gruel",
    "hudibras.htm": "Hudibras",
    "jars.htm": "Advice On Jars",
    "joost.htm": "Joost Van Dongelbracke",
    "lighthouses.htm": "The Dobson Memorial Lecture 2004",
    "mayfly.htm": "A Mayfly Nymph Drawn by Jan Swammerdam",
    "obsequies.htm": "An extract from Obsequies For Lars Talc, Struck By Lightning",
    "peason.htm": "Peason",
    "pills.htm": "A Brief Note About Pills",
    "ponds.htm": "The Names of the Ponds",
    "preen.htm": "The Novels of Lothar Preen",
    "stationery.htm": "International Society of Stationery Fanatics",
    "titles.htm": "Titles",
    "transcript.htm": "Transcript of a Dictaphone Recording",
    "what.htm": "What is Hooting Yard?",
}


def unhelpful_index() -> dict[str, PostData]:
    index: dict[str, PostData] = {}
    html: HtmlElement = parse(str(UnhelpfulIndex)).getroot()
    for a in elements(html, ".//div[@class='index']//a"):
        title = str(a.text_content())
        href = a.get("href")
        date = extract_iso_date(href)
        kind = a.get("class")
        name = soup_committee_id(date, title)
        post = PostData(date, kind, title, name, href)
        index[post.href] = post
    return index


def preamble_index() -> dict[str, PostData]:
    index: dict[str, PostData] = {}
    for path in Archive.glob("???[0-9][0-9].htm"):
        href = path.name
        date = datetime.strptime(href, "%b%y.htm")
        title = date.strftime("Hooting Yard Archive, %B %Y")
        name = soup_committee_id(date, title)
        post = PostData(date, "preamble", title, name, href)
        index[post.href] = post
    return index


def miscellaneous_index() -> dict[str, PostData]:
    index: dict[str, PostData] = MiscellaneousIndex
    seen: set[str] = set()
    for html, first_posting in chain(posts(), quotes(), preambles()):
        for a in elements(html, ".//a"):
            href = a.get("href")
            if href not in index and href in MiscellaneousFiles:
                seen.add(href)
                title = MiscellaneousFiles[href]
                href = a.get("href")
                name = soup_committee_id(first_posting.date, title)
                post = PostData(first_posting.date, "miscellaneous", title, name, href)
                index[post.href] = post
    return index


# ---------------------------------------------------------------------------------------------


def months() -> Iterator[tuple[Path, HtmlElement]]:
    for path in Archive.glob("???[0-9][0-9].htm"):
        html: HtmlElement = parse(str(path)).getroot()
        yield path, html


def posts() -> Iterator[tuple[HtmlElement, PostData]]:
    for path, html in months():
        for post in elements(html, ".//div[@class='post']"):
            a = element(post, ".//a[@name]")
            href = path.name + a.get("href")
            yield post, Index[href]


def quotes() -> Iterator[tuple[HtmlElement, PostData]]:
    for path, html in months():
        for day in elements(html, './/div[@class="day"]'):
            a = element(day, "h1/a")
            href = path.name + a.get("href")
            for quote in elements(day, './/div[@class="quote"]'):  # (0 or 1 of these)
                yield quote, Index[href]


def preambles() -> Iterator[tuple[HtmlElement, PostData]]:
    for path, html in months():
        header = element(html, './/div[@class="header"]')
        yield header, Index[path.name]


def miscellany() -> Iterator[tuple[HtmlElement, PostData]]:
    for file in chain(MiscellaneousFiles, MiscellaneousIndex):
        path = Archive / file
        html: HtmlElement = parse(str(path)).getroot()
        body = element(html, "body")
        body.attrib.clear()
        body.tag = "div"
        yield body, Index[file]


Resources: set[str] = set()


def copy_resource(date: datetime, file: str, source: Path, destination: Path) -> str:
    new_name = f"{date.strftime('%Y-%m')}-{file}"
    new_href = f"../{destination.name}/{new_name}"
    new_path = destination / new_name
    old_path = source / file
    if ADD_NEW_RESOURCE_FILES:
        destination.mkdir(parents=True, exist_ok=True)
        copyfile(src=old_path, dst=new_path)
    else:
        pass
        # print(f"{file} -> {new_path}")
    return new_href


Index = unhelpful_index() | preamble_index()
Index |= miscellaneous_index()


def redirect_links(div: HtmlElement, data: PostData) -> None:
    for a in elements(div, ".//a"):
        href = str(a.attrib["href"])
        a.attrib.clear()
        if ":" in href:  # has a protocol, so is an external link
            a.attrib["class"] = "external"
            a.attrib["href"] = href
        else:
            a.attrib["class"] = "internal"
            href = relative_to(href, data.href)
            if href in Index:  # links to an Archive page
                a.attrib["href"] = Index[href].name + ".xhtml"  # use the new name
            elif href == "unhelpfulindex.htm":  # this is no longer used
                a.drop_tag()
            else:  # links to some special treat
                kind = file_kind(href)
                a.attrib["class"] = "internal-" + kind
                if kind == "image":
                    a.attrib["href"] = copy_resource(
                        data.date, href, Archive, BigBook / "Images"
                    )
                else:
                    a.attrib["href"] = copy_resource(
                        data.date, href, Archive, BigBook / "Media"
                    )


def file_kind(file: str) -> str:
    if file.endswith("pdf"):
        return "pdf"
    else:
        mime = guess_type(file)[0]
        return "media" if (not mime) else upto("/", mime)


def tidy_img_tags(div: HtmlElement, data: PostData) -> None:
    for img in elements(div, ".//img"):
        src = img.attrib["src"]
        alt = img.get("alt", "")
        height = int(img.attrib["height"])
        img.attrib.clear()
        assert ":" not in src  # is local
        new_src = copy_resource(data.date, src, Archive, BigBook / "Images")
        img.attrib["src"] = new_src
        if not alt:
            img.attrib["alt"] = f"{data.title}: {upto('.', src).title()}"
        if height > 400:
            img.attrib["class"] = "size-large"
        elif height < 100:
            img.attrib["class"] = "small"
        else:
            img.attrib["class"] = "size-medium"


def replace(e: HtmlElement, replacement: HtmlElement) -> None:
    parent = e.getparent()
    parent.replace(e, replacement)


def make_into_heading(e: HtmlElement, level: str = "h1") -> None:
    title = str(e.text_content()).title()
    h1 = fromstring(f"<{level}></{level}>")
    h1.text = title
    replace(e, h1)


def clean_misc_text(div: HtmlElement) -> None:
    for p in elements(div, ".//p"):
        if re.match(r"^\s*$", p.text_content()):
            p.drop_tree()
    for e in elements(div, './/b[font[size="+2"]]'):
        make_into_heading(e)
    for e in elements(div, './/font[size="+2" and b]'):
        make_into_heading(e)
    for e in elements(div, './/font[size="+3"]'):
        make_into_heading(e)
    for e in elements(div, './/font[size="+4"]'):
        make_into_heading(e)
    for e in elements(div, ".//font"):
        e.drop_tag()
    for e in elements(div, ".//*[@align]"):
        del e.attrib["align"]


def clean_stars(div: HtmlElement) -> None:
    for e in elements(div, "p[strong[em]]"):
        e.drop_tree()
    for e in elements(div, ".//hr"):
        e.drop_tree()

    div.insert(0, H1("Unspeakable Desolation Pouring Down From the Stars"))
    e = element(div, "./p[1]")
    h2 = H2(e.text_content().title())
    replace(e, h2)

    e = element(div, "./p[strong[a]]")
    a = element(div, "./p/strong/a")
    p = P(
        CLASS("breakabove"),
        A(e.text_content(), CLASS("internal"), href=a.attrib["href"]),
    )
    replace(e, p)


def edit_illustration_divs(div: HtmlElement) -> None:
    for illustration in elements(div, './/div[@class="illustration"]'):
        images = element(illustration, 'div[@class="images"]')
        p = element(images, "p")
        p.attrib["class"] = "imagerow"
        images.drop_tag()
        for caption in elements(illustration, 'div[@class="caption"]'):
            for p in elements(caption, "p"):
                p.attrib["class"] = "caption"
            caption.drop_tag()


def tidy_text(div: HtmlElement) -> None:
    for i in elements(div, ".//i"):
        i.tag = "em"
    for b in elements(div, ".//b"):
        b.tag = "strong"

    # no paragraph indent is blank space above
    for p in elements(div, "./p[1]"):
        p.attrib["class"] = "noindent"
    for p in elements(div, ".//blockquote/p[1]"):
        p.attrib["class"] = "noindent"
    for p in elements(div, ".//p[preceding-sibling::div]"):
        p.attrib["class"] = "noindent"

    for e in elements(div, ".//*"):
        if e.text:
            e.text = text_surgery(e.text)
        if e.tail:
            e.tail = text_surgery(e.tail)

    for br in elements(div, ".//br"):
        br.attrib.clear()


def clean(div: HtmlElement, data: PostData) -> None:
    tidy_text(div)
    tidy_img_tags(div, data)
    redirect_links(div, data)
    edit_illustration_divs(div)


def write(div: HtmlElement, data: PostData, force: bool = False) -> None:
    path = BigBook / "Text" / (data.name + ".xhtml")
    if force or OVERWRITE_EXISTING_PAGES or not path.exists():
        path.write_text(xhtml(div, data))


def main():
    for div, data in posts():
        h2 = element(div, "h2")
        a = element(h2, "a")
        a.drop_tag()
        h2.tag = "h1"
        clean(div, data)
        write(div, data)

    for div, data in quotes():
        clean(div, data)

        div.insert(0, H1("Quote of the Day"))
        write(div, data)

    for div, data in preambles():
        div.attrib.clear()
        div.attrib["class"] = "monthly-preamble"
        element(div, "./a").drop_tree()
        clean(div, data)
        write(div, data)

    for div, data in miscellany():
        edited_version = OldBook / "Text" / (data.href.removesuffix(".htm") + ".xhtml")
        if edited_version.exists():
            html: HtmlElement = parse(str(edited_version)).getroot()
            div = element(html, "body")
            div.tag = "div"
            for img in elements(div, ".//img"):
                file = Path(img.attrib["src"]).name
                img.attrib["src"] = copy_resource(
                    data.date, file, OldBook / "Images", BigBook / "Images"
                )
        else:
            clean_misc_text(div)
            clean(div, data)
            if (
                "unspeakable-desolation-pouring-down-from-the-stars-chapter"
                in data.name
            ):
                clean_stars(div)
        write(div, data)

    update_bigbook_toc.run(BigBook / "Text")


if __name__ == "__main__":
    main()
