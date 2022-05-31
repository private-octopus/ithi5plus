# Main program, printing statistics
import sys
import ithi5file
import os
from os.path import isfile, isdir, join

class m10_as_per_cc :
    def __init__(self, as_text):
        self.as_text = as_text
        self.count = 0
        self.open_dns_count = 0

class m10_per_country:
    def __init__(self, cc):
        self.cc = cc
        self.count = 0
        self.open_dns_count = 0
        self.open_dns = dict()
        self.tot_items = dict()

    def load(self, ithi5e):
        self.count += ithi5e.count

        for tot_i in ithi5e.tot_items:
            tot_x = tot_i
            if tot_x == "sameas":
                tot_x = "samecc"
            if not tot_x in self.tot_items:
                self.tot_items[tot_x] = 0
            self.tot_items[tot_x] += ithi5e.tot_items[tot_i].count
        if "allopnrvrs" in ithi5e.tot_items:
            open_dns_count = ithi5e.tot_items["allopnrvrs"].count
            self.open_dns_count += open_dns_count
        for odns in ithi5e.items:
            if odns == "xopnrvrs":
                continue
            if ithi5e.items[odns].count > 0:
                if odns in self.open_dns:
                    self.open_dns[odns] += ithi5e.items[odns].count
                else:
                    self.open_dns[odns] = ithi5e.items[odns].count

    def write_m10_line(F, sub_metric, last_day_of_month, key, v):
        # format fractions using at most three digits
        iv = int(v)
        decimal_format = '{0:.0f}'
        if iv != v:
            decimal_format = '{0:.4f}'
        F.write(sub_metric + "," + last_day_of_month + ",v2.0," + key + "," + decimal_format.format(v) + "\n")

    def write_m10(self, F, last_day_of_month):
        sub10 = "M10." + self.cc + "."
        # fraction of open resolver services, and other per country statistics
        allopen = 0
        samecc = 0
        diffcc = 0
        if "allopnrvrs" in self.tot_items:
            allopen = self.tot_items["allopnrvrs"]
        if "samecc" in self.tot_items:
            samecc = self.tot_items["samecc"]
        if "diffcc" in self.tot_items:
            diffcc = self.tot_items["diffcc"]
        m10_per_country.write_m10_line(F, sub10 + "1", last_day_of_month, "", allopen/self.count)
        m10_per_country.write_m10_line(F, sub10 + "2", last_day_of_month, "", samecc/self.count)
        m10_per_country.write_m10_line(F, sub10 + "3", last_day_of_month, "", diffcc/self.count)
        min_value = self.count * 0.00005
        for odns in self.open_dns:
            if self.open_dns[odns] > min_value:
                m10_per_country.write_m10_line(F, sub10 + "4", last_day_of_month, odns, self.open_dns[odns]/self.count)
        # number of samples
        m10_per_country.write_m10_line(F, sub10 + "5", last_day_of_month, "", self.count)

    def add(self,other):
        self.count += other.count
        self.open_dns_count += other.open_dns_count
        for tot_i in other.tot_items:
            if not tot_i in self.tot_items:
                self.tot_items[tot_i] = 0
            self.tot_items[tot_i] += other.tot_items[tot_i]
        for odns in other.open_dns:
            if odns in self.open_dns:
                self.open_dns[odns] += other.open_dns[odns]
            else:
                self.open_dns[odns] = other.open_dns[odns]

# Main code
# Read year, month, day from command line.
year = sys.argv[1]
month = sys.argv[2]
day = sys.argv[3]
# Read main folder from command line.
folder = sys.argv[4]
# Load the files for dir/year/month/*
cc_data_list = dict()
for p in ithi5file.build_file_list(folder):
    ithi5 = ithi5file.ithi5plus_file(p, year, month, day)
    ithi5.load_file()
    for i5pe in ithi5.entries:
        if not i5pe.cc in cc_data_list:
            cc_data_list[i5pe.cc] = m10_per_country(i5pe.cc)
        cc_data_list[i5pe.cc].load(i5pe)
# Sum of all the files for the month
zz_data =  m10_per_country('ZZ')
for cc in cc_data_list:
    zz_data.add(cc_data_list[cc])
# Write the metrics:
last_day_of_month = year + "-" + month + "-" + day
with open(sys.argv[5],"wt") as F:
    zz_data.write_m10(F,last_day_of_month)
    for cc in cc_data_list:
        cc_data_list[cc].write_m10(F,last_day_of_month)
