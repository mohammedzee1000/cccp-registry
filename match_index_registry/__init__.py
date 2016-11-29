from Matcher import Matcher
from json import dumps
from sys import argv

indexd_location = argv[1]
m = Matcher(indexd_location)
print dumps(m.run())
