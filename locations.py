import json
import os
import string
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Set

from config import Config

location_template = string.Template(
    open("location_template.html", encoding="utf-8").read()
)

flag_name_to_item_name = json.load(
    open("flag_name_to_item_name.json", encoding="utf-8")
)

config = Config.new()


@dataclass
class Button:
    text: str
    location_name: str


def _get_item_names(flags: Set[str]):
    for flag in flags:
        try:
            yield flag_name_to_item_name[flag]
        except KeyError:
            pass


def make_location_link(location_name: str, flags: Set[str]):
    url_flags = ("?" + "|".join(flags)) if flags else ""
    link = f"/locations/{location_name}{url_flags}"
    return link


@dataclass
class Location:
    image_filename: str
    upper_text: Optional[str] = None
    lower_text: Optional[str] = None
    flag_to_location_name: Tuple[Tuple[str, str], ...] = ()
    flags_to_add: Tuple[str] = ()
    flags_to_remove: Tuple[str] = ()
    buttons: Tuple[Button] = ()

    def make_html(self, flags: Set[str]):
        item_names = config.items_separator.join(_get_item_names(flags))
        page = location_template.substitute({
            "image_filename": self.image_filename,
            "upper_text": (
                f'<p><b class="upper_text">{self.upper_text}</b></p>'
                if self.upper_text else ''
            ),
            "lower_text": (
                f'<p>{self.lower_text}</p>'
                if self.lower_text else ''
            ),
            "buttons": "".join(
                f'<form action='
                f'"{make_location_link(button.location_name, flags)}"'
                f'><input type="hidden" value="brandcode" />'
                f'<button class="button">{button.text}</button>'
                f'</form>'
                for button in self.buttons
            ),
            "item_names": (
                '<p>'
                + config.items_list_formattable_string.format(item_names)
                + '</p>'
            ) if item_names else ""
        })
        return page


def as_stripped_pairs(iterable):
    iterator = iter(iterable)
    try:
        while True:
            yield next(iterator).strip(), next(iterator).strip()
    except StopIteration:
        return


def make_locations_dict(
        directory_with_locations_name="locations"
) -> Dict[str, Location]:
    """
    Location file format:
    image = example.jpg
    upper_text = blabla
    lower_text = blabla
    flag_to_location_name = those|are_pairs | of_flags|and_location_names
    flags_to_add = flag1 | flag2 | etc
    flags_to_remove = flag3 | flag4 | etc
    buttons = button_text|location_name | button_text|location_name
    """
    locations = {}
    for filename in os.listdir(directory_with_locations_name):
        file_contents = open(
            os.path.join(directory_with_locations_name, filename),
            encoding="utf-8"
        ).read()
        fields = {
            field_name.strip(): field_value.strip().replace("\\n", "\n")
            for field_name, field_value in (
                line.split("=", maxsplit=1)
                for line in file_contents.splitlines()
            )
        }
        fields["image_filename"] = fields.pop("image")
        try:
            fields["flag_to_location_name"] = tuple(as_stripped_pairs(
                fields["flag_to_location_name"].split("|")
            ))
        except KeyError:
            pass
        for field_name in ("flags_to_add", "flags_to_remove"):
            try:
                fields[field_name] = tuple(
                    flag.strip() for flag in fields[field_name].split("|")
                )
            except KeyError:
                pass
        try:
            fields["buttons"] = tuple(
                Button(button_text, location_name_)
                for button_text, location_name_ in as_stripped_pairs(
                    fields["buttons"].split("|")
                )
            )
        except KeyError:
            pass
        location_name = os.path.splitext(filename)[0]
        locations[location_name] = Location(**fields)
    return locations
