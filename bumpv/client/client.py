import json

import yaml

from .config import Configuration
from .files import FileUpdater
from .logging import (
    get_logger,
    get_logger_list,
)
from .vcs import get_vcs
from .versioning import Version


logger = get_logger(False)
logger_list = get_logger_list()


class BumpClient:
    def __init__(self, config: Configuration = None, verbose=0, show_list=False, allow_dirty=False):
        if config is None:
            config = Configuration()

        self.logger = get_logger(show_list, verbose)
        self.logger_list = get_logger_list()
        self.config = config
        self.vcs = get_vcs(allow_dirty)
        self.current_version = Version.from_config(config)
        self.new_version = None

    def bump(self, part, dry_run=False):
        self.new_version = self.current_version.bump(part)
        updater = FileUpdater(self.config, self.current_version, self.new_version)
        updater.replace(dry_run)

        if self.config.commit:
            for path in self.config.files():
                self.vcs.add_path(path)
            message = self.config.message.format(
                current_version=self.current_version.serialize(),
                new_version=self.new_version.serialize(),
            )
            self.logger.debug(f"COMMITTING w/ message: {message}")
            self.vcs.commit(message)
        if self.config.tag:
            self.logger.debug(f"GIT TAG: {self.new_version.get_tag()}")
            self.vcs.tag(self.new_version.get_tag())

        self.config.set_value("bumpv", "current_version", self.new_version.serialize())
        self.config.write()

        return self.new_version

    def rollback(self):
        pass

    def dict(self):
        return {
            "old_version": self.current_version.serialize(),
            "new_version": self.new_version.serialize(),
            "tag": self.new_version.get_tag(),
        }

    def json(self):
        return json.dumps(self.dict())

    def yaml(self):
        return yaml.dump(self.dict())
