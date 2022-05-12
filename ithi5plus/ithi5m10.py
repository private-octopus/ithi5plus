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
        self.ases = dict()
        self.open_dns = dict()

    def load(self, ithi5e):
        self.count += ithi5e.count
        if not ithi5e.as_text in self.ases:
            self.ases[ithi5e.as_text] = m10_as_per_cc(ithi5e.as_text)
        self.ases[ithi5e.as_text].count += ithi5e.count
        if "allopnrvrs" in ithi5e.tot_items:
            open_dns_count = ithi5e.tot_items["allopnrvrs"].count
            self.open_dns_count += open_dns_count
            self.ases[ithi5e.as_text].open_dns_count += open_dns_count
        for odns in ithi5e.items:
            if odns == "xopnrvrs":
                continue
            if ithi5e.items[odns].count > 0:
                if odns in self.open_dns:
                    self.open_dns[odns] += ithi5e.items[odns].count
                else:
                    self.open_dns[odns] = ithi5e.items[odns].count

    def write_m10_line(F, sub_metric, last_day_of_month, key, v):
        F.write(sub_metric + "," + last_day_of_month + ",v2.0," + key + "," + str(v) + "\n")

    def write_m10(self, F, last_day_of_month):
        sub10 = "M10." + self.cc + "."
        # fraction of open resolver services
        m10_per_country.write_m10_line(F, sub10 + "1", last_day_of_month, "", self.open_dns_count/self.count)
        # main open resolvers
        for odns in self.open_dns:
            m10_per_country.write_m10_line(F, sub10 + "2", last_day_of_month, odns, self.open_dns[odns]/self.count)
        # fraction of ASes delegating <= 10%
        # fraction of ASes delegating >= 90%
        nb_as = len(self.ases)
        if nb_as > 0:
            nb_10pc = 0
            nb_90pc = 0
            for as_text in self.ases:
                if self.ases[as_text].open_dns_count <= 0.1*self.ases[as_text].count:
                    nb_10pc += 1
                elif self.ases[as_text].open_dns_count >= 0.9*self.ases[as_text].count:
                    nb_90pc += 1
            m10_per_country.write_m10_line(F, sub10 + "3", last_day_of_month, "", nb_10pc/nb_as)
            m10_per_country.write_m10_line(F, sub10 + "4", last_day_of_month, "", nb_90pc/nb_as)
        # number of ASes
        m10_per_country.write_m10_line(F, sub10 + "5", last_day_of_month, "", nb_as)
        # number of samples
        m10_per_country.write_m10_line(F, sub10 + "6", last_day_of_month, "", self.count)

    def add(self,other):
        self.count += other.count
        self.open_dns_count += other.open_dns_count
        for as_text in other.ases:
            if not as_text in self.ases:
                self.ases[as_text] = m10_as_per_cc(as_text)
            self.ases[as_text].count += other.ases[as_text].count
            self.ases[as_text].open_dns_count += other.ases[as_text].open_dns_count
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
