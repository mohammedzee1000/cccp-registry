import os
from shutil import rmtree
from glob import glob

class Cleaner(object):

    def __init__(self, distribution_store_location="/var/lib/registry"):

        self._distribution_store = distribution_store_location + "/docker/registry/v2"
        self._blobs_location = self._distribution_store + "/blobs"
        self._repos_location = self._distribution_store + "/repositories"

    def _get_reachabe_manifests(self):

        reachable_list = []
        for repo in glob(self._repos_location + "/*/_layers/sha256/*"):
            reachable_list.append(os.path.basename(repo))
        return reachable_list

    def _get_blobs_layers(self):
        blobs_list = []
        for blob in glob(self._blobs_location + "/sha256/*/*"):
            blobs_list.append(os.path.basename(blob))
        return blobs_list

    def _get_unreachable_layers(self):
        reachable_layers = self._get_reachabe_manifests()
        all_layers = self._get_blobs_layers()
        unreachable_layers = []

        for layer in all_layers:
            if layer not in reachable_layers:
                unreachable_layers.append(layer)
        return unreachable_layers

    def _delete_unreachable(self):
        unreachable_layers = self._get_unreachable_layers()

        for layer in unreachable_layers:
            rmtree(self._blobs_location + "/sha256/" + layer[:2] + "/" + layer)

    def run(self):
        print self._get_unreachable_layers()