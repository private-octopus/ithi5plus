# Main program, printing statistics
import sys
import ithi5file
import os
from os.path import isfile, isdir, join
import datetime

eu_cc_list = [ "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"]
eu_cc_set = set(eu_cc_list)
eu_tb2b_list = [
    "AS12046", "AS12301", "AS12392", "AS12552", "AS12876", "AS13213", "AS15892", "AS16247", "AS16276", "AS16509",
    "AS1930", "AS1955", "AS196640", "AS199155", "AS199524", "AS202422", "AS203020", "AS2107", "AS2108", "AS213183",
    "AS24940", "AS24961", "AS25117", "AS25248", "AS25255", "AS2602", "AS2611", "AS28725", "AS28952", "AS29119",
    "AS29244", "AS29447", "AS31027", "AS31117", "AS31313", "AS3221", "AS32934", "AS34410", "AS35328", "AS35506",
    "AS36183", "AS39737", "AS40676", "AS43513", "AS43561", "AS43624", "AS47232", "AS49282", "AS49725", "AS49981",
    "AS51167", "AS51765", "AS52173", "AS5408", "AS5578", "AS5617", "AS58046", "AS58065", "AS62044", "AS8368",
    "AS8473", "AS8764", "AS8881", "AS9008", "AS9009", "AS9031", "AS9119", "AS21100", "AS14061", "AS28753"]
eu_tb2b_set = set(eu_tb2b_list)

eu_tracked = [ "googlepdns", "cloudflare", "opendns", "level3", "quad9", "neustar" ]
eu_tracked_set = set(eu_tracked)

class eu_cc_cat_line:
    def __init__(self, cc, cat):
        self.cc = cc
        self.cat = cat
        self.cc_hits = 0
        self.count = 0
        self.public_dns_count = 0
        self.public_dns = []
        for tracked in eu_tracked:
            self.public_dns.append(0)
    def add(self, i5pe):
        self.count += int(i5pe.count)
        if "allopnrvrs" in i5pe.tot_items:
            self.public_dns_count += i5pe.tot_items["allopnrvrs"].count
        i = 0
        for tracked in eu_tracked:
            if tracked in i5pe.items:
                self.public_dns[i] += i5pe.items[tracked].count
            i += 1
    def to_string(self):
        s = self.cc + "," + self.cat + "," + str(self.count)
        local = self.count - self.public_dns_count
        s +=  "," + '{0:.2f}'.format(100*local/self.count)
        s +=  "," + str(local)
        s +=  "," + '{0:.2f}'.format(100*self.public_dns_count/self.count) + "%"
        s +=  "," + str(self.public_dns_count)

        others = self.public_dns_count
        for i in range(0,len(eu_tracked)):
            s += "," + '{0:.2f}'.format(100*self.public_dns[i]/self.count) + "%"
            s += "," + str(self.public_dns[i])
            others -= self.public_dns[i]
            i += 1
        s += "," + '{0:.2f}'.format(100*others/self.count) + "%"
        s += "," + str(others)
        s += "\n"
        return s
    def to_header():
        s = "CC, Category, Count"
        s += ", local_%, local" 
        s += ", public_%, public"
        for tracked in eu_tracked:
            s += "," + tracked + "%," + tracked
        s += ",others%,others"
        s += "\n"
        return s;
        

def add_to_key(cc, cat, data_dict, i5pe):
    key = cc + "-" + cat
    if not key in data_dict:
        data_dict[key] = eu_cc_cat_line(cc, cat)
    data_dict[key].add(i5pe)

def last_day_of_month(s_year, s_month):
    year = int(s_year)
    month = int(s_month)
    first_day_next_month = datetime.date(year, month, 27)
    last_day_this_month = first_day_next_month
    while first_day_next_month.month == month:
        last_day_this_month = first_day_next_month
        first_day_next_month += datetime.timedelta(1)
    return last_day_this_month.day

def buildEUReport(source_folder, target_folder, year, month):
    # compute the last day of the month
    # Load the files for dir/year/month/*
    eu_data_dict = dict()
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
                    if not i5pe.cc in eu_cc_set:
                        continue
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
    for key in cc_as_data_list:
        i5pe = cc_as_data_list[key]
        if not i5pe.cc in eu_cc_set:
            continue
        if i5pe.count < hits_required:
            continue
        cat = "isp_medium"
        if i5pe.as_text in eu_tb2b_set:
            cat = "tb2b"
        elif i5pe.count < hits_medium:
            cat = "isp_small"
        elif i5pe.count >= hits_high:
            cat = "isp_big"
        
        add_to_key(i5pe.cc, cat, eu_data_dict, i5pe)
        add_to_key("eu", cat, eu_data_dict, i5pe)
        if cat == "tb2b":
            add_to_key(cat, i5pe.as_text, eu_data_dict, i5pe)
        else:
            add_to_key(i5pe.cc, "isp_all", eu_data_dict, i5pe)
            add_to_key("eu", "isp_all", eu_data_dict, i5pe)

    # At this point, we have summary files for n days in the month
    if len(eu_data_dict) == 0:
        print("Could not find any file in " + source_month)
        return
    # Write the EU report:
    eu_day = year + "-" + month + "-" + str(last_day)
    eu_file_name = "EU-" + eu_day + ".csv"
    eu_file_path = join(target_folder, eu_file_name)

    with open(eu_file_path,"wt") as F:
        F.write("date," + eu_cc_cat_line.to_header())
        key_list = []
        for key in eu_data_dict:
            s = ""
            if key.startswith("eu"):
                s += "1"
            elif key.startswith("b2c"):
                s += "3"
            else:
                s += "2"
            s += key
            key_list.append(s)
        key_list = sorted(key_list)
        for lkey in key_list:
            key = lkey[1:]
            F.write(eu_day + "," + eu_data_dict[key].to_string())
    print("Saved eu data in " + eu_file_path)

def usage():
    print("Usage:")
    print("    ithi5eu.py source_folder target_folder [ <year> <month> ]")
    exit(1)

# Main code
# Read year, month, day from command line.
source_folder = sys.argv[1]
target_folder = sys.argv[2]

if len(sys.argv) == 5: 
    year = sys.argv[3]
    month = sys.argv[4]
    buildEUReport(source_folder, target_folder, year, month)
else:
    usage()
