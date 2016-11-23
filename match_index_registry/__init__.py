from Matcher import Matcher
from sys import argv

indexd_location = argv[1]
m = Matcher(indexd_location)
print m.run()