from yaml import load, dump
from os import path
import errors


def load_yaml(yaml_path):

    with open(yaml_path, "r") as yaml_file:
        return load(yaml_file)


def write_yaml(yaml_path, yaml_data):

    with open(yaml_path, "w") as yaml_file:
        dump(yaml_data, yaml_file)


class Validator(object):

    def __init__(self):
        self._errors = []
        self._warnings = []
        self._success = True


class IndexValidator(Validator):

    def __init__(self, index_file):
        Validator.__init__(self)
        self.
