import os
from configparser import ConfigParser, NoOptionError

from .exceptions import InvalidConfigPath, OptionNotFound
from ..logging import get_logger
from ..versioning import Version


logger = get_logger(False)

FILE_SECTION_PREFIX = "bumpv:file:"
PART_SECTION_PREFIX = "bumpv:part:"


DEFAULT = {
    "bumpv": {
        "current_version": "",
        "commit": False,
        "tag": False,
        "parse": r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)",
        "serialize": "{major}.{minor}.{patch}",
        "search": "{current_version}",
        "replace": "{new_version}",
        "tag_name": "v{new_version}",
        "message": "Bump version: {current_version} → {new_version}",
    }
}


class Configuration:
    def __init__(self, file_path=".bumpv.cfg", *args, **kwargs):
        config = ConfigParser()
        config.read_dict(DEFAULT)
        if os.path.exists(file_path):
            config.read(file_path)
        else:
            raise InvalidConfigPath(f"no file found at: {file_path}")

        self._config = config

        bumpv_section = self.get_section("bumpv")

        self.current_version = bumpv_section.get("current_version")
        self.commit = bumpv_section.getboolean("commit")
        self.tag = bumpv_section.getboolean("tag")
        self.tag_name = bumpv_section.get("tag_name")
        self.parse = bumpv_section.get("parse")
        self.serialize = bumpv_section.get("serialize").split("\n")
        self.search = bumpv_section.get("search")
        self.replace = bumpv_section.get("replace")
        self.message = bumpv_section.get("message")

    def get_section(self, key):
        return self._config[key]

    def get_raw_section_option(self, key, option):
        try:
            return self._config[key].get(option, "")
        except KeyError:
            raise OptionNotFound(f"option '{option}'' not found in section '{key}'")

    def get_section_names(self, key):
        for section in self._config.sections():
            if section == "bumpv":
                continue
            _, section, name = section.split(":")
            if section == key:
                yield name

    def files(self):
        return self.get_section_names("file")

    def get_file_section(self, file_path):
        return self.get_section(f"{FILE_SECTION_PREFIX}{file_path}")

    def parts(self):
        return self.get_section_names("part")

    def get_part_section(self, part):
        return self.get_section(f"{FILE_SECTION_PREFIX}{part}")
