
import os
import random
import string

class BuildLogger:

    def __init__(self, loglocation):

        if not os.path.isabs(loglocation):

            loglocation = os.path.abspath(loglocation)

        self._logLocation = loglocation
        self._buildLogsLocation = loglocation + "/build.logs"

        self._builtContainers = {
            "success": [

            ],
            "failure": [

            ]
        }

        return

    @staticmethod
    def _generaterandomstring(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def addsuccessbuild(self, dockerfilePath):

        self._builtContainers["success"].append(dockerfilePath)

        return

    def addfailedbuild(self, dockerfilePath):

        self._builtContainers["failure"].append(dockerfilePath)

        return

    def generateBuildLogFile(self, dockerfilePath, logFileName=None):

        flname = os.path.basename(dockerfilePath) + BuildLogger._generaterandomstring()

        if logFileName is not None:

            flname = logFileName

        return open(flname, "w")

