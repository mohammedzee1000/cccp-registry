import yaml
import os

class IndexFileManager:

    def __init__(self, indexfilepath):

        if not os.path.exists(indexfilepath):

            raise Exception("Invalid path of indexfile specified")

        self._indexfilepath = indexfilepath

        with open(indexfilepath, "r") as indexfile:

            self._indexdata = yaml.load(indexfile)

        return

    def finalizechanges(self):

        with open(self._indexfilepath, "w") as indexfile:

            yaml.dump(self._indexdata, indexfile)

        return

    def addindexentry(self, id, appid, jobid, giturl, gitpath, gitbranch, notifyemail, dependson=None, targetfile=None):

        t = {}
        success = True

        if id in self._indexdata.keys():

            success = False



        return success