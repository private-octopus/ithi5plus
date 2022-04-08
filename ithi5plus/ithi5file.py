#!/usr/local/opt/python/libexec/bin/python
import sys
import traceback

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
        
        self.a = ith5plus_item.get_float(cell_list[1])
        self.b = ith5plus_item.get_float(cell_list[2])
        self.c = ith5plus_item.get_float(cell_list[3])
        self.d = ith5plus_item.get_float(cell_list[4])

        
class ith5plus_entry:
    def __init__(self, file_name, year, month, day):
        self.file_name = file_name
        self.year = year
        self.month = month
        self.day = day
        self.as_text = ""
        self.cc = ""
        self.count1 = 0.0
        self.pop_size1 = 0.0
        self.count2 = 0.0
        self.pop_size2 = 0.0
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
            self.count1 = float(parts[2])
            self.pop_size1 = float(parts[3])
            self.count2 = float(parts[4])
            self.pop_size2 = float(parts[5])
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
            
    def sum(self, category="srv"):
        l = []
        if category == "cc_sum":
            l = list(self.cc_items.values())
        elif category == "totals":
            l = list(self.tot_items.values())
        else:
            l = list(self.items.values())
        sum_item = ith5plus_item([category, "0", "0", "0", "0"])
        for line_item in l:
            sum_item.a += line_item.a
            sum_item.b += line_item.b
            sum_item.c += line_item.c
            sum_item.d += line_item.d
        return sum_item

    def sum_dict(dict1, dict2):
        for service in dict2:
            if not service in dict1:
                dict1[service] = ith5plus_item([service, "0", "0", "0", "0"])
            dict1[service].a += dict2[service].a
            dict1[service].b += dict2[service].b
            dict1[service].c += dict2[service].c
            dict1[service].d += dict2[service].d

    def add_lists(self, other):
        self.count1 += other.count1
        self.pop_size1 += other.pop_size1
        self.count2 += other.count2
        self.pop_size2 += other.pop_size2
        ith5plus_entry.sum_dict(self.items, other.items)
        ith5plus_entry.sum_dict(self.tot_items, other.tot_items)
        ith5plus_entry.sum_dict(self.cc_items, other.cc_items)

    big_services = ["xopnrvrs", "googlepdns", "cloudflare", "dnspai", "opendns", "onedns", "level3", "114dns", "quad9", "greenteamdns" ]
    def write_simple_count(self, F):
        F.write(self.as_text + "," + self.cc + "," + str(self.count1))
        for service in ith5plus_entry.big_services:
            i5pi = self.items[service]
            F.write("," + str(i5pi.a))
        F.write("\n")

    def write_simple_count_header(F):
        F.write("AS,CC,count")
        for service in ith5plus_entry.big_services:
            F.write("," + service)
        F.write("\n")


class ithi5plus_file:
    def __init__(self, file_name, year, month, day):
        print("Inside init file")
        self.file_name = file_name
        self.year = year
        self.month = month
        self.day = day
        self.entries = []

    def load_file(self):
        try:
            # parse each line of the 
            for line in open(self.file_name, "r"):
                i5pe = ith5plus_entry(self.file_name, self.year, self.month, self.day)
                i5pe.load_line(line)
                self.entries.append(i5pe)
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
                    cc_items[cc].as_text = "AS0"
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


