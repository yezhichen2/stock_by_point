# coding=utf-8
import time
import pickle
from functools import lru_cache

import pandas as pd
import datetime
import myconf
from cache_tool import api_cache


@lru_cache(maxsize=100)
def fix_dt_num(num, k="30"):
    ns_30 = [
        (931, 1000), (1001, 1030), (1031, 1100), (1101, 1130),
        (1301, 1330), (1331, 1400), (1401, 1430), (1431, 1500)
    ]

    ns_60 = [
        (931, 1030), (1031, 1130), (1301, 1400), (1401, 1500)
    ]

    if k == "D":
        return 0

    if k == "30":
        for start, end in ns_30:
            if start <= num <= end:
                return end

    if k == "60":
        for start, end in ns_60:
            if start <= num <= end:
                return end

    return 0


def convert_date_time(k="60"):

    def convert(row):

        at = row['at']
        t = f"{at.hour:02}{at.minute:02}"
        t = fix_dt_num(int(t), k=k)
        t = str(t).zfill(4)
        date_str = f"{at.year:04}-{at.month:02}-{at.day:02} {t}"
        dt = datetime.datetime.strptime(f"{date_str}", "%Y-%m-%d %H%M")
        return dt

    return convert


def read_min30_data(code):
    return Generator.read_min30_data(code)


class Generator(object):

    @classmethod
    @api_cache(ex=3600 * 480)
    def read_min30_data(cls, code):
        fname = f"{myconf.data_dir}/{code}.df"
        with open(fname, "rb") as df_file:
            min30_df = pickle.load(df_file)

        return min30_df

    @classmethod
    def generate_k_data(cls, base_df, ktype="60"):

        df = base_df.ix[:]

        df['at'] = df.index

        df['at_group'] = df.apply(convert_date_time(k=ktype), axis=1)

        df_gb = df.groupby("at_group")

        group_open = df_gb['open'].first()

        df_target = group_open.to_frame(name='open')
        df_target['close'] = df_gb['close'].last()
        df_target['high'] = df_gb['high'].max()
        df_target['low'] = df_gb['low'].min()
        df_target['volume'] = df_gb['volume'].sum()
        df_target['amount'] = df_gb['amount'].sum()

        df_target.index.rename("date", inplace=True)
        df_target.sort_index(ascending=True, inplace=True)
        return df_target


def main():
    pd.set_option("display.max_columns", 500)

    # df = read_5min_data('files/SH#600280.txt')
    # df_d = generate_k_data(df, ktype="30")

    df = Generator.read_min30_data('SH600268')
    df60 = Generator.generate_k_data(base_df=df, ktype="60")

    print(df60)


if __name__ == '__main__':
    main()



