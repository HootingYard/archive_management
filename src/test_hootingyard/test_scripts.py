import datetime
import os

from hootingyard.config.directories import get_big_book_scripts_dirctory
from hootingyard.index.story import Story
from hootingyard.script.generators import get_scripts
from hootingyard.script.script import (
    get_id_from_filename,
    Script,
    get_date_from_filename,
)


def test_get_id_from_filename0():
    filename = "2011-07-22-slap-bang-up-to-date-dabbling.xhtml"
    result: int = get_id_from_filename(filename)
    assert result == "2011-07-22-slap-bang-up-to-date-dabbling"


def test_get_date_from_filename0():
    filename = "2011-07-22-slap-bang-up-to-date-dabbling.xhtml"
    result: datetime.date = get_date_from_filename(filename)
    assert result == datetime.date(2011, 7, 22)


def test_get_story_from_script():
    file_path = os.path.join(
        get_big_book_scripts_dirctory(),
        "2011-07-22-slap-bang-up-to-date-dabbling.xhtml",
    )
    script = Script(file_path)
    story: Story = script.get_story()

    assert story.id == "2011-07-22-slap-bang-up-to-date-dabbling"
    assert story.title == "Slap Bang Up To Date Dabbling"
    assert story.date == datetime.date(2011, 7, 22)


def test_get_story_from_generator():
    first_script = next(get_scripts())
    first_story = first_script.get_story()

    assert first_story.title == "American Vicarage"
