# coding=utf-8
import datetime
import pickle

import pandas as pd

from gen_k_data import Generator
from concurrent.futures import ProcessPoolExecutor

data_input_dir = "/home/cqz/Stk_Min5_QFQ_20190616"
data_ouput_dir = "/home/cqz/stock_30_min"

pool = ProcessPoolExecutor(max_workers=8)

def convert(row):
    trade_time = row['trade_time']
    dt = datetime.datetime.strptime(trade_time, "%Y/%m/%d %H:%M")
    return dt



def merge_data(ts_code):

    with open(f"{data_input_dir}/{ts_code}.CSV") as csv_file:
        df05 = pd.read_csv(csv_file, names=['trade_date', 'trade_time', 'open', 'high', 'low', 'close', 'volume', 'amount'])

    df05['trade_time'] = df05['trade_date'] + ' ' + df05['trade_time']

    df05['date'] = df05.apply(convert, axis=1)
    del df05['trade_date']
    del df05['trade_time']

    df05.set_index("date", inplace=True)
    df05.sort_index(ascending=True, inplace=True)

    df30 = Generator.generate_k_data(df05, ktype='30')
    with open(f"{data_ouput_dir}/{ts_code}.df", "wb+") as df_file:
        pickle.dump(df30, df_file)

    return ts_code

def get_all_code():
    import os, re
    for root, dirs, files in os.walk(data_input_dir):
        for filename in files:
            find = re.findall("((?:SZ|SH)\d{6})", filename)
            if find:
                yield find[0]


if __name__ == '__main__':

    all_codes = list(get_all_code())
    length = len(all_codes)
    count = 0

    for res in pool.map(merge_data, all_codes):
        count += 1
        print(f"{res}  ->  {count/length*100:.2f}")
