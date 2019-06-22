# coding=utf-8
import pickle

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, BaggingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import Perceptron, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import ExtraTreesClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from myfeatures.fdata import load_fc_list
from myfeatures.feature2 import create_feature_df


def get_data_and_target():
    fc_list = load_fc_list()
    feautes_df = create_feature_df(fc_list)

    col_names = ['p_change', 'label', 'ma_values__240__007', 'mdi_values__30__003', 'p_change_values__240__009', 'p_change_values__240__005', 'mdi_values__240__008', 'p_change_values__240__012', 'mdi_values__30__008', 'mdi_values__30__007', 'ma_values__30__007', 'vol_values__60__006', 'mdi_values__240__006', 'vol_values__240__001', 'p_change_values__30__010', 'vol_values__30__008', 'mdi_values__60__012', 'mdi_values__30__004', 'p_change_values__60__012', 'mdi_values__30__006', 'mdi_values__240__007', 'p_change_values__30__014', 'mdi_values__60__010', 'vol_values__30__006', 'vol_values__30__005', 'vol_values__30__003', 'p_change_values__60__010', 'vol_values__30__009', 'p_change_values__60__007', 'p_change_values__60__003', 'vol_values__60__008', 'vol_values__30__004', 'vol_values__60__005', 'mdi_values__30__005', 'vol_values__30__007', 'mdi_values__240__001', 'ma_values__240__001', 'p_change_values__30__001', 'vol_values__60__003', 'ma_values__240__002', 'mdi_values__240__009', 'p_change_values__60__014', 'vol_values__60__001', 'p_change_values__240__010', 'p_change_values__60__011', 'p_change_values__30__008', 'p_change_values__30__004', 'mdi_values__240__005', 'p_change_values__30__012', 'p_change_values__60__001', 'mdi_values__240__004', 'mdi_values__240__003', 'ma_values__240__008', 'vol_values__30__002', 'mdi_values__30__009', 'ma_values__60__003', 'mdi_values__240__011', 'ma_values__30__004', 'vol_values__60__002', 'ma_values__60__007', 'ma_values__240__004', 'vol_values__30__001', 'ma_values__240__005', 'ma_values__30__003', 'p_change_values__60__013', 'ma_values__60__004', 'mdi_values__60__003', 'vol_kdj_values__240__003', 'vol_values__60__004', 'mdi_values__30__011', 'p_change_values__240__011', 'vol_kdj_values__240__002', 'mdi_values__30__010', 'mdi_values__60__008', 'p_change_values__60__009', 'p_change_values__60__005', 'vol_kdj_values__240__001', 'mdi_values__30__012', 'p_change_values__240__001', 'ma_values__30__008', 'p_change_values__30__013', 'ma_values__30__005', 'p_change_values__30__011', 'mdi_values__240__002', 'mdi_values__240__010', 'ma_values__30__002', 'ma_values__60__001', 'mdi_values__60__004', 'mdi_values__240__012', 'ma_values__60__002', 'ma_values__240__003', 'p_change_values__60__002', 'p_change_values__60__006', 'ma_values__60__008', 'vol_kdj_values__60__003', 'ma_values__60__005', 'mdi_values__30__002', 'kdj_values__60__002', 'p_change_values__240__014', 'ma_values__240__006', 'p_change_values__30__002', 'p_change_values__30__006', 'mdi_values__30__001', 'p_change_values__30__007', 'p_change_values__30__003', 'p_change_values__60__004', 'p_change_values__60__008', 'vol_values__60__007', 'p_change_values__240__013', 'p_change_values__30__005', 'p_change_values__30__009', 'p_change_values__240__006', 'p_change_values__240__002', 'vol_kdj_values__60__001', 'vol_kdj_values__60__002', 'kdj_values__60__003', 'ma_values__30__001', 'mdi_values__60__006', 'ma_values__30__006', 'kdj_values__60__004', 'mdi_values__60__011', 'mdi_values__60__005', 'mdi_values__60__002', 'ma_values__60__006', 'mdi_values__60__009', 'kdj_values__240__003', 'mdi_values__60__001', 'vol_values__240__002', 'kdj_values__240__004', 'p_change_values__240__003', 'p_change_values__240__007', 'vol_values__240__009', 'p_change_values__240__004', 'p_change_values__240__008', 'kdj_values__240__002', 'vol_values__240__008', 'kdj_values__30__003', 'vol_values__60__009', 'kdj_values__30__002', 'kdj_values__30__004', 'mdi_values__60__007', 'kdj_values__240__001', 'vol_values__240__003', 'kdj_values__60__001', 'vol_values__240__004', 'kdj_values__30__001', 'vol_values__240__005', 'vol_values__240__007', 'vol_values__240__006']
    feautes_df = feautes_df.ix[:, col_names]

    del feautes_df['p_change']

    y = feautes_df["label"].values

    del feautes_df['label']

    X = feautes_df.values

    # print(np.isnan(X).any())

    return X, y


def train(clf, sc, name):
    clf.fit(X_train_std, y_train)
    # 分类测试集，这将返回一个测试结果的数组
    y_pred = clf.predict(X_test_std)

    # 计算模型在测试集上的准确性
    score = accuracy_score(y_test, y_pred)
    print(f"[{name}] accuracy_score: {score}")

    print("classification report:\n", classification_report(y_test, y_pred))

    # with open(f"dump/clf_{name}.pkl", "wb+") as pkl:
    #     pickle.dump((clf, sc), pkl)


if __name__ == '__main__':

    X, y = get_data_and_target()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1)
    sc = StandardScaler()

    sc.fit(X_train)

    X_train_std = sc.transform(X_train)
    X_test_std = sc.transform(X_test)

    print("Sample size:", len(y))

    # classifier_map = {
    #     "knn": KNeighborsClassifier(n_neighbors=50),
    #     "dec_tree": DecisionTreeClassifier(),
    #     "perceptron": Perceptron(max_iter=2000),
    #     "svc_rbf": SVC(kernel="rbf", C=0.8),
    #     "svc_linear": SVC(kernel="linear", C=0.025),
    #     "random_forest": RandomForestClassifier(max_depth=50, n_estimators=60, max_features=1),
    #     "MLP": MLPClassifier(alpha=1, max_iter=1000),
    #     "AdaBoost": AdaBoostClassifier(),
    # }

    # estimators要做决策的算法  voting='hard'少数服从多数
    # voting_clf = VotingClassifier(
    #     estimators=[
    #         ('knn', KNeighborsClassifier(n_neighbors=50)),
    #         ('svc_rbf', SVC(kernel="rbf", C=0.8)),
    #         ('dec_tree', DecisionTreeClassifier()),
    #         ("MLP", MLPClassifier(alpha=1, max_iter=1000)),
    #     ],
    #     voting='hard'
    # )


    # voting_clf = VotingClassifier(
    #     estimators=[
    #         ('knn', KNeighborsClassifier(n_neighbors=50)),
    #         ('svc_rbf', SVC(kernel="rbf", C=0.8, probability=True)),
    #         # ('dec_tree', DecisionTreeClassifier()),
    #         # ("MLP", MLPClassifier(alpha=1, max_iter=1000)),
    #     ],
    #     voting='soft'
    # )

    # n_estimators 集成几个模型  max_samples每个模型用多少样本训练 bootstrap是否放回样本
    # voting_clf = BaggingClassifier(
    #     DecisionTreeClassifier(),
    #     n_estimators=100, max_samples=500,
    #     bootstrap=False
    # )

    # voting_clf = RandomForestClassifier(max_depth=50, n_estimators=200, max_features=1)

    # voting_clf = ExtraTreesClassifier(n_estimators=200, bootstrap=True, oob_score=True, random_state=666)

    voting_clf = AdaBoostClassifier(DecisionTreeClassifier(max_depth=20), n_estimators=80)

    train(voting_clf, sc, "soft")




