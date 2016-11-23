import urllib2
from json import load


class DockerDistributionRequester:

    def __init__(self, registry_url, registry_port=None, secure=True):

        if secure:
            if "https" not in registry_url:
                registry_url = "https://" + registry_url
        else:
            if "http" not in registry_url:
                registry_url = "http://" + registry_url
        self._registry_url = registry_url
        if registry_port is not None:
            self._registry_url = registry_url + ":" + str(registry_port)

    def _request_url(self, append_url):

        url = self._registry_url + append_url
        try:
            req = urllib2.urlopen(url)
        except Exception:
            req = None

        return req

    def get_all_repos(self):

        append_url = "/v2/_catalog"
        req = self._request_url(append_url)
        if req is None:
            return None
        return load(req)["repositories"]

    def get_repo_tags(self, repo_name):

        append_url = "/v2/" + repo_name + "/tags/list"
        req = self._request_url(append_url)
        if req is None:
            return None
        return load(req)["tags"]

    def get_image_manifest(self, repo_name, reference):

        append_url = "/v2/" + repo_name + "/manifests/" + reference
        req = self._request_url(append_url)
        if req is None:
            return None
        return load(req)
