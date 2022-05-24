#!/usr/local/opt/python/libexec/bin/python
import bz2
import sys
import traceback
import os
from os.path import isfile, isdir, join

# Extract the list of files from the directory
def build_file_list(this_dir):
    this_list = []
    for file_name in os.listdir(this_dir):
        p = join(this_dir, file_name)
        if isdir(p):
            x = build_file_list(p)
            for fp in x:
                this_list.append(fp)
        elif (p.endswith(".bz2") or p.endswith(".dat")) and "6-as" in p:
            this_list.append(p)
    return this_list

# infer date from file path
def date_from_file_path(file_path):
    year = "0000"
    month = "00"
    day = "00"
    if "/" in file_path:
        file_parts = file_path.split("/")
    else:
        file_parts = file_path.split("\\")

    if len(file_path) < 4:
        print("Cannot find date in " + file_path)
    else:
        year = file_parts[-4]
        month = file_parts[-3]
        day = file_parts[-2]
    return year, month, day

# Parsing the input file, building the required object
# if needed, saving as a set of flat files per country, AS, provider, data,
# so that we can then drive tabulation by set of countries, or per set of AS, or per provider network, or per slices of dates.
#
# The original file is a CSV file, which could be parsed using pandas.

class ith5plus_item:
    def get_float(s):
        x = 0.0
        if len(s) > 0:
            x = float(s)
        return x

    def __init__(self, cell_list):
        self.service = cell_list[0]
        
        self.count = ith5plus_item.get_float(cell_list[1])
        self.share = ith5plus_item.get_float(cell_list[2])
        self.w_count = ith5plus_item.get_float(cell_list[3])
        self.w_share = ith5plus_item.get_float(cell_list[4])

        
class ith5plus_entry:
    def __init__(self, file_name, year, month, day):
        self.file_name = file_name
        self.year = year
        self.month = month
        self.day = day
        self.as_text = ""
        self.cc = ""
        self.count = 0.0
        self.w_count = 0.0
        self.query_count = 0.0
        self.w_query_count = 0.0
        self.items = dict()
        self.tot_items = dict()
        self.cc_items = dict()

    def load_line(self, line):
        try:
            # break as csv
            clean_line = line.strip()
            parts = clean_line.split(",")
            # read the fist columns
            self.as_text = parts[0]
            self.cc = parts[1]
            self.count = float(parts[2])
            self.w_count = float(parts[3])
            self.query_count = float(parts[4])
            self.w_query_count = float(parts[5])
            # read a succession of service or groups
            remain_parts = parts[6:]
            while len(remain_parts) > 5:
                line_item = ith5plus_item(remain_parts[0:5])
                if line_item.service in ["incc", "outcc", "inccx", "outccx", "diffcceu", "diffccneu" ]:
                    self.cc_items[line_item.service] = line_item
                elif line_item.service in ["allopnrvrs", "sameas", "samecc", "diffcc"]:
                    self.tot_items[line_item.service] = line_item
                else:
                    self.items[line_item.service] = line_item
                remain_parts = remain_parts[5:]
        except Exception as e:
            traceback.print_exc()
            print("\nException: " + str(e))
            print("line: \n" + line + "\n");
            exit(1)
            
    def sum(self, count, w_count, category="srv"):
        l = []
        if category == "cc_sum":
            l = list(self.cc_items.values())
        elif category == "totals":
            l = list(self.tot_items.values())
        else:
            l = list(self.items.values())
        sum_item = ith5plus_item([category, "0", "0", "0", "0"])
        for line_item in l:
            sum_item.count += line_item.count
            sum_item.share = sum_item.count/count
            sum_item.w_count += line_item.w_count
            sum_item.w_share = sum_item.w_count/w_count
        return sum_item

    def sum_dict(dict1, dict2, count, w_count):
        for service in dict2:
            if not service in dict1:
                dict1[service] = ith5plus_item([service, "0", "0", "0", "0"])
            dict1[service].count += dict2[service].count
            dict1[service].share = dict1[service].count / count
            dict1[service].w_count += dict2[service].w_count
            dict1[service].w_share = dict1[service].w_count / w_count

    def add_lists(self, other):
        self.count += other.count
        self.w_count += other.w_count
        self.query_count += other.query_count
        self.w_query_count += other.w_query_count
        ith5plus_entry.sum_dict(self.items, other.items, self.count, self.w_count)
        ith5plus_entry.sum_dict(self.tot_items, other.tot_items, self.count, self.w_count)
        ith5plus_entry.sum_dict(self.cc_items, other.cc_items, self.count, self.w_count)

    big_services = ["xopnrvrs", "googlepdns", "cloudflare", "dnspai", "opendns", "onedns", "level3", "114dns", "quad9", "greenteamdns" ]
    def write_simple_count(self, F):
        F.write(self.as_text + "," + self.cc + "," + str(self.count) + "," + str(self.w_count))
        for service in ith5plus_entry.big_services:
            i5pi = self.items[service]
            F.write("," + str(i5pi.count))
        F.write("\n")

    def write_simple_count_header(F):
        F.write("AS,CC,count,w_count,")
        for service in ith5plus_entry.big_services:
            F.write("," + service)
        F.write("\n")


class ithi5plus_file:
    def __init__(self, file_name, year, month, day):
        self.file_name = file_name
        self.year = year
        self.month = month
        self.day = day
        self.entries = []

    def load_file(self):
        try:
            # parse each line of the file
            if self.file_name.endswith(".bz2"):
                F = bz2.open(self.file_name,"rt")
            else:
                F = open(self.file_name, "r")
            for line in F:
                i5pe = ith5plus_entry(self.file_name, self.year, self.month, self.day)
                i5pe.load_line(line)
                if i5pe.as_text != "AS0" and i5pe.count > 100:
                    self.entries.append(i5pe)
            F.close()
        except Exception as e:
            traceback.print_exc()
            print("\nException: " + str(e))
            exit(1)

    def sumByCC(self):
        cc_items = dict()
        for i5pe in self.entries:
            try:
                cc = i5pe.cc
                if not cc in cc_items:
                    cc_items[cc] = ith5plus_entry(i5pe.file_name, i5pe.year, i5pe.month, i5pe.day)
                    cc_items[cc].cc = cc
                    cc_items[cc].as_text = "AS*"
                cc_items[cc].add_lists(i5pe)
            except Exception as e:
                traceback.print_exc()
                print("\nException: " + str(e))
                print("Entry: " +  str(i5pe))
                exit(1)
        return cc_items
    
    def sumByAS(self):
        as_items = dict()
        for i5pe in self.entries:
            try:
                as_text = i5pe.as_text
                if not as_text in as_items:
                    as_items[as_text] = ith5plus_entry(i5pe.file_name, i5pe.year, i5pe.month, i5pe.day)
                    as_items[as_text].as_text = as_text
                    as_items[as_text].cc = "XX"
                as_items[as_text].add_lists(i5pe)
            except Exception as e:
                traceback.print_exc()
                print("\nException: " + str(e))
                print("Entry: " +  str(i5pe))
                exit(1)
        return as_items

    def write_simple_count(self, file_name):
        with open(file_name, "wt") as F:
            ith5plus_entry.write_simple_count_header(F)
            for i5pe in self.entries:
                i5pe.write_simple_count(F)

    def write_demographics(self, file_path, service_list):
        with open(file_path,"wt") as F:
            F.write("as,cc,samples")
            for srv in service_list:
                F.write("," + srv)
            F.write("\n")
            for i5pe in self.entries:
                F.write(i5pe.as_text + "," + i5pe.cc + "," + '{0:.0f}'.format(i5pe.count))
                for srv in service_list:
                    s_samples = 0
                    if srv in i5pe.items:
                        s_samples = i5pe.items[srv].count
                    elif srv in i5pe.cc_items:
                        s_samples = i5pe.cc_items[srv].count
                    elif srv in i5pe.tot_items:
                        s_samples = i5pe.tot_items[srv].count
                    F.write(",")
                    if s_samples > 0:
                        s_share = 100*s_samples/i5pe.count
                        decimal_format = '{0:.1f}'
                        if s_share < 0.001:
                            decimal_format = '{0:.5f}'
                        elif s_share < 0.01:
                            decimal_format = '{0:.4f}'
                        elif s_share < 0.1:
                            decimal_format = '{0:.3f}'
                        elif s_share < 1:
                            decimal_format = '{0:.2f}'
                        F.write(decimal_format.format(s_share) + '%')
                F.write("\n")


