# coding=utf-8
import pickle
import re

import pandas as pd

from myfeatures.feature2 import FeatureCollector, create_feature_df


def load_fc_list():
    with open("dump/tfc_1.dp", "rb") as dp:
        obj = pickle.load(dp)
        return obj



def analysis_correlation(features_df):
    columns = features_df.columns
    columns = [col for col in columns.values if re.findall("values", col)]

    items = []
    for col in columns:
        item_df = feautes_df.ix[:, ['p_change', col]]
        corr1 = item_df.corr(method='pearson').tail(1).values[0][0]
        corr2 = item_df.corr(method='kendall').tail(1).values[0][0]
        corr3 = item_df.corr(method='spearman').tail(1).values[0][0]

        corr_sum = abs(corr1) + abs(corr2) + abs(corr3)

        items.append([col, corr_sum, corr1, corr2, corr3])

    items.sort(key=lambda item: abs(item[1]))

    for item in items:
        print(item)


if __name__ == '__main__':

    fc_list = load_fc_list()
    feautes_df = create_feature_df(fc_list)

    analysis_correlation(feautes_df)
