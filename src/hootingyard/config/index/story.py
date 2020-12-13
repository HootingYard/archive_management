from dataclasses import dataclass
import datetime


@dataclass
class Story:
    id: int
    title: str
    date: datetime.date
    text: str

    def validate(self):
        assert isinstance(self.id, str)
        assert len(self.id) > 0
        assert isinstance(self.title, str)
        assert len(self.title) > 0
        assert self.date > datetime.date(1995, 1, 1)
        assert len(self.text) > 0
