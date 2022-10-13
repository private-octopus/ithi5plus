# From M10 published data, get CC graph

import sys

with open(sys.argv[2],"wt") as F:
    cc = ""
    sum = ""
    frac = ""
    for line in open(sys.argv[1],"rt"):
        line = line.strip()
        cols = line.split(",")
        if len(cols) <= 1:
            continue
        first = cols[0].split(".")
        if len(first) <= 2:
            continue
        if first[1] != cc:
            if cc != "":
                F.write(cc + "," + sum + "," + frac + "\n")
            cc = first[1]
            sum = ""
            frac = ""
        metric = first[2].strip()
        if metric == "1":
            frac = cols[4]
        elif metric == "5":
            sum = cols[4]


