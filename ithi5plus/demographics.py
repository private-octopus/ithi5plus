#!/usr/local/opt/python/libexec/bin/python
#
# This is the exporter for the "demographics" project.
# Usage:
#     python3 demographics.py source_folder target_folder [ <year> <month> ]
# If year and month as specified, the code will process entries for that file
# and month. If not, the code will process entries for this month and for
# the revious month.
#
# The source folder is organized as <source_folder>/<year>/<month>/<day>/rvr-du-6-as.dat
# The target folder is organized as <target_folder>/year/rvr-as-cc-<year>-<month>-<day>.dat
#
# The exported filed are a cleaned up version from the original data, going
# through the conversion program.
#
# The goal of the program is to synchronize the two directories. First, check that
# the target folder exists, and create it if the year is not present. Then, list the
# files in the source folder for the relevant months. Then, if the file does not exist
# in the target folder, create it.

import sys
import ithi5file
import traceback
import os
from os.path import isfile, isdir, join
import datetime


def usage():
    print("Usage:")
    print("    demographics.py source_folder target_folder [ <year> <month> ]")
    exit(1)

def demographics(source_folder, target_folder, year, month):
    target_year = join(target_folder, year)
    source_year = join(source_folder, year)
    source_month = join(source_year, month)

    if not isdir(target_year):
        try:
            os.mkdir(target_year, mode = 0o777)
            print("Created directory: " + target_year)
        except Exception as e:
            print("Cannot create directory: " + target_year)
            traceback.print_exc()
            print("\nException: " + str(e))
            usage()

    service_list = [
            "allopnrvrs",
            "sameas",
            "samecc",
            "diffcc",
            "cloudflare",
            "cnnic",
            "dnspai",
            "dnspod",
            "dnswatch",
            "dyn",
            "freedns",
            "googlepdns",
            "greenteamdns",
            "he",
            "level3",
            "neustar",
            "onedns",
            "opendns",
            "opennic",
            "quad9",
            "uncensoreddns",
            "vrsgn",
            "yandex",
            "comodo",
            "safedns",
            "freenom",
            "cleanbrowsing",
            "alternatedns",
            "puntcat",
            "alidns",
            "baidu",
            "114dns",
            "quad101"
            ]

    try:
        if not isdir(source_month):
            print("Directory " + source_month + " does not exist.")
        else:
            for day in os.listdir(source_month):
                source_day = join(source_month, day)
                if isdir(source_day):
                    for source_file_name in os.listdir(source_day):
                        if (source_file_name.endswith(".bz2") or source_file_name.endswith(".dat")) and "6-as" in source_file_name:
                            # build a target file name and path
                            target_file_name = "rvr-as-cc-" + year + "-" + month + "-" + day + ".csv"
                            target_file_path = join(target_year, target_file_name)
                            # if the target does no exist, it should be created
                            if not isfile(target_file_path):
                                source_file_path = join(source_day, source_file_name)
                                print(source_file_path + " exists, " + target_file_path + " does_not.")
                                try:
                                    ithi5 = ithi5file.ithi5plus_file(source_file_path, year, month, day)
                                    ithi5.load_file()
                                    capture_date = year + "-" + month + "-" + day
                                    ithi5.write_demographics(target_file_path, service_list, capture_date)
                                    print("Saved " + target_file_path)
                                except Exception as e:
                                    print("Cannot save demographics: " + source_file_path)
                                    traceback.print_exc()
                                    print("\nException: " + str(e))
                                    usage()
    except Exception as e:
        print("Cannot list directory: " + source_month)
        traceback.print_exc()
        print("\nException: " + str(e))
        usage()

# main

if len(sys.argv) != 5 and len(sys.argv) != 3:
    usage()
source_folder = sys.argv[1]
target_folder = sys.argv[2]

if len(sys.argv) == 5: 
    year = sys.argv[3]
    month = sys.argv[4]
    demographics(source_folder, target_folder, year, month)
else:
    current_day = datetime.datetime.now()
    year = str(current_day.year)
    month = str(current_day.month).zfill(2)
    first_day = datetime.date(current_day.year, current_day.month, 1)
    delta_one_day = datetime.timedelta(1)
    previous_day = first_day - delta_one_day
    previous_year = str(previous_day.year)
    previous_month = str(previous_day.month).zfill(2)
    print("Synchronizing " + year + "/" + month)
    demographics(source_folder, target_folder, year, month)
    print("Synchronizing " + previous_year + "/" + previous_month)
    demographics(source_folder, target_folder, previous_year, previous_month)
    print("Done")


    
