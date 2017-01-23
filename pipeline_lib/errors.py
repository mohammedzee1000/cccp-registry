class MalformedIndexYaml(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(*args, **kwargs)