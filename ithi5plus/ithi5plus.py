# Main program, printing statistics
import sys
import ithi5file

class ithi5_cc_as_sum:
    def __init__(self, cc):
        self.key = cc
        self.count = 0.0
        self.w_count = 0.0
        self.open_count = 0.0
        self.nb_as = 0
        self.as_hits = []
        self.open_hits = []
        self.as_count = []
        for i in range(0,10):
            self.as_hits.append(0.0)
            self.open_hits.append(0.0)
            self.as_count.append(0.0)

    def add(self,i5pe):
        i5pi = i5pe.items['xopnrvrs']
        nb_open = i5pe.count - i5pi.count
        ratio = nb_open/i5pe.count
        self.count += i5pe.count
        self.w_count += i5pe.w_count
        self.open_count += nb_open
        self.nb_as += 1
        i_slot = int(10.0*ratio)
        if i_slot < 0:
            i_slot = 0
        elif i_slot >= 10:
            i_slot = 9
        self.as_hits[i_slot] += i5pe.count
        self.open_hits[i_slot] += nb_open
        self.as_count[i_slot] += 1

    def csv_header():
        s = 'cc,count,w_count,open,nb_as'
        for i in range(0,10):
            s += ",h("+str(10*i)+"-"+str(10*(i+1))+"%)"
            s += ",o("+str(10*i)+"-"+str(10*(i+1))+"%)"
            s += ",a("+str(10*i)+"-"+str(10*(i+1))+"%)"
        s += '\n'
        return s

    def csv_line(self):
        s = self.key
        s += "," + str(self.count)
        s += "," + str(self.w_count)
        s += "," + str(self.open_count)
        s += "," + str(self.nb_as)
        for i in range(0,10):
            s += ',' + str(self.as_hits[i])
            s += ',' + str(self.open_hits[i])
            s += ',' + str(self.as_count[i])
        s += '\n'
        return s
 
class ithi5_as_cc_sum:
    def __init__(self, as_text):
        self.key = as_text
        self.count = 0.0
        self.w_count = 0.0
        self.open_count = 0.0
        self.nb_cc = 0
        self.best_cc = ""
        self.best_cc_count = 0
        self.cc_hits = []
        self.open_hits = []
        self.cc_count = []
        for i in range(0,10):
            self.cc_hits.append(0.0)
            self.open_hits.append(0.0)
            self.cc_count.append(0.0)

    def add(self,i5pe):
        i5pi = i5pe.items['xopnrvrs']
        nb_open = i5pe.count - i5pi.count
        ratio = nb_open/i5pe.count
        self.count += i5pe.count
        self.w_count += i5pe.w_count
        self.open_count += nb_open
        self.nb_cc += 1
        if i5pe.count > self.best_cc_count:
            self.best_cc = i5pe.cc
            self.best_cc_count = i5pe.count
        i_slot = int(10.0*ratio)
        if i_slot < 0:
            i_slot = 0
        elif i_slot >= 10:
            i_slot = 9
        self.cc_hits[i_slot] += i5pe.count
        self.open_hits[i_slot] += nb_open
        self.cc_count[i_slot] += 1

    def csv_header():
        s = 'as,count,w_count,open,nb_cc,bcc,bcount,'
        for i in range(0,10):
            s += ",h("+str(10*i)+"-"+str(10*(i+1))+"%)"
            s += ",o("+str(10*i)+"-"+str(10*(i+1))+"%)"
            s += ",a("+str(10*i)+"-"+str(10*(i+1))+"%)"
        s += '\n'
        return s

    def csv_line(self):
        s = self.key
        s += "," + str(self.count)
        s += "," + str(self.w_count)
        s += "," + str(self.open_count)
        s += "," + str(self.nb_cc)
        s += "," + self.best_cc
        s += "," + str(self.best_cc_count)
        for i in range(0,10):
            s += ',' + str(self.cc_hits[i])
            s += ',' + str(self.open_hits[i])
            s += ',' + str(self.cc_count[i])
        s += '\n'
        return s

    def csv_short_header():
        s = 'as,count,w_count,open,ratio,nb_cc,bcc,cc_ratio\n'
        return s
    
    def csv_short_line(self):
        s = self.key
        s += "," + str(self.count)
        s += "," + str(self.w_count)
        s += "," + str(self.open_count)
        s += "," + str(self.open_count/self.count)
        s += "," + str(self.nb_cc)
        s += "," + self.best_cc
        s += "," + str(self.best_cc_count/self.count)
        s += '\n'
        return s


# Main code
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
    print("\nVerifying count vs query count.")
    nb_entries = 0
    for i5pe in ithi5.entries:
        if i5pe.count == i5pe.query_count:
            continue
        nb_entries += 1
        print("Found difference for " + i5pe.as_text + "-" + i5pe.cc + ":")
        print(i5pe.as_text + "-" + i5pe.cc + ", " + str(i5pe.count) + "," + str(i5pe.w_count) + "," + str(i5pe.query_count))
        sum5 = i5pe.sum(i5pe.count, i5pe.w_count)
        print(sum5.service + ", " + str(sum5.count) + "," + str(sum5.share) + "," + str(sum5.w_count) + "," + str(sum5.w_share))
        tots = i5pe.sum(i5pe.count, i5pe.w_count, "totals")
        print(tots.service + ", " + str(tots.count) + "," + str(tots.share) + "," + str(tots.w_count) + "," + str(tots.w_share))
        cc_sum5 = i5pe.sum(i5pe.count, i5pe.w_count, "cc_sum")
        print(cc_sum5.service + ", " + str(cc_sum5.count) + "," + str(cc_sum5.share) + "," + str(cc_sum5.w_count) + "," + str(cc_sum5.w_share))
        print("Service, count, share, w_count, w_share")
        for service in i5pe.cc_items:
            se = i5pe.cc_items[service]
            print(se.service + ", " + str(se.count) + "," + str(se.share) + "," + str(se.w_count) + "," + str(se.w_share))
        print("\n")
        if nb_entries >= 5:
            break

    # evaluate which services are the most popular
    ithi5_per_as = ithi5file.ithi5plus_file(file_path, year, month, day);
    ithi5_per_as.entries = list(ithi5.sumByAS().values())
    ithi5_total = ithi5file.ithi5plus_file(file_path, year, month, day);
    ithi5_total.entries = list(ithi5_per_as.sumByCC().values())
    print("\nPrint the sum of all AS and all CC.")
    for i5pe in ithi5_total.entries:
        print(i5pe.as_text + "-" + i5pe.cc + ", " + str(i5pe.count) + "," + str(i5pe.w_count) + "," + str(i5pe.query_count) + "," + str(i5pe.w_query_count))
        print("Share of resolvers:")
        for service in i5pe.items:
            srv_item = i5pe.items[service]
            print(srv_item.service + ", " + str(srv_item.count) + "," + str(srv_item.share) + "," + str(srv_item.w_count) + "," + str(srv_item.w_share))
    
    print("\nSaving summary files.")
    # Save a simple file per AS
    if len(sys.argv) > 2:
        ithi5_per_as.write_simple_count(sys.argv[2])

    # Save a simple file per CC
    if len(sys.argv) > 3:
        ithi5_per_cc = ithi5file.ithi5plus_file(file_path, year, month, day);
        ithi5_per_cc.entries = list(ithi5.sumByCC().values())
        ithi5_per_cc.write_simple_count(sys.argv[3])

    # save a summary of ASes postures per CC
    cc_as_sum = dict()
    for i5pe in ithi5.entries:
        if not i5pe.cc in cc_as_sum:
            cc_as_sum[i5pe.cc] = ithi5_cc_as_sum(i5pe.cc)
        cc_as_sum[i5pe.cc].add(i5pe)
    with open(sys.argv[4],"wt") as F:
        F.write(ithi5_cc_as_sum.csv_header())
        for cc in cc_as_sum:
            F.write(cc_as_sum[cc].csv_line())

    
    # save a summary of CCes postures per AS
    as_cc_sum = dict()
    for i5pe in ithi5.entries:
        if not i5pe.as_text in as_cc_sum:
            as_cc_sum[i5pe.as_text] = ithi5_as_cc_sum(i5pe.as_text)
        as_cc_sum[i5pe.as_text].add(i5pe)
    with open(sys.argv[5],"wt") as F:
        F.write(ithi5_as_cc_sum.csv_short_header())
        for as_text in as_cc_sum:
            F.write(as_cc_sum[as_text].csv_short_line())

    # save a shortened value of the file
    # but first, get a list of the relevant services

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

    with open(sys.argv[6],"wt") as F:
        F.write("as,cc,samples")
        for srv in service_list:
            F.write("," + srv)
        F.write("\n")
        for i5pe in ithi5.entries:
            # weight = 0
            # if i5pe.w_count > 0 and i5pe.count > 0:
            #     weight = i5pe.w_count/i5pe.count
            F.write(i5pe.as_text + "," + i5pe.cc + "," + '{0:.0f}'.format(i5pe.count)) # + "," + str(weight))
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
                    F.write('{0:.5f}'.format(s_share) + '%')
            F.write("\n")





