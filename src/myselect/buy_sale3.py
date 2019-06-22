# coding=utf-8
import datetime
import pandas as pd
import gen_k_data as gkd
from zibiao import ZB

pd.set_option("display.max_columns", 500)


class BuySelector(object):

    @classmethod
    def gen_date(cls, dt, target_ktype="60"):

        ns_30 = [
            (930, 1000), (1000, 1030), (1030, 1100), (1100, 1130),
            (1300, 1330), (1330, 1400), (1400, 1430), (1430, 1500)
        ]

        ns_60 = [
            (930, 1030), (1030, 1130), (1300, 1400), (1400, 1500)
        ]
        k = target_ktype

        year, month, day = dt.year, dt.month, dt.day
        num = int(str(dt.hour).zfill(2) + str(dt.minute).zfill(2))

        if k == "D":
            _time_str = "0000"
            return datetime.datetime.strptime(f"{year}/{month}/{day} {_time_str}", "%Y/%m/%d %H%M")

        if k == "30":
            for start, end in ns_30:
                if start < num <= end:
                    _time_str = str(end).zfill(4)
                    return datetime.datetime.strptime(f"{year}/{month}/{day} {_time_str}", "%Y/%m/%d %H%M")

        if k == "60":
            for start, end in ns_60:
                if start < num <= end:
                    _time_str = str(end).zfill(4)
                    return datetime.datetime.strptime(f"{year}/{month}/{day} {_time_str}", "%Y/%m/%d %H%M")

        _time_str = "0000"
        _time_str = str(end).zfill(4)
        return datetime.datetime.strptime(f"{year}/{month}/{day} {_time_str}", "%Y/%m/%d %H%M")

    @classmethod
    def match(cls, target_index, target_df, selected_col_name):
        tdf = target_df[(target_df.index == target_index) & (target_df[selected_col_name] == True)]
        if tdf.empty:
            return False
        return True

    @classmethod
    def select_x003(cls, st_df):
        """
        k30
        """
        name = "s003"

        mdi_df = ZB.mdi(st_df)
        x1 = (mdi_df["DIFF"] > mdi_df["DIFF"].shift(1)) & (mdi_df["DIFF"] > mdi_df["DIFF"].shift(2))
        x2 = ZB.cross(mdi_df['ADX'], mdi_df['ADXR'])

        mdi_df[name] = False

        mdi_df.ix[x1 & x2, name] = True

        return mdi_df.ix[:, [name]]

    @classmethod
    def select_x004(cls, st_df):
        """
        k60
        """
        name = "s004"

        mdi_df = ZB.mdi(st_df)

        x1 = mdi_df["DIFF"] > mdi_df["DIFF"].shift(1)
        # x2 = mdi_df['ADXR'] < mdi_df['ADXR'].shift(1)

        mdi_df[name] = False

        mdi_df.ix[x1, name] = True

        return mdi_df.ix[:, [name]]

    @classmethod
    def select_x005(cls, st_df):
        """
        kd
        """
        name = "s005"

        kdj_df = ZB.kdj(st_df)

        x1 = kdj_df["kdj_k"] > kdj_df["kdj_k"].shift(1)
        # x2 = kdj_df["kdj_k"] <= 80

        kdj_df[name] = False

        kdj_df.ix[x1, name] = True

        return kdj_df.ix[:, [name]]


    @classmethod
    def search(cls, select11, select21, select31):

        input_df = select11[select11['s003'] == True]
        for index, row in input_df.iterrows():

            # target_dt30 = BuySelector.gen_date(index, target_ktype="30")
            target_dt60 = BuySelector.gen_date(index, target_ktype="60")
            target_dtd = BuySelector.gen_date(index, target_ktype="D")

            match21 = BuySelector.match(target_index=target_dt60, target_df=select21, selected_col_name="s004")
            match31 = BuySelector.match(target_index=target_dtd, target_df=select31, selected_col_name="s005")

            if match21 and match31:
                yield index


class SaleSelector(object):

    @classmethod
    def gen_next_date(cls, dt):
        year, month, day = dt.year, dt.month, dt.day

        next_start_dt = datetime.datetime(year, month, day, 9, 30) + datetime.timedelta(days=1)
        return next_start_dt

    @classmethod
    def select_x004(cls, st_df):
        """
        k60
        """
        name = "s004"

        mdi_df = ZB.mdi(st_df)

        x1 = mdi_df["DIFF"] < mdi_df["DIFF"].shift(1)

        mdi_df[name] = False

        mdi_df.ix[x1, name] = True

        return mdi_df.ix[:, [name]]


    @classmethod
    def find_sale_point(cls, dt, sale_point_df):
        find_df = sale_point_df[sale_point_df.index > dt].head(1)
        if find_df.empty:
            return None

        for index, row in find_df.iterrows():
            return index


