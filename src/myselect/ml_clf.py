# coding=utf-8
import pickle


def get_x_test(name, base_df, buy_date):
    from myfeatures import feature2 as fe2

    fc = fe2.mk_fc(name, buy_date=buy_date, p_change=0, base_df=base_df)
    if not fc:
        return None

    fc_list = [fc]

    feaute_df = fe2.create_feature_df(fc_list, to_label_func=fe2.p_change_to_label)

    if feaute_df.empty:
        return None

    del feaute_df['label']
    del feaute_df['p_change']

    x_test = feaute_df.values

    return x_test


def ml_predict(clf, sc, x_test):

    X_test_std = sc.transform(x_test)

    y_pred = clf.predict(X_test_std)

    if int(y_pred.tolist()[0]) == 1:
        return 1

    return 0


def high_ml_predict(clf, sc, x_test):

    X_test_std = sc.transform(x_test)

    y_pred = clf.predict(X_test_std)

    p = int(y_pred.tolist()[0])
    if p == 1: return 3
    if p == 2: return 2

    return 0

def load_big_mls():

    clf_names = ['knn', 'svc_rbf', 'svc_linear', 'GaussianNB', 'random_forest', 'MLP']
    for name in clf_names:
        with open(f"dump/clf_big_{name}.pkl", "rb") as pkl:
            yield pickle.load(pkl)


def load_common_mls():

    clf_names = ['knn', 'dec_tree', 'perceptron', 'svc_rbf', 'svc_linear', 'random_forest', 'MLP']
    for name in clf_names:
        with open(f"dump/clf_common_{name}.pkl", "rb") as pkl:
            yield pickle.load(pkl)


def load_high_mls():

    clf_names = ['knn', 'dec_tree', 'svc_rbf', 'svc_linear', 'random_forest', 'MLP']
    for name in clf_names:
        with open(f"dump/clf_high_{name}.pkl", "rb") as pkl:
            yield pickle.load(pkl)


big_mls = list(load_big_mls())
common_mls = list(load_common_mls())
high_mls = list(load_high_mls())


def zonghei_yc(name, base_df, by_date):

    flag = False

    x_test = get_x_test(name, base_df, by_date)
    if x_test is None:
        return flag

    big_count, common_count, high_count = 0, 0, 0

    for clf, sc in big_mls:
        big_count += ml_predict(clf, sc, x_test)

    if big_count <= 3:
        return False

    for clf, sc in common_mls:
        common_count += ml_predict(clf, sc, x_test)

    if common_count <= 4:
        return False

    for clf, sc in high_mls:
        high_count += high_ml_predict(clf, sc, x_test)

    if high_count < 3*2+2*2:
        return False

    return True


