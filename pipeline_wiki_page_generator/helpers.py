from yaml import load
from os import path
import re
from urlparse import urlparse, urlunparse
import subprocess
import urllib2
from config import config
import json


def load_yaml(yaml_path):
    if not path.exists(yaml_path):
        raise Exception("The yaml file does not exist at " + yaml_path)
    with open(yaml_path, "r") as yaml_file:
        return load(yaml_file)


def run_cmd(cmd, check_call=True):
    if not check_call:
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        if process.returncode > 0:
            raise Exception("Failed to execute command")
    else:
        subprocess.check_call(cmd)


def _request_url(url):

    try:
        req = urllib2.urlopen(url)
    except Exception as ex:
        req = None

    return req


def check_image_exists(container_name):
    exists = False
    rdata = None
    name_actual, tag = container_name.split(":")
    req_url = "https://" + config["registry"] + "/v2/" + name_actual + "/tags/list"
    rdata = _request_url(req_url)
    if rdata:
        data = json.load(rdata)
        if "tags" in data and tag in data["tags"]:
            exists = True
    return exists


class WikiCentosOrg(object):

    @staticmethod
    def _form_title(title):
        if title:
            return "\n" + ("=" * 3) + title + ("=" * 3) + "\n"
        else:
            raise Exception("Please provide title")

    @staticmethod
    def _form_section_indicator(section, end=False):
        if not section:
            raise Exception("Please provide a section")
        if end:
            pre = "##end-"
        else:
            pre = "##begin-"
        return "\n" + pre + section + "\n"

    @staticmethod
    def _form_table_row(items):
        if not isinstance(items, list) or len(items) <= 0:
            raise Exception("Please provide list of items to append.")
        row_data = "||"
        for item in items:
            row_data += str(item) + "||"
        return "\n" + row_data + "\n"

    @staticmethod
    def _form_link(data, url):
        if data and url:
            link_data = (
                "[{0} {1}]"
            ).format(url, data)
            return link_data
        else:
            raise Exception("Please provide the data and url")

    @staticmethod
    def _normalize_url(url):
        parsed = list(urlparse(url))
        parsed[2] = re.sub("/{2,}", "/", parsed[2])
        return urlunparse(parsed)

    def __init__(self, dump_file_path):
        self._dump_file_path = dump_file_path
        with open(self._dump_file_path, "w"):
            pass

    def _write_dump_file(self, data):
        with open(self._dump_file_path, "a+") as dump_file:
            dump_file.write(data)

    def add_title(self, title):
        self._write_dump_file(self._form_title(title))

    def add_section_indicator(self, section, end=False):
        self._write_dump_file(self._form_section_indicator(section, end))

    def add_table_header(self):
        items = [
            "Sl no",
            "Source",
            "Container URL"
        ]
        self._write_dump_file(self._form_table_row(items))

    def add_table_row(self, sl_no, source, container_url, container_name):
        source = self._normalize_url(source)
        source = self._form_link(container_name, source)
        items = [
            sl_no,
            source,
            container_url
        ]
        self._write_dump_file(self._form_table_row(items))
