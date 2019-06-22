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
            return datetime.datetime.strptime(f"{year}-{month}-{day} {_time_str}", "%Y/%m/%d %H%M")

        if k == "30":
            for start, end in ns_30:
                if start < num <= end:
                    _time_str = str(end).zfill(4)
                    return datetime.datetime.strptime(f"{year}-{month}-{day} {_time_str}", "%Y/%m/%d %H%M")

        if k == "60":
            for start, end in ns_60:
                if start < num <= end:
                    _time_str = str(end).zfill(4)
                    return datetime.datetime.strptime(f"{year}-{month}-{day} {_time_str}", "%Y/%m/%d %H%M")

        _time_str = "0000"
        _time_str = str(end).zfill(4)
        return datetime.datetime.strptime(f"{year}-{month}-{day} {_time_str}", "%Y/%m/%d %H%M")

    @classmethod
    def match(cls, df, selected_col_name="selected"):

        if df.empty:
            return False

        tdf = df.tail(1)
        tdf = tdf[tdf[selected_col_name] == True]
        if tdf.empty:
            return False

        return True

    @classmethod
    def select_x003(cls, st_df):
        """
        k30
        """
        name = "selected"

        mdi_df = ZB.mdi(st_df)
        ma_df = ZB.ma(st_df)
        close = st_df['close']

        x1 = ZB.cross(mdi_df['ADX'], mdi_df['ADXR']) & (mdi_df['ADXR'] < 30)
        x2 = mdi_df['DIFF'] > mdi_df['DIFF'].shift(1)
        x21 = (mdi_df['PDI'] > mdi_df['ADXR']) & (mdi_df['PDI'] > mdi_df['MDI'])
        x3 = (ma_df['ma50'] <= close + (close * 0.02)) & (ma_df['ma50'] <= close - (close * 0.02))

        t1 = (mdi_df.index.hour > 10) & (mdi_df.index.hour <= 14)
        mdi_df[name] = False

        mdi_df.ix[t1 & x1 & x2 & x21 & x3, name] = True

        return mdi_df.ix[:, [name]]

    @classmethod
    def select_x004(cls, st_df):
        """
        k60
        """
        name = "selected"

        mdi_df = ZB.mdi(st_df)
        ma_df = ZB.ma(st_df)

        x1 = mdi_df["DIFF"] > mdi_df["DIFF"].shift(1)

        close = st_df['close']
        mdi_df['MAX_ADXR'] = mdi_df['ADXR'].rolling(center=False, min_periods=1, window=10).max()
        #
        # x2 = (mdi_df['ADXR'] < 24) & (mdi_df['DIFF'] > -30)
        x3 = (ma_df['ma50'] <= close + (close * 0.02)) & (ma_df['ma50'] <= close - (close * 0.02))
        # x4 = mdi_df['MAX_ADXR'] < 30
        mdi_df[name] = False

        # mdi_df.ix[x1 & x2 & x3 & kk, name] = True
        mdi_df.ix[x1 & x3, name] = True

        return mdi_df.ix[:, [name]]

    @classmethod
    def select_x005(cls, st_df):
        """
        kd
        """
        name = "selected"

        mdi_df = ZB.mdi(st_df)

        # x1 = kdj_df['kdj_k'] > kdj_df['kdj_k'].shift()

        mdi_df[name] = True

        x1 = mdi_df["DIFF"] > mdi_df["DIFF"].shift(1)
        mdi_df.ix[x1, name] = True

        return mdi_df.ix[:, [name]]

    @classmethod
    def search(cls, df30):

        buy_30 = BuySelector.select_x003(df30)
        buy_30 = buy_30[buy_30['selected'] == True]

        for index, row in buy_30.iterrows():
            base_df = df30[df30.index <= index]

            df60 = gkd.Generator.generate_k_data(base_df, ktype="60").tail(300)
            buy_60 = BuySelector.select_x004(df60)
            match_60 = cls.match(buy_60)

            if not match_60: continue

            df240 = gkd.Generator.generate_k_data(base_df, ktype="D").tail(300)
            buy_240 = BuySelector.select_x005(df240)
            match_240 = cls.match(buy_240)

            if match_60 and match_240:
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
        name = "selected"

        mdi_df = ZB.mdi(st_df, d=8)

        x1 = mdi_df["DIFF"] < mdi_df["DIFF"].shift(1)

        mdi_df[name] = False

        mdi_df.ix[x1, name] = True

        return mdi_df.ix[:, [name]]

    @classmethod
    def select_x005(cls, st_df):
        """
        k_day
        """
        pass


    @classmethod
    def find_sale_point(cls, base_df, dt, sale_point_df):
        find_df = sale_point_df[sale_point_df.index >= dt].head(1)
        if find_df.empty:
            return None

        for index, row in find_df.iterrows():
            return index


