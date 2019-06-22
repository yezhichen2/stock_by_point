# coding=utf-8
import pickle
import re
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import gen_k_data as gkd

from zibiao import ZB

pd.set_option("display.max_columns", 500)
pool = ProcessPoolExecutor(max_workers=8)


def load_counter():
    with open("dump/total_counter_1.dp", "rb") as dp:
        obj = pickle.load(dp)
        return obj


def save_fc_list(total_feature_collector):
    with open("dump/tfc.dp", "wb+") as dp:
        pickle.dump(total_feature_collector, dp)


class FeatureCollector(object):

    def __init__(self, p_change, buy_datetime, group=""):
        self.group = group
        self.p_change = p_change
        self.buy_datetime = buy_datetime
        self.data30 = {}
        self.data60 = {}
        self.data240 = {}

    def __str__(self):
        return f"{self.group} {self.buy_datetime}"


class Features(object):
    @classmethod
    def get_max_30k(cls, ktype="60"):
        if ktype == '30':
            return 100
        if ktype == '60':
            return 300

        if ktype == 'D':
            return 2400

        return 3200

    @classmethod
    def _extract(cls, zb_df, cns):
        _df = zb_df.loc[:, cns].tail(1)
        return _df.values[0].tolist()

    @classmethod
    def get_kdj_values(cls, base_df, dt, ktype="60"):
        base_df = base_df[base_df.index <= dt].tail(cls.get_max_30k(ktype))
        data_df = gkd.Generator.generate_k_data(base_df, ktype=ktype)

        zb_df = ZB.kdj(data_df)

        cur_d = zb_df['kdj_d']
        max_d = zb_df['kdj_d'].rolling(center=False, min_periods=1, window=20).max()
        min_d = zb_df['kdj_d'].rolling(center=False, min_periods=1, window=20).max()

        zb_df['up_ratio'] = (cur_d - min_d) / cur_d
        zb_df['down_ratio'] = (max_d - cur_d) / max_d

        cns = ['kdj_k', 'kdj_d', 'up_ratio', 'down_ratio']
        return cls._extract(zb_df, cns)


    @classmethod
    def get_mdi_values(cls, base_df, dt, ktype="60"):
        base_df = base_df[base_df.index <= dt].tail(cls.get_max_30k(ktype))
        data_df = gkd.Generator.generate_k_data(base_df, ktype=ktype)

        zb_df = ZB.mdi(data_df)

        zb_df['energy'] = zb_df["DIFF"] * zb_df['ADXR'] / 100

        e1 = zb_df['energy']
        e3 = zb_df['energy'].shift(3)
        e5 = zb_df['energy'].shift(5)
        e9 = zb_df['energy'].shift(9)
        e15 = zb_df['energy'].shift(15)

        zb_df['e_1_3'] = (e1 - e3) / e3 * 100
        zb_df['e_1_5'] = (e1 - e5) / e5 * 100
        zb_df['e_1_9'] = (e1 - e9) / e9 * 100

        zb_df['e_3_5'] = (e3 - e5) / e5 * 100
        zb_df['e_3_9'] = (e3 - e9) / e9 * 100
        zb_df['e_3_15'] = (e3 - e15) / e15 * 100

        zb_df['e_5_9'] = (e5 - e9) / e9 * 100
        zb_df['e_5_15'] = (e5 - e15) / e15 * 100

        cns = ['ADX', 'ADXR', 'DIFF', 'energy', 'e_1_3', 'e_1_5', 'e_1_9', 'e_3_5', 'e_3_9', 'e_3_15', 'e_5_9', 'e_5_15']
        return cls._extract(zb_df, cns)


    @classmethod
    def get_ma_values(cls, base_df, dt, ktype="60"):
        """
        描述了均线的分布情况
        :param base_df:
        :param dt:
        :param ktype:
        :return:
        """
        base_df = base_df[base_df.index <= dt].tail(cls.get_max_30k(ktype))
        data_df = gkd.Generator.generate_k_data(base_df, ktype=ktype)

        ma_df = ZB.ma(data_df)
        ma_df['close'] = data_df['close']

        ma_df['m_1_5'] = (ma_df['close'] - ma_df['ma5']) / ma_df['ma5'] * 100
        ma_df['m_1_10'] = (ma_df['close'] - ma_df['ma10']) / ma_df['ma10'] * 100
        ma_df['m_5_10'] = (ma_df['ma5'] - ma_df['ma10']) / ma_df['ma10'] * 100
        ma_df['m_5_20'] = (ma_df['ma5'] - ma_df['ma20']) / ma_df['ma20'] * 100
        ma_df['m_10_20'] = (ma_df['ma10'] - ma_df['ma20']) / ma_df['ma20'] * 100
        ma_df['m_10_50'] = (ma_df['ma10'] - ma_df['ma50']) / ma_df['ma50'] * 100

        ma_df['avg'] = (ma_df['m_1_5'] + ma_df['m_1_10'] + ma_df['m_5_10'] +
                        ma_df['m_5_20'] + ma_df['m_10_20'] + ma_df['m_10_50']) / 6

        ma_df['abs'] = (ma_df['m_1_5'].abs() + ma_df['m_1_10'].abs() + ma_df['m_5_10'].abs() +
                        ma_df['m_5_20'].abs() + ma_df['m_10_20'].abs() + ma_df['m_10_50'].abs()) / 6

        cns = ['m_1_5', 'm_1_10', 'm_5_10', 'm_5_20', 'm_10_20', 'm_10_50', 'avg', 'abs']
        return cls._extract(ma_df, cns)

    @classmethod
    def get_p_change_values(cls, base_df, dt, ktype="60"):
        base_df = base_df[base_df.index <= dt].tail(cls.get_max_30k(ktype))
        data_df = gkd.Generator.generate_k_data(base_df, ktype=ktype)

        close = data_df['close']
        pre1_close = data_df['close'].shift(1)
        pre3_close = data_df['close'].shift(3)
        pre5_close = data_df['close'].shift(5)
        pre9_close = data_df['close'].shift(9)
        pre15_close = data_df['close'].shift(15)

        data_df['p_change'] = (close - pre1_close) / pre1_close * 100

        # 累计涨幅
        data_df['p_change_t3'] = (close - pre3_close) / pre3_close * 100
        data_df['p_change_t5'] = (close - pre5_close) / pre5_close * 100
        data_df['p_change_t9'] = (close - pre9_close) / pre9_close * 100
        data_df['p_change_t15'] = (close - pre15_close) / pre15_close * 100

        # 均涨幅
        data_df['p_change_t3_avg'] = data_df['p_change_t3'] / 3
        data_df['p_change_t5_avg'] = data_df['p_change_t5'] / 5
        data_df['p_change_t9_avg'] = data_df['p_change_t9'] / 9
        data_df['p_change_t15_avg'] = data_df['p_change_t15'] / 15

        # 各段涨幅比
        data_df['pch_r_3_5'] = (close - pre3_close) / (close - pre5_close)
        data_df['pch_r_3_9'] = (close - pre3_close) / (close - pre9_close)
        data_df['pch_r_3_15'] = (close - pre3_close) / (close - pre15_close)
        data_df['pch_r_5_9'] = (close - pre5_close) / (close - pre9_close)
        data_df['pch_r_5_15'] = (close - pre5_close) / (close - pre15_close)

        cns = [
            'p_change', 'p_change_t3', 'p_change_t5', 'p_change_t9', 'p_change_t15',
            'p_change_t3_avg', 'p_change_t5_avg', 'p_change_t9_avg', 'p_change_t15_avg',
            'pch_r_3_5', 'pch_r_3_9', 'pch_r_3_15', 'pch_r_5_9', 'pch_r_5_15'
        ]
        return cls._extract(data_df, cns)

    @classmethod
    def get_vol_values(cls, base_df, dt, ktype="60"):
        base_df = base_df[base_df.index <= dt].tail(cls.get_max_30k(ktype))
        data_df = gkd.Generator.generate_k_data(base_df, ktype=ktype)

        # 忽略当前volume
        data_df = data_df[:-1]

        data_df['v3'] = data_df['volume'].rolling(center=False, min_periods=1, window=3).sum()
        data_df['v5'] = data_df['volume'].rolling(center=False, min_periods=1, window=5).sum()
        data_df['v9'] = data_df['volume'].rolling(center=False, min_periods=1, window=9).sum()
        data_df['v15'] = data_df['volume'].rolling(center=False, min_periods=1, window=15).sum()
        data_df['v30'] = data_df['volume'].rolling(center=False, min_periods=1, window=30).sum()
        data_df['v50'] = data_df['volume'].rolling(center=False, min_periods=1, window=50).sum()

        data_df['rv_3_5'] = data_df['v3'] / data_df['v5']
        data_df['rv_3_9'] = data_df['v3'] / data_df['v9']
        data_df['rv_3_15'] = data_df['v3'] / data_df['v15']

        data_df['rv_5_9'] = data_df['v5'] / data_df['v9']
        data_df['rv_5_15'] = data_df['v5'] / data_df['v15']
        data_df['rv_5_30'] = data_df['v5'] / data_df['v30']
        data_df['rv_5_50'] = data_df['v5'] / data_df['v50']

        data_df['rv_15_30'] = data_df['v15'] / data_df['v30']
        data_df['rv_15_50'] = data_df['v15'] / data_df['v50']

        cns = [
            'rv_3_5', 'rv_3_9', 'rv_3_15',
            'rv_5_9', 'rv_5_15', 'rv_5_30', 'rv_5_50',
            'rv_15_30', 'rv_15_50'
        ]
        return cls._extract(data_df, cns)

    @classmethod
    def get_vol_kdj_values(cls, base_df, dt, ktype="60"):
        base_df = base_df[base_df.index <= dt].tail(cls.get_max_30k(ktype))
        data_df = gkd.Generator.generate_k_data(base_df, ktype=ktype)

        # 忽略当前volume
        data_df = data_df[:-1]

        data_df['v5'] = data_df['volume'].rolling(center=False, min_periods=1, window=5).sum()
        data_df['v15'] = data_df['volume'].rolling(center=False, min_periods=1, window=15).sum()

        zb_df = ZB.kdj(data_df)

        zb_df['direction'] = 1

        # 向下的趋势
        xd1 = (zb_df['kdj_d'] < zb_df['kdj_d'].shift(1)) | (zb_df['kdj_k'] < zb_df['kdj_k'].shift(1))

        zb_df.ix[xd1, 'direction'] = -1
        zb_df['energy_d'] = zb_df['direction'] * zb_df['kdj_d']

        data_df['direction'] = zb_df['direction']
        data_df['energy_kdj_d'] = zb_df['energy_d']
        data_df['energy_vol_kdj_d'] = data_df['energy_kdj_d'] * (data_df['v5']/data_df['v15'])

        cns = [
            'direction', 'energy_kdj_d', 'energy_vol_kdj_d'
        ]

        return cls._extract(data_df, cns)


def mk_fc(group, buy_date, p_change, base_df):
    fc = FeatureCollector(p_change, buy_datetime=buy_date, group=group)

    # day ktype
    kdj_values_240 = Features.get_kdj_values(base_df, buy_date, ktype="D")
    ma_values_240 = Features.get_ma_values(base_df, buy_date, ktype="D")
    mdi_values_240 = Features.get_mdi_values(base_df, buy_date, ktype="D")
    p_change_values_240 = Features.get_p_change_values(base_df, buy_date, ktype="D")
    vol_values_240 = Features.get_vol_values(base_df, buy_date, ktype="D")
    vol_kdj_values_240 = Features.get_vol_kdj_values(base_df, buy_date, ktype="D")

    fc.data240["kdj_values"] = kdj_values_240
    fc.data240["ma_values"] = ma_values_240
    fc.data240["mdi_values"] = mdi_values_240
    fc.data240["p_change_values"] = p_change_values_240
    fc.data240["vol_values"] = vol_values_240
    fc.data240["vol_kdj_values"] = vol_kdj_values_240

    # 60 ktype
    kdj_values_60 = Features.get_kdj_values(base_df, buy_date, ktype="60")
    ma_values_60 = Features.get_ma_values(base_df, buy_date, ktype="60")
    mdi_values_60 = Features.get_mdi_values(base_df, buy_date, ktype="60")
    p_change_values_60 = Features.get_p_change_values(base_df, buy_date, ktype="60")
    vol_values_60 = Features.get_vol_values(base_df, buy_date, ktype="60")
    vol_kdj_values_60 = Features.get_vol_kdj_values(base_df, buy_date, ktype="60")

    fc.data60["kdj_values"] = kdj_values_60
    fc.data60["ma_values"] = ma_values_60
    fc.data60["mdi_values"] = mdi_values_60
    fc.data60["p_change_values"] = p_change_values_60
    fc.data60["vol_values"] = vol_values_60
    fc.data60["vol_kdj_values"] = vol_kdj_values_60

    # 30 ktype
    kdj_values_30 = Features.get_kdj_values(base_df, buy_date, ktype="30")
    ma_values_30 = Features.get_ma_values(base_df, buy_date, ktype="30")
    mdi_values_30 = Features.get_mdi_values(base_df, buy_date, ktype="30")
    p_change_values_30 = Features.get_p_change_values(base_df, buy_date, ktype="30")
    vol_values_30 = Features.get_vol_values(base_df, buy_date, ktype="30")

    fc.data30["kdj_values"] = kdj_values_30
    fc.data30["ma_values"] = ma_values_30
    fc.data30["mdi_values"] = mdi_values_30
    fc.data30["p_change_values"] = p_change_values_30
    fc.data30["vol_values"] = vol_values_30

    return fc


def p_change_to_label3(p_change):
    if p_change < 0:
        return 9

    if p_change >= 6:
        return 1

    if p_change >= 3:
        return 2

    if p_change >= 1:
        return 3

    else:
        return 4


def p_change_to_label(p_change):
    if p_change < -0.6:
        return 3

    if p_change >= 1.4:
        return 1
    else:
        return 2


def p_change_to_label_2(p_change):
    if p_change >= -0.6:
        return 1
    else:
        return 2


def create_feature_df(fc_list, to_label_func=p_change_to_label):

    def extract_data(zb_values, prefix, label):
        data = {}
        for i, v in enumerate(zb_values.get(label, [])):
            data[f"{label}__{prefix}__{i + 1:03}"] = v

        return data

    # --------------------------------------------#
    data_list = []

    for fc in fc_list:
        fc_item_data = dict()
        fc_item_data['label'] = to_label_func(fc.p_change)
        fc_item_data['p_change'] = fc.p_change

        fc_item_data.update(extract_data(fc.data240, 240, label="kdj_values"))
        fc_item_data.update(extract_data(fc.data240, 240, label="ma_values"))
        fc_item_data.update(extract_data(fc.data240, 240, label="mdi_values"))
        fc_item_data.update(extract_data(fc.data240, 240, label="p_change_values"))
        fc_item_data.update(extract_data(fc.data240, 240, label="vol_values"))
        fc_item_data.update(extract_data(fc.data240, 240, label="vol_kdj_values"))

        fc_item_data.update(extract_data(fc.data60, 60, label="kdj_values"))
        fc_item_data.update(extract_data(fc.data60, 60, label="ma_values"))
        fc_item_data.update(extract_data(fc.data60, 60, label="mdi_values"))
        fc_item_data.update(extract_data(fc.data60, 60, label="p_change_values"))
        fc_item_data.update(extract_data(fc.data60, 60, label="vol_values"))
        fc_item_data.update(extract_data(fc.data60, 60, label="vol_kdj_values"))

        fc_item_data.update(extract_data(fc.data30, 30, label="kdj_values"))
        fc_item_data.update(extract_data(fc.data30, 30, label="ma_values"))
        fc_item_data.update(extract_data(fc.data30, 30, label="mdi_values"))
        fc_item_data.update(extract_data(fc.data30, 30, label="p_change_values"))
        fc_item_data.update(extract_data(fc.data30, 30, label="vol_values"))

        data_str = str(fc_item_data)

        if re.findall("inf,", data_str):
            continue

        data_list.append(fc_item_data)

    df1 = pd.DataFrame(data_list, index=pd.Index(range(len(data_list))))
    df1 = df1.dropna()
    return df1


def to_mk_fc(name, base_df, rec):
    buy_date = rec.by_date
    p_change = rec.p_change

    fc = mk_fc(name, buy_date, p_change, base_df)

    return fc


def run_collector():

    total_feature_collector = []
    counter = load_counter()

    for child in counter.child:
        name = child.group
        print(name)
        print(f"length of {len(total_feature_collector)}")

        base_df = gkd.read_min30_data(name)

        def _mk_params():
            params = [[], [], []]
            for rec in child.data[1:]:
                params[0].append(name)
                params[1].append(base_df)
                params[2].append(rec)

            return params

        for fc in pool.map(to_mk_fc, *_mk_params()):
            if fc: total_feature_collector.append(fc)

    save_fc_list(total_feature_collector)


if __name__ == '__main__':
    run_collector()
