import json
from dataclasses import dataclass


@dataclass
class Config:
    host: str
    port: int
    items_list_formattable_string: str
    items_separator: str

    @classmethod
    def new(cls):
        return cls(**json.load(open("config.json", encoding="utf-8")))
