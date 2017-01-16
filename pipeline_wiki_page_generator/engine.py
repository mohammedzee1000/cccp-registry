from config import config
from helpers import run_cmd, WikiCentosOrg, load_yaml, check_image_exists
from os import path
from shutil import rmtree
from glob import glob
import re


class IndexReader(object):

    def __init__(self):
        self._index_git = config["index_git"]
        self._clone_path = path.abspath(config["index_git_clone"])
        self._index_location = self._clone_path + "/" + "index.d"
        self._wiki_centos_org = WikiCentosOrg(config["dump_location"])
        self._projects_data = {}
        self._clone_repo()

    def _clone_repo(self):
        cmd = ["git", "clone", self._index_git, self._clone_path]
        if path.exists(self._clone_path):
            rmtree(self._clone_path)
        run_cmd(cmd)

    def _get_wiki_info(self, entry):
        matched = False
        section = None
        title = None
        target_file_url = (
            "{git_url}/tree/{git_branch}/{git_path}/{target_file}"
        ).format(git_url=entry["git-url"], git_branch=entry["git-branch"], git_path=entry["git-path"],
                 target_file=entry["target-file"])
        container_name = (
            "{app_id}/{job_id}:{desired_tag}"
        ).format(app_id=entry["app-id"], job_id=entry["job-id"], desired_tag=str(entry["desired-tag"]))

        # Attempt to match
        for section_name, section_info in config["section_mappings"].items():
            for pattern in section_info["pattern"]:
                if re.match(pattern, container_name):
                    matched = True
                    title = section_info["title"]
                    section = section_name
                    break
            if matched:
                break

        if not matched:
            section = entry["app-id"]
            title = entry["app-id"]

        return title, section, container_name, target_file_url

    def _generate_wiki_content(self):
        for section, section_data in self._projects_data.items():
            self._wiki_centos_org.add_title(section_data["title"])
            self._wiki_centos_org.add_section_indicator(section)
            self._wiki_centos_org.add_table_header()
            sl_no = 0
            for item in section_data["items"]:
                sl_no += 1
                name = item["name"]
                url = item["url"]
                registry_url = config["registry"] + name
                if check_image_exists(name):
                    self._wiki_centos_org.add_table_row(sl_no, url, registry_url, name)
                else:
                    print(name + " does not exist")
            self._wiki_centos_org.add_section_indicator(section, end=True)

    def run(self):
        index_files = glob(self._index_location + "/*.yml")
        for index_file in index_files:
            if "index_template" not in index_file:
                data = load_yaml(index_file)
                if "Projects" not in data:
                    raise Exception("Invalid index file")
                for entry in data["Projects"]:
                    title, section, container_name, target_file_url = self._get_wiki_info(entry)
                    if section not in self._projects_data:
                        self._projects_data[str(section)] = {
                            "title": title,
                            "items": []
                        }
                    self._projects_data[str(section)]["items"].append({
                        "name": container_name,
                        "url": target_file_url
                    })
        self._generate_wiki_content()
