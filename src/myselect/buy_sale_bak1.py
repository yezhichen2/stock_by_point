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

        """
        name = "s004"

        kdj_df = ZB.kdj(st_df)

        x1 = kdj_df["kdj_k"] < kdj_df['kdj_d']
        x2 = kdj_df["kdj_k"] >= kdj_df["kdj_k"].shift(1)

        x3 = ZB.cross(kdj_df["kdj_k"], kdj_df["kdj_d"])

        t1 = kdj_df.index.hour >= 13

        kdj_df[name] = False

        kdj_df.ix[t1 & x1 & x2, name] = True
        kdj_df.ix[t1 & x3, name] = True

        return kdj_df.ix[:, [name]]


    @classmethod
    def select_x004(cls, st_df):
        """
        k<d, k >= ref(k,1) 或者 cross(k,d)
        下午13：00之后操作
        """
        name = "s004"

        kdj_df = ZB.kdj(st_df)

        x1 = kdj_df["kdj_k"] < kdj_df['kdj_d']
        x2 = kdj_df["kdj_k"] >= kdj_df["kdj_k"].shift(1)

        x3 = ZB.cross(kdj_df["kdj_k"], kdj_df["kdj_d"])

        t1 = kdj_df.index.hour >= 13

        kdj_df[name] = False

        kdj_df.ix[t1 & x1 & x2, name] = True
        kdj_df.ix[t1 & x3, name] = True

        return kdj_df.ix[:, [name]]

    @classmethod
    def select_x005(cls, st_df):
        """
        k60
        """
        name = "s005"

        kdj_df = ZB.kdj(st_df)

        diff = kdj_df['kdj_k'] - kdj_df['kdj_d']
        kdj_df["diff"] = diff.ewm(com=2).mean()

        x10 = kdj_df["diff"] > kdj_df["diff"].shift(1)
        x11 = (kdj_df["kdj_k"] > kdj_df["kdj_k"].shift(1)) & (kdj_df["kdj_k"] > kdj_df["kdj_k"].shift(2))
        x2 = kdj_df["diff"] <= 0

        kdj_df[name] = False

        kdj_df.ix[x2 & x10 & x11, name] = True

        return kdj_df.ix[:, [name]]

    @classmethod
    def select_x006(cls, st_df):
        """
        k60
        """
        name = "s006"

        mdi_df = ZB.mdi(st_df)

        x10 = mdi_df["DIFF"] > mdi_df["DIFF"].shift(1)

        mdi_df[name] = False

        mdi_df.ix[x10, name] = True

        return mdi_df.ix[:, [name]]


    @classmethod
    def search(cls, select1, select2, select3):
        input_df = select1[select1['s004'] == True]
        for index, row in input_df.iterrows():

            target_dt = BuySelector.gen_date(index, target_ktype="60")
            match1 = BuySelector.match(target_index=target_dt, target_df=select2, selected_col_name="s005")
            match2 = BuySelector.match(target_index=target_dt, target_df=select3, selected_col_name="s006")

            if match1 and match2:
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

        """
        name = "s004"

        kdj_df = ZB.kdj(st_df)

        diff = kdj_df['kdj_k'] - kdj_df['kdj_d']
        kdj_df["diff"] = diff.ewm(com=1).mean()

        # 高位, 确认趋势变坏
        x1 = kdj_df["diff"] > 0
        x2 = kdj_df["diff"] < kdj_df["diff"].shift(1)
        x3 = kdj_df["diff"].shift(1) <= kdj_df["diff"].shift(2)

        c1 = ZB.cross(kdj_df['kdj_d'], kdj_df['kdj_k'])
        c2 = kdj_df['kdj_k'] >= 30
        kdj_df[name] = False

        kdj_df.ix[x1 & x2 & x3, name] = True
        kdj_df.ix[c1 & c2, name] = True

        return kdj_df.ix[:, [name]]


    @classmethod
    def find_sale_point(cls, dt, sale_point_df):
        find_df = sale_point_df[sale_point_df.index > dt].head(1)
        if find_df.empty:
            return None

        for index, row in find_df.iterrows():
            return index


