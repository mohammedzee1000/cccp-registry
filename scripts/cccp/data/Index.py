#!/bin/python

import yaml
from IndexEntry import IndexEntry


class Index:

    def __init__(self, indexyml):

        self._file = indexyml
        self._entries = dict()

        self._buildFromYaml()

        return

    def _buildFromYaml(self):

        with open(self._file, "r") as ymlfile:
            ymldata = yaml.load(ymlfile)

        return

    @property
    def entries(self):
        return self._entries
