# coding=utf-8
import pandas as pd
import matplotlib.pyplot as plt
import gen_k_data as gkd
from zibiao import ZB

if __name__ == '__main2__':
    pd.set_option("display.max_columns", 500)

    df = gkd.read_5min_data('files/SH#600280.txt')
    df = df.tail(2000)
    df = df.head(1000)

    df_d = gkd.generate_k_data(df, ktype="30")

    df_kdj = ZB.kdj(df_d)
    df_mdi = ZB.mdi(df_d)

    xx_df = pd.concat([df_kdj, df_mdi], axis=1)

    xx_df = xx_df.reset_index(drop=True)

    diff1 = xx_df['kdj_k'] - xx_df['kdj_d']
    xx_df["diff1"] = diff1.ewm(com=3).mean()

    diff2 = xx_df['PDI'] - xx_df['MDI']
    xx_df["diff2"] = diff2.ewm(com=3).mean()

    del xx_df["PDI"]
    del xx_df["MDI"]
    del xx_df["ADX"]
    del xx_df["ADXR"]


    #---------------------------------
    # df_d2 = gkd.generate_k_data(df, ktype="60")
    # df_kdj2 = ZB.kdj(df_d2)
    #
    # # df_kdj = df_kdj.tail(120)
    # df_kdj2 = df_kdj2.reset_index(drop=True)
    # diff = df_kdj2['kdj_k'] - df_kdj2['kdj_d']
    # df_kdj2["diff"] = diff.ewm(com=2).mean()
    #
    # df_kdj2['zz'] = 0
    #

    # ---------------------------------------
    plt.figure()

    xx_df.plot(grid=True)
    #df_kdj2.plot()
    plt.show()


if __name__ == '__main__':
    pd.set_option("display.max_columns", 500)

    df = gkd.read_5min_data('files/SH#600280.txt')
    df = df.tail(3000)
    df = df.head(2000)

    df_d = gkd.generate_k_data(df, ktype="60")

    mdi_df = ZB.mdi(df_d)

    mdi_df = mdi_df.reset_index(drop=True)

    mdi_df = mdi_df.ix[:, ["PDI", "MDI", "ADX", "ADXR", "DIFF"]]

    plt.figure()

    mdi_df.plot(grid=True)
    #df_kdj2.plot()
    plt.show()

