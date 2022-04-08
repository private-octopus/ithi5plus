# Main program, printing statistics
import sys
import ithi5file

file_path = sys.argv[1]
file_parts = []

if "/" in file_path:
    file_parts = file_path.split("/")
else:
    file_parts = file_path.split("\\")

if len(file_path) < 4:
    print("Cannot find date in " + file_path)
    exit(1)
else:
    year = file_parts[-4]
    month = file_parts[-3]
    day = file_parts[-2]
    print("File " + file_path + ", " + year + "/" + month + "/" + day)

    ithi5 = ithi5file.ithi5plus_file(file_path, year, month, day)
    ithi5.load_file()
    nb_entries = 0
    for i5pe in ithi5.entries:
        cc_sum5 = i5pe.sum("cc_sum")
        if i5pe.count1 == i5pe.count2:
            continue
        nb_entries += 1
        print(i5pe.as_text + "-" + i5pe.cc + ", " + str(i5pe.count1) + "," + str(i5pe.pop_size1) + "," + str(i5pe.count2) + "," + str(i5pe.pop_size2))
        sum5 = i5pe.sum()
        print(sum5.service + ", " + str(sum5.a) + "," + str(sum5.b) + "," + str(sum5.c) + "," + str(sum5.d))
        tots = i5pe.sum("totals")
        print(tots.service + ", " + str(tots.a) + "," + str(tots.b) + "," + str(tots.c) + "," + str(tots.d))
        print(cc_sum5.service + ", " + str(cc_sum5.a) + "," + str(cc_sum5.b) + "," + str(cc_sum5.c) + "," + str(cc_sum5.d))
        for service in i5pe.cc_items:
            se = i5pe.cc_items[service]
            print(se.service + ", " + str(se.a) + "," + str(se.b) + "," + str(se.c) + "," + str(se.d))
        if nb_entries >= 5:
            break

    # evaluate which services are the most popular
    ithi5_per_as = ithi5file.ithi5plus_file(file_path, year, month, day);
    ithi5_per_as.entries = list(ithi5.sumByAS().values())
    ithi5_total = ithi5file.ithi5plus_file(file_path, year, month, day);
    ithi5_total.entries = list(ithi5_per_as.sumByCC().values())

    for i5pe in ithi5_total.entries:
        print(i5pe.as_text + "-" + i5pe.cc + ", " + str(i5pe.count1) + "," + str(i5pe.pop_size1) + "," + str(i5pe.count2) + "," + str(i5pe.pop_size2))
        for service in i5pe.items:
            srv_item = i5pe.items[service]
            print(srv_item.service + ", " + str(srv_item.a) + "," + str(srv_item.b) + "," + str(srv_item.c) + "," + str(srv_item.d))

    # Save a simple file per AS
    if len(sys.argv) > 2:
        ithi5_per_as.write_simple_count(sys.argv[2])

    # Save a simple file per CC
    if len(sys.argv) > 3:
        ithi5_per_cc = ithi5file.ithi5plus_file(file_path, year, month, day);
        ithi5_per_cc.entries = list(ithi5.sumByCC().values())
        ithi5_per_cc.write_simple_count(sys.argv[3])

    # save a simple file per CC

    # TODO: load files for a whole month. Perform statistics.
    # What statistics?
    # - Per contry summaries: maybe band diagram, top N, share, share of all services, share of classic DNS.
    # - Present as table for now.
    # - Maybe sort by type of AS.



