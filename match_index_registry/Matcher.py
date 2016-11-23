from yaml import load
from os import path
from Registry_Talk import DockerDistributionRequester
from glob import glob


class Matcher:

    def __init__(self, indexd_location="./index.d", registry_url="registry.centos.org"):

        if not path.exists(indexd_location):
            raise Exception("Please specify a location of index.d")
        self._indexd_location = indexd_location
        self._registry_url = registry_url
        self._registry_query = DockerDistributionRequester(self._registry_url)
        self._image_list = self._registry_query.get_all_repos()
        self._containers_exist = {

        }

    def _load_yaml(self, yaml_file):

        if not path.exists(yaml_file):
            raise Exception("Specified yaml file does'nt exist")
        with open(yaml_file, "r") as the_file:
            yaml_data = load(the_file)
        return yaml_data

    def _mark_container_exists(self, container_name, exists):
        self._containers_exist[container_name] = exists

    def _check_registry_for_container(self, app_id, job_id, desired_tag):

        container_name = app_id + "/" + job_id
        container_full_name = container_name + ":" + desired_tag
        self._mark_container_exists(container_full_name, False)
        if container_name in self._image_list and desired_tag in self._registry_query.get_repo_tags(container_name):
            self._mark_container_exists(container_full_name, True)

    def run(self):

        files = glob(self._indexd_location + "/*.yml")

        for item in files:
            if "index_template" not in item:
                data = self._load_yaml(item)
                if "Projects" not in data:
                    continue
                entries = data["Projects"]
                for entry in entries:
                    self._check_registry_for_container(str(entry["app-id"]), str(entry["job-id"]),
                                                       str(entry["desired-tag"]))

        return self._containers_exist
