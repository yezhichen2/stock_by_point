# coding=utf-8
import datetime
import time
import pickle
from concurrent.futures import ProcessPoolExecutor
import gen_k_data as gkd
from myselect.buy_sale import BuySelector, SaleSelector
from myselect.ml_clf import zonghei_yc
from myutils import MyFiles2


pool = ProcessPoolExecutor(max_workers=8)


class Rec(object):
    def __init__(self):
        pass


class Counter(object):

    def __init__(self, group=""):
        self.group = group
        self.count = 0
        self.success_count = 0
        self.p_change_sum = 0

        self.data = []
        self.child = []

    def tack(self, name, b_close, s_close, by_date, sale_date, true_count=0):
        p_change = (s_close - b_close) / b_close * 100

        if abs(p_change) > 30: return

        rec = Rec()

        rec.by_date = by_date
        rec.p_change = p_change

        self.data.append(rec)

        self.count += 1

        if p_change > 0:
            self.success_count += 1

        self.p_change_sum += p_change

        if p_change > -5000:
            print(f"[{name}] [{by_date} - {sale_date}] [{p_change:.3f}] [{true_count}]")

    def append(self, child):

        self.count += child.count
        self.success_count += child.success_count
        self.p_change_sum += child.p_change_sum

        self.child.append(child)

    def print_info(self):
        print("#" * 20, f"Counter Info for {self.group}",  "#" * 20)
        success_rate = self.success_count * 1.0 / (self.count or 1) * 100
        p_change_avg = self.p_change_sum / (self.count or 1)

        print(f"count = {self.count}")

        print(f"p_change_avg = {p_change_avg: .2f} %")
        print(f"success rate = {success_rate: .2f} %")


def get_close(dt, df30):

    close = df30[df30.index == dt].head(1)['close'].values[0]
    return close


def run_counter(name):

    df30 = gkd.read_min30_data(name)
    df30 = df30[df30.index >= datetime.datetime.strptime(f"2018-01-01", "%Y-%m-%d")]
    df60 = gkd.Generator.generate_k_data(base_df=df30, ktype="60")

    sale_s1 = SaleSelector.select_x004(df60)
    sale_s1 = sale_s1[sale_s1['selected'] == True]

    counter = Counter(name)

    for by_date in BuySelector.search(df30):

        flag = zonghei_yc(name, df30, by_date)
        if not flag: continue

        min_sale_dt = SaleSelector.gen_next_date(by_date)
        sale_date = SaleSelector.find_sale_point(min_sale_dt, sale_s1)

        if sale_date:
            b_close = get_close(by_date, df30)
            s_close = get_close(sale_date, df60)

            counter.tack(name, b_close, s_close, by_date, sale_date, true_count=0)

    counter.print_info()
    return counter


def run_total_count():

    process_count = 0
    total_counter = Counter("Total")
    all_names = list(MyFiles2.list_train_names())[0:]

    def _mk_params():
        for name in all_names:
            yield name

    for counter in pool.map(run_counter, _mk_params()):
        total_counter.append(counter)
        process_count += 1
        print(f"process in {process_count/len(all_names) * 100:.2f} %")

    print("\n\n")
    total_counter.print_info()

    # with open("dump/total_counter.dp", "wb+") as dp:
    #     pickle.dump(total_counter, dp)


if __name__ == '__main__':
    run_total_count()
