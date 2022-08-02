# Main program, printing statistics
import sys
import ithi5file
import os
from os.path import isfile, isdir, join
import datetime
import functools
import ip2as

class m10_as_per_cc :
    def __init__(self, as_text):
        self.as_text = as_text
        self.count = 0
        self.open_dns_count = 0

def compare_by_pdns(item, other):
    n1 = item.get_pdns()
    n2 = other.get_pdns()
    if n1 < n2:
        return -1
    elif n1 > n2:
        return 1
    elif item.count < other.count:
        return -1
    elif item.count > other.count:
        return 1
    elif item.as_text < other.as_text:
        return -1
    elif item.as_text > other.as_text:
        return 1
    else:
        return 0

def last_day_of_month(s_year, s_month):
    year = int(s_year)
    month = int(s_month)
    first_day_next_month = datetime.date(year, month, 27)
    last_day_this_month = first_day_next_month
    while first_day_next_month.month == month:
        last_day_this_month = first_day_next_month
        first_day_next_month += datetime.timedelta(1)
    return last_day_this_month.day

def cloudhunt(source_folder, target, as_file, year, month):
    # compute the last day of the month
    # Load the files for dir/year/month/*

    as_names = ip2as.asname()
    as_names.load(as_file)
    print("loaded " + str(len(as_names.table)) + " AS names.")

    as_data_list = dict()
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
    # Sum all the entries per as
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
                    key = i5pe.as_text;
                    if not key in as_data_list:
                        as_data_list[key] = i5pe;
                    else:
                        if i5pe.count > as_data_list[key].count:
                            as_data_list[key].cc = i5pe.cc
                        as_data_list[key].add_lists(i5pe);
                print("Loaded " + p + " at " + str(datetime.datetime.now()))

    # Consider now all as+cc entries that have at least 100 hits per day on average,
    # add them per contry.
    hits_required = 100*nb_days
    nb_saved = 0
    with open(target,"wt") as F:
        F.write("AS_name,")
        ithi5file.ith5plus_entry.write_simple_count_header(F)
        as_data = sorted(list(as_data_list.values()), key=functools.cmp_to_key(compare_by_pdns), reverse=True)
        for i5pe in as_data:
            if i5pe.count >= hits_required:
                asn = as_names.as_nb(i5pe.as_text)
                asn_name = as_names.name(asn)
                F.write("\"" + asn_name + "\",")
                i5pe.write_simple_count(F)
                nb_saved += 1
    print("Saved data for " + str(nb_saved) + " ASes in " + target)

def usage():
    print("Usage:")
    print("    cloudhunt.py source_folder target as_file")
    exit(1)

# Main code
# Read year, month, day from command line.
source_folder = sys.argv[1]
target = sys.argv[2]
as_file = sys.argv[3]

if len(sys.argv) == 6: 
    year = sys.argv[4]
    month = sys.argv[5]
    cloudhunt(source_folder, target, as_file, year, month)
else:
    current_day = datetime.datetime.now()
    year = str(current_day.year)
    month = str(current_day.month).zfill(2)
    first_day = datetime.date(current_day.year, current_day.month, 1)
    delta_one_day = datetime.timedelta(1)
    previous_day = first_day - delta_one_day
    previous_year = str(previous_day.year)
    previous_month = str(previous_day.month).zfill(2)
    cloudhunt(source_folder, target, as_file, year, month)
    print("Done")