#!/usr/bin/python
# coding=utf-8
#
# AS classification.
# This program updates a classification list of ASes, created as argument.
# The classification list is a CSV file, with the following columns:
# - AS_text, e.g., AS12345
# - classification, one of "isp", "cloud" or "business"
# - date of classification
# - author
# - supporting URL

import datetime
import webbrowser
import sys
import os
import traceback

# Does a path exist?
# This is false for dangling symbolic links on systems that support them.
def exists(path):
    """Test whether a path exists.  Returns False for broken symbolic links"""
    try:
        os.stat(path)
    except OSError:
        return False
    return True

def get_as_class_num(t):
    r = -1
    if t == "isp":
        r = 0
    elif t == "business":
        r = 1
    elif t == "cloud":
        r = 2
    return r


class record_line:
    def __init__(self):
        self.as_text = ""
        self.as_class = ""
        self.date_class = ""
        self.author = ""
        self.url_class = ""

    def parse(self, line):
        clean_line = line.strip()
        parts = clean_line.split(",")
        try:
            self.as_text = parts[0].strip()
            self.as_class = parts[1].strip()
            self.date_class = parts[2].strip()
            self.author = parts[3].strip()
            self.url_class = parts[4].strip()
        except Exception as e:
            traceback.print_exc()
            print("\nException: " + str(e))
            print("line: \n" + clean_line + "\n")

    def to_text(self):
        s = self.as_text
        s += "," + self.as_class
        s += "," + self.date_class
        s += "," + self.author
        s += "," + self.url_class
        return s

    def header_text():
        s = "as_text"
        s += ",as_class"
        s += ",date"
        s += ",author"
        s += ",url"
        return s


class record_dict:
    def __init__(self):
        self.r_dict = dict()

    def add_record(self, record, records_file):
        if not record.as_text in self.r_dict:
            self.r_dict[record.as_text] = []
        self.r_dict[record.as_text].append(record)
        if records_file != "":
            with open(records_file, "at") as F:
                s = record.to_text() + "\n"
                F.write(s)

    def load_line(self, line):
        record = record_line()
        record.parse(line)
        if not record.as_text in self.r_dict:
            self.r_dict[record.as_text] = []
        self.r_dict[record.as_text].append(record)

    def load_file(self, records_file):
        for line in open(records, "rt"):
            # parse and store the record line
            self.load_line(line)

    def get_guess(self, as_text):
        g = ""
        g_c = 0
        c = [ 0, 0, 0]
        if as_text in self.r_dict:
            l = self.r_dict[as_text]
            for r in l:
                r_i = get_as_class_num(r.as_class)
                r_c = 0
                if r_i >= 0:
                    c[r_i] += 1
                    r_c = c[r_i]
                if r_c > 0 and r_c >= g_c:
                    g = r.as_class
                    g_c = r_c
        return g

class as_stat_line:
    def __init__(self):
        self.as_name = ""
        self.as_text = ""
        self.cc = ""
        self.count = 0
        self.w_count = 0
        self.pdns = 0
        self.xopnrvrs = 0
        self.googlepdns = 0
        self.cloudflare = 0
        self.dnspai = 0
        self.opendns = 0
        self.onedns = 0
        self.level3 = 0
        self.n114dns = 0
        self.quad9 = 0
        self.greenteamdns = 0

    def parse(self, line):
        ret = True
        clean_line = line.strip()
        parts = clean_line.split(",")
        if parts[0] == "AS_name":
            ret = False
            print("Found header: \n" + clean_line)
        else:
            try:
                self.as_name = ""
                while len(parts) > 16:
                    self.as_name += parts[0].strip() + " "
                    parts = parts[1:]
                self.as_name += parts[0].strip()
                self.as_text =  parts[1].strip()
                self.cc =  parts[2].strip()
                self.count = int(float(parts[3].strip()))
                self.w_count = int(float(parts[4].strip()))
                self.pdns = int(float(parts[5].strip()))
                self.xopnrvrs = int(float(parts[6].strip()))
                self.googlepdns = int(float(parts[7].strip()))
                self.cloudflare = int(float(parts[8].strip()))
                self.dnspai = int(float(parts[9].strip()))
                self.opendns = int(float(parts[10].strip()))
                self.onedns = int(float(parts[11].strip()))
                self.level3 = int(float(parts[12].strip()))
                self.n114dns = int(float(parts[13].strip()))
                self.quad9 = int(float(parts[14].strip()))
                self.greenteamdns = int(float(parts[15].strip()))
            except Exception as e:
                traceback.print_exc()
                print("\nException: " + str(e))
                print("line: \n" + clean_line + "\n")
                ret = False
            if ret and not self.as_text.startswith("AS"):
                print("Incorrect AS number: \n" + clean_line)
                ret = False
        return ret

# main
author=sys.argv[1]
records = sys.argv[2]
stats = sys.argv[3]

current_day = datetime.datetime.now()
str_date = current_day.isoformat()

if not exists(records):
    print("Need to create record file: " + records)
    try:
        with open(records,"wt") as F:
            F.write(record_line.header_text() + "\n")
    except Exception as e:
        traceback.print_exc()
        print("\nException: " + str(e))
        print("Cannot create record file: " + records)
        exit()
else:
    print("File alredy exists: " + records)

r_dict = record_dict()
r_dict.load_file(records)

for line in open(stats, "rt"):
    as_stat = as_stat_line()
    if as_stat.parse(line):
        r_g = r_dict.get_guess(as_stat.as_text)
        if r_g == "":
            record = record_line()
            record.date_class = str_date
            record.as_text = as_stat.as_text
            if 10*as_stat.pdns < as_stat.count or as_stat.count < 30000:
                record.author = "auto"
                record.as_class = "isp"
            else:
                record.author = author
                print("\nExplaining:\n" + line.strip())
                url = "https://duckduckgo.com/?q=" + as_stat.as_text
                webbrowser.open(url)
                record.url_class = input("Webpage for provider? ")
                r_c = -1
                while r_c < 0:
                    record.as_class = input("AS class for " + as_stat.as_text + " ? ")
                    r_c = get_as_class_num(record.as_class)
                    if r_c < 0:
                        print("\"" + record.as_class + "\" is not a proper AS class. Use \"isp\", \"cloud\", or \"business\"")
            r_dict.add_record(record, records)
    else:
        print("Cannot parse:\n" + line)



