# Main program, printing statistics
import sys
import ithi5file
import os
from os.path import isfile, isdir, join
import datetime

eu_cc_list = [ "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"]
eu_cc_set = set(eu_cc_list)

region_AP = ["AF","AQ","AM","AU","AZ","BH","BD","BT","BN","KH","CN","CX","CC","CK","CY","FJ","GE","HM",\
    "HK","IN","ID","IR","IQ","IL","JP","JO","KZ","KI","KP","KR","KW","KG","LA","LB","MO","MY","MV","MH",\
    "FM","MN","MM","NR","NP","NZ","NU","NF","OM","PK","PW","PS","PG","PH","QA","WS","SA","SG","SB","LK",\
    "SY","TW","TJ","TH","TL","TK","TO","TR","TM","TV","AE","UZ","VU","VN","YE"]
region_EUR = ["AX","AL","AD","AI","AW","AC","AT","BY","BE","BM","BA","BV","IO","BG","KY","HR","CW","CZ",\
    "DK","EE","FK","FO","FI","FR","GF","PF","TF","DE","GI","GR","GL","GP","GG","VA","HU","IS","IE","IM",\
    "IT","JE","LV","LI","LT","LU","MT","MQ","YT","MD","MC","ME","MS","NL","NC","MK","NO","PN","PL","PT",\
    "RE","RO","RU","SH","PM","SM","RS","SK","SI","GS","ES","SJ","SE","CH","TC","UA","UK .GB","VG","WF"]
region_AF = ["DZ","AO","BJ","BW","BF","BI","CM","CV","CF","TD","KM","CG","CD","CI","DJ","EG","GQ","ER",\
    "SZ","ET","GA","GM","GH","GN","GW","KE","LS","LR","LY","MG","MW","ML","MR","MU","MA","MZ","NA","NE",\
    "NG","RW","ST","SN","SC","SL","SO","ZA","SS","SD","TZ","TG","TN","UG","EH","ZM","ZW"]
region_NA = ["AS","CA","GU","MP","PR","US","UM","VI"]
region_LAC = ["AG","AR","BS","BB","BZ","BO","BQ","BR","CL","CO","CR","CU","DM","DO","EC","SV","GD","GT",\
    "GY","HT","HN","JM","MX","NI","PA","PY","PE","BL","KN","LC","MF","VC","SX","SR","TT","UY","VE"]

region_list = [ "XAP", "XEU", "XAF",  "XNA", "XLA" ]
region_sets = [ set(region_AP), set(region_EUR), set(region_AF), set(region_NA), set(region_LAC) ]

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

def buildm10(source_folder, target_folder, year, month):
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
    for key in cc_as_data_list:
        i5pe = cc_as_data_list[key]
        as_class = "medium"
        if i5pe.count >= hits_required:
            if not i5pe.cc in cc_data_list:
                cc_data_list[i5pe.cc] = m10_per_country(i5pe.cc)
            cc_data_list[i5pe.cc].load(i5pe)
            open_dns_count = 0
            if "allopnrvrs" in i5pe.tot_items:
                open_dns_count = i5pe.tot_items["allopnrvrs"].count

    # At this point, we have summary files for n days in the month
    if len(cc_data_list) == 0:
        print("Could not find any file in " + source_month)
        return
    # Sum of all the files for the month to get the 'ZZ' entry,
    # and all the files in EU countries to get the "EU" entry.
    zz_data = m10_per_country('ZZZ')
    region_data = []
    for i in range(0, len(region_list)):
        region_data.append(m10_per_country(region_list[i]))
    
    for cc in cc_data_list:
        zz_data.add(cc_data_list[cc])
        for i in range(0, len(region_list)):
            if cc in region_sets[i]:
                region_data[i].add(cc_data_list[cc])

    # Write the metrics:
    metric_day = year + "-" + month + "-" + str(last_day)
    metric_file_name = "M10-" + metric_day + ".csv"
    metric_file_path = join(target_folder, metric_file_name)
    with open(metric_file_path,"wt") as F:
        zz_data.write_m10(F,metric_day)
        for region_dt in region_data:
            region_dt.write_m10(F,metric_day)
        for cc in cc_data_list:
            cc_data_list[cc].write_m10(F,metric_day)
    print("Saved data for " + str(len(cc_data_list)) + " countries in " + metric_file_path)

def usage():
    print("Usage:")
    print("    ithi5m10.py source_folder target_folder [ <year> <month> ]")
    exit(1)

# Main code
# Read year, month, day from command line.
source_folder = sys.argv[1]
target_folder = sys.argv[2]

if len(sys.argv) == 5: 
    year = sys.argv[3]
    month = sys.argv[4]
    buildm10(source_folder, target_folder, year, month)
else:
    current_day = datetime.datetime.now()
    year = str(current_day.year)
    month = str(current_day.month).zfill(2)
    first_day = datetime.date(current_day.year, current_day.month, 1)
    delta_one_day = datetime.timedelta(1)
    previous_day = first_day - delta_one_day
    previous_year = str(previous_day.year)
    previous_month = str(previous_day.month).zfill(2)
    print("Building M10 " + year + "/" + month)
    buildm10(source_folder, target_folder, year, month)
    last_day_of_month(previous_year, previous_month)
    print("Building M10 " + previous_year + "/" + previous_month)
    buildm10(source_folder, target_folder, previous_year, previous_month)
    print("Done")