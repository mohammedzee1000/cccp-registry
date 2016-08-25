import yaml
from subprocess import check_call, call
import os


class BuildImage:

    def __init__(self, targetfilepath, imagetag, buildcontext):

        self._target_file_path = str(targetfilepath)
        self._image_tag = str(imagetag)
        self._build_context = str(buildcontext)

    def build(self):

        get_back = os.getcwd()
        f = open("./builder-logs.log", "a+")
        os.chdir(self._build_context)
        cmd = ["docker", "build", "-t", self._image_tag, "-f", self._target_file_path, "."]
        check_call(cmd, stdout=f)
        f.close()
        os.chdir(get_back)


class BuildHandler:

    def __init__(self, listfile):

        self._listFile = listfile
        self._build_context = None
        self._builds = []

        if not os.path.exists(self._listFile):
            raise ValueError("Invalid path of list file specified.")

        yamldata = None

        with open(listfile, "r") as tf:
            yamldata = yaml.load(tf)

        if "build-images" not in yamldata:
            raise ValueError("Invalid list file")

        for entry in yamldata["build-images"]["builds"]:

            self._builds.append({
                "file": entry["file"],
                "tag": entry["tag"],
                "context": entry["context"]
            })

    def dobuilds(self):

        for bld in self._builds:

            print str.format("\nBuilding {0}, tagged as {1}\n", bld["file"], bld["tag"])
            BuildImage(bld["file"], bld["tag"], bld["context"]).build()