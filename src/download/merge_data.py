# coding=utf-8
import datetime
import pickle

import pandas as pd

from myutils import MyFiles2


def convert(row):
    trade_time = row.values[1]
    dt = datetime.datetime.strptime(trade_time, "%Y-%m-%d %H:%M:%S")
    return dt



def merge_data(ts_code):
    def _load():
        for year in range(2012, 2020):
            with open(f"/home/cqz/stock_30_min/others/{ts_code}__{year}.df", "rb") as df_file:
                yield pickle.load(df_file)

    dfs = list(_load())
    all_df = pd.concat(dfs)

    all_df['trade_time'] = all_df.apply(convert, axis=1)
    del all_df['ts_code']

    all_df.set_index("trade_time", inplace=True)
    all_df.sort_index(ascending=True, inplace=True)

    with open(f"/home/cqz/stock_30_min/merge/{ts_code}.df", "wb+") as df_file:
        pickle.dump(all_df, df_file)




if __name__ == '__main__':
    for name in MyFiles2.list_test_names():
        merge_data(name)