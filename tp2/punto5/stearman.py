import csv
import pandas as pd
txt_file = r"TF_IDF_2.res"
csv_file = r"TF_IDF.csv"

data = pd.read_csv(txt_file, sep=" ", header = None)
data.columns = ["a", "b", "c", "d", "e", "f"]

print data