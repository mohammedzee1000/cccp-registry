import lib_helpers
import errors


class IndexInfo(object):

    def __init__(self, tid, app_id, job_id, git_url, git_path, git_branch, target_file, desired_tag, notify_email,
                 depends_on):

        if not isinstance(depends_on, list):
            depends_on = [depends_on]

        self._id = tid
        self._app_id = app_id
        self._job_id = job_id
        self._git_url = git_url
        self._git_path = git_path
        self._git_branch = git_branch
        self._target_file = target_file
        self._desired_tag = desired_tag
        self._notify_email = notify_email
        self._depends_on = depends_on

    def get_id(self):
        return self._id

    def get_app_id(self):
        return self._app_id

    def get_job_id(self):
        return self._job_id

    def get_git_url(self):
        return self._git_url

    def get_git_path(self):
        return self._git_path

    def get_git_branch(self):
        return self._git_branch

    def get_target_file(self):
        return self._target_file

    def get_desired_tag(self):
        return self._desired_tag

    def get_notify_email(self):
        return self.get_notify_email()

    def get_depends_on(self, tostring=False):
        if tostring:
            return ",".join(self._depends_on)
        return self._depends_on


class CccpInfo(object):

    def __init__(self, job_id, test_skip, test_script, build_script, delivery_script, custom_delivery, docker_index):
        self._job_id = job_id
        self._test_skip = test_skip
        self._test_script = test_script
        self._build_script = build_script
        self._delivery_script = delivery_script
        self._custom_delivery = custom_delivery
        self._docker_index = docker_index


class Project(object):

    def __init__(self, index_file):
        self._index_file = index_file
        self._cccp_yaml_file = None
        self._index_info = None
        self._cccp_info = None

    def _load_index(self, index_data):
        pass

    def _load_cccp_yaml(self, cccp_yaml_data):
        pass

    def load_cccp(self, cccp_yaml_path):
        self._cccp_yaml_file = cccp_yaml_path
        self._load_cccp_yaml(lib_helpers.load_yaml(cccp_yaml_path))
