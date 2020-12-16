import datetime
import functools
import os
import logging
from dataclasses import dataclass
from typing import Mapping, Union

from bs4 import BeautifulSoup

from hootingyard.index.story import Story, InvalidStory

log = logging.getLogger(__name__)


class NotAScript(RuntimeError):
    pass


def get_script_from_file_path(filename, root):
    if filename.endswith(".xhtml"):
        try:
            id = get_id_from_filename(filename)
            file_path = os.path.join(root, filename)
            yield Script(file_path)
        except NotAScript:
            pass


def get_id_from_filename(filename: str) -> str:
    (
        file_id,
        _,
    ) = filename.split(".", maxsplit=1)
    return file_id


def get_date_from_filename(filename: str) -> datetime.date:
    yyyymmdd = filename[:10]
    return datetime.date.fromisoformat(yyyymmdd)


@dataclass
class Script:
    path: str

    def __hash__(self):
        return hash(self.path)

    def get_stream(self):
        return open(self.path)

    def get_id(self) -> str:
        return get_id_from_filename(os.path.basename(self.path))

    @functools.lru_cache(1)
    def get_dom(self) -> BeautifulSoup:
        return BeautifulSoup(self.get_stream().read(), features="html.parser")

    def get_title(self) -> str:
        title = self.get_dom().title.string
        assert isinstance(title, str)
        return str(title)

    def get_paragraphs(self):
        def is_postwebpage(ptag) -> bool:
            return "postwebpage" in ptag.attrs.get("class", [])

        paragraphs = [p for p in self.get_dom().find_all("p") if not is_postwebpage(p)]

        return paragraphs

    def get_text(self) -> str:
        return "\n".join(p.get_text() for p in self.get_paragraphs())

    def get_metadata(self) -> Mapping[str, Union[str, str]]:
        m = {}
        for meta in self.get_dom().find_all("meta"):
            try:
                m[meta.attrs["name"]] = meta.attrs["content"]
            except KeyError:
                continue

        return m

    def get_date(self) -> datetime.date:
        return get_date_from_filename(os.path.basename(self.path))

    def get_story(self) -> Story:
        story = Story(
            id=self.get_id(),
            title=self.get_title(),
            text=self.get_text(),
            date=self.get_date(),
        )
        try:
            story.validate()
        except InvalidStory:
            log.exception(f"Cannot generate story for {self.path}.")
            raise
        return story
