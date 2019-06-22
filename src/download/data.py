# coding=utf-8
import pickle
import re

import tushare as ts

from myutils import MyFiles2

me = 'eb5feb836c6e2819542b15fa003fa14be19823e44264ea6a0010a1c9'
pro = ts.pro_api(me)


def load_30_min_data(ts_code, year):

    try:
        df = pro.mins(
            ts_code=ts_code, freq='30min',
            start_time=f"{year}0101 09:00:00", end_time=f'{year}1231 15:00:00', adj='qfq'
        )

        with open(f"/home/cqz/stock_30_min/{ts_code}__{year}.df", "wb+") as df_file:
            pickle.dump(df, df_file)
    except Exception as e:

        print(f"Error or {ts_code} for {year}")


def load_zz500():
    names = list(MyFiles2.list_test_names())[:200]

    for name in names:

        find = re.findall(r"(SH|SZ)#(\d{6})", name)
        _name = f'{find[0][1]}.{find[0][0]}'

        for year in range(2012, 2020):
            load_30_min_data(_name, year)


if __name__ == '__main__':

    # load_zz500()
    df = pro.index_daily(
        ts_code='000905.SH'
    )

    print(df)