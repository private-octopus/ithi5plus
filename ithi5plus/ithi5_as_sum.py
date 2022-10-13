# Main program, printing statistics
import sys
import ithi5file
import os
from os.path import isfile, isdir, join
import datetime

eu_cc_list = [ "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"]
eu_cc_set = set(eu_cc_list)

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

def last_day_of_month(s_year, s_month):
    year = int(s_year)
    month = int(s_month)
    first_day_next_month = datetime.date(year, month, 27)
    last_day_this_month = first_day_next_month
    while first_day_next_month.month == month:
        last_day_this_month = first_day_next_month
        first_day_next_month += datetime.timedelta(1)
    return last_day_this_month.day

def as_sum(source_folder, target_folder, year, month):
    # compute the last day of the month
    # Load the files for dir/year/month/*
    cc_data_list = dict()
    cc_as_data_list = dict()
    nb_days = 0
    last_day = last_day_of_month(year, month)
    source_year = join(source_folder, year)
    if not isdir(source_year):
        print("Not a directory: " + source_year)
        return
    source_month = join(source_year, month)
    if not isdir(source_month):
        print("Not a directory: " + source_month)
        return
    # Sum all the entries per as and cc
    for day in range(1,last_day + 1):
        s_day = str(day)
        if day < 10:
            s_day = "0" + str(day)
        source_day = join(source_month, s_day)
        if isdir(source_day):
            nb_days += 1
            for p in ithi5file.build_file_list(source_day):
                ithi5 = ithi5file.ithi5plus_file(p, year, month, s_day)
                ithi5.load_file()
                for i5pe in ithi5.entries:
                    key = i5pe.cc + "-" + i5pe.as_text;
                    if not key in cc_as_data_list:
                        cc_as_data_list[key] = i5pe;
                    else:
                        cc_as_data_list[key].add_lists(i5pe);
                print("Loaded " + p + " at " + str(datetime.datetime.now()))
    # Consider now all as+cc entries that have at least 100 hits per day on average,
    # add them per contry.
    hits_required = 100*nb_days
    hits_medium = 1000*nb_days
    hits_high = 10000*nb_days
    # write the AS summary 
    metric_day = year + "-" + month + "-" + str(last_day)
    metric_file_name = "AS10-" + metric_day + ".csv"
    metric_file_path = join(target_folder, metric_file_name)
    with open(metric_file_path,"wt") as F:
        ithi5file.ith5plus_entry.write_simple_count_header(F)
        for key in cc_as_data_list:
            if cc_as_data_list[key] >= hits_required and cc_as_data_list[key].as_text != "AS1" :
                cc_as_data_list[key].write_simple_count(F)
    print("Saved data for " + str(len(cc_as_data_list)) + " ASes in " + metric_file_path)

def usage():
    print("Usage:")
    print("    ithi5_as_sum.py source_folder as_folder <year> <month>")
    exit(1)

# Main code
# Read year, month, day from command line.

if len(sys.argv) == 5: 
    source_folder = sys.argv[1]
    target_folder = sys.argv[2]
    year = sys.argv[3]
    month = sys.argv[4]
    print("Computing AS summary " + year + "/" + month)
    as_sum(source_folder, target_folder, year, month)
    print("Done")
else:
    usage()