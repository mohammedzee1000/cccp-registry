#!/bin/bash

class IndexEntry:

    def __init__(self, pid, appid, jobid, giturl, gitpath, gitbranch, notifyemail, dependson):

        self._pid = pid
        self._appId = appid
        self._jobId = jobid
        self._gitUrl = giturl
        self._gitPath = gitpath
        self._gitBranch = gitbranch
        self._notifyEmail = notifyemail
        self._dependsOn = dependson

        return

    @property
    def pid(self):
        return self._pid

    @property
    def appId(self):
        return self._appId

    @property
    def jobID(self):
        return self._jobId

    @property
    def gitUrl(self):
        return self._gitUrl

    @property
    def gitPath(self):
        return self._gitPath

    @property
    def gitBranch(self):
        return self._gitBranch

    @property
    def notifyEmail(self):
        return self._notifyEmail

    @property
    def dependsOn(self):
        return self._dependsOn
