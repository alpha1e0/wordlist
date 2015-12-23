
import json
from collections import OrderedDict

source = open("cms_identify.txt", "r")
dest = open("cms_identify.json", "w")

#result = {}
result = OrderedDict()

for line in source:
    line = line.strip()
    if line and not line.startswith("/**"):
        l = line.split()
        if not result.get(l[0], None):
            result[l[0]] = []

        result[l[0]].append({"need":True if l[1]=="+" else False, "path":l[2], "pattern":None if len(l)==3 else l[3]})

print result
json.dump(result, dest, indent=4)

source.close()
dest.close()
