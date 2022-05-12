# Main program, printing statistics
import sys
import ithi5file

class cc_day_item:
    def __init__(self, cc, as_text, samples, w_samples, year, month, day):
        self.cc = cc
        self.as_text = as_text
        self.samples = samples
        self.w_samples = w_samples
        self.year = year
        self.month = month
        self.day = day

    def add(self, samples, w_samples):
        self.samples += samples
        self.w_samples += w_samples

class data_stats:
    def __init__(self):
        self.nb = 0
        self.sum = 0
        self.average = 0
        self.min = 0
        self.max = 0

    def add(self, v):
        self.nb += 1
        self.sum += v
        self.average = self.sum / self.nb
        if v < self.min or self.nb == 1:
            self.min = v
        if v > self.max:
            self.max = v
            
    def csv_string(self):
        s = str(self.min) + "," + str(self.average) + "," + str(self.max) 
        return s

class cc_stats:
    def __init__(self, cc):
        self.cc = cc
        self.sample_share = data_stats()
        self.weight_share = data_stats()
        self.weight_factor = data_stats()

    def add(self, count, w_count, total_count, total_w_count):
        self.sample_share.add(count / total_count)
        self.weight_share.add(w_count / total_w_count)
        self.weight_factor.add(w_count / count)




# Main code
in_dir = sys.argv[1]

# first, build a list of files 
f_list = ithi5file.build_file_list(in_dir)
print("Found " + str(len(f_list)) + " files")

# next, sum the day files.
# for each CC, we want to compute the sum of samples and the sum of weights
# we want then to have lines per CC and date providing the values
# and testing ratios compared to the "total" country

# for each AS, we want to compute the number of samples per CC across all
# days. The goal is to isolate ASes that span multiple countries, and look
# for anomalies

day_sum = dict()
cc_by_day = dict()
as_cc = dict()
cc_list = dict()
as_list = dict()

for p in f_list:
    # infer date from file name
    year, month, day = ithi5file.date_from_file_path(p)
    print(year + "-" + month + "-" + day + ", " + p)
    ithi5 = ithi5file.ithi5plus_file(p, year, month, day)
    ithi5.load_file()
    day_key = "--" + year + "-" + month + "-" + day
    day_sum[day_key] = cc_day_item("", "", 0, 0, year, month, day)
    for ithi_e in ithi5.entries:
        # compute total for the day
        day_sum[day_key].add(ithi_e.count, ithi_e.w_count)
        # register cc in list
        if not ithi_e.cc in cc_list:
            cc_list[ithi_e.cc] = cc_stats(ithi_e.cc)
        # compute total by CC and day
        cc_day_key = ithi_e.cc + "-" + day_key
        if cc_day_key in cc_by_day:
            cc_by_day[cc_day_key].add(ithi_e.count, ithi_e.w_count)
        else:
            cc_by_day[cc_day_key] = cc_day_item(ithi_e.cc, "", ithi_e.count, ithi_e.w_count, year, month, day)
        # compute total by AS and CC
        as_cc_key = ithi_e.cc + "-" + ithi_e.as_text
        if as_cc_key in as_cc:
            as_cc[as_cc_key].add(ithi_e.count, ithi_e.w_count)
        else:
            as_cc[as_cc_key] = cc_day_item(ithi_e.cc, ithi_e.as_text, ithi_e.count, ithi_e.w_count, "", "", "")

# AS statistics
#
# Compute the number of CC per AS, top N CC per AS, share of traffic
# Write as CSV file

# CC statistics.
#
# Maybe, Extract data in CSV files for a sample of CC
# Compute ratios, min, max, average
# - count over sum(count, all CC). Shows the "share of country in samples"
# - w_count over sum(w_count, all CC). Shows the "share of country in population"
# Trace per day
# - sum(w_count,all CC) over sum(count, all CC). Is there a link?
for day_key in day_sum:
    total_count = day_sum[day_key].samples
    total_w_count = day_sum[day_key].w_samples
    for cc in cc_list:
        cc_day_key = cc + "-" + day_key
        if cc_day_key in cc_by_day:
            count = cc_by_day[cc_day_key].samples
            w_count = cc_by_day[cc_day_key].w_samples
            cc_list[cc].add(count, w_count, total_count, total_w_count)

with open(sys.argv[2], "wt") as F:
    F.write("cc,sample_share_min,sample_share_avg,sample_share_max,weight_share_min,weight_share_avg,weight_share_max,factor_min,factor_avg,factor_max\n");
    for cc in cc_list:
        F.write(cc + "," + cc_list[cc].sample_share.csv_string() + "," + cc_list[cc].weight_share.csv_string() + "," + cc_list[cc].weight_factor.csv_string() + "\n")

# CC AS statistics
# - fraction of traffic in single CC AS.
# - fraction in AS0
# - fraction in shared AS. Maybe some ratio.
    

        






