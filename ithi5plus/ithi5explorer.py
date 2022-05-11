# Main program, printing statistics
import sys
import ithi5file
import os
from os.path import isfile, isdir, join
from pathlib import Path

def build_file_list(this_dir):
    this_list = []
    for file_name in os.listdir(this_dir):
        p = join(this_dir, file_name)
        if isdir(p):
            x = build_file_list(p)
            for fp in x:
                this_list.append(fp)
        else:
            this_list.append(p)
    return this_list



# Main code
in_dir = sys.argv[1]

f_list = build_file_list(in_dir)
for p in f_list:
    if p.endswith(".bz2") or p.endswith(".dat"):
        if "6_as" in p:
            print(p)
