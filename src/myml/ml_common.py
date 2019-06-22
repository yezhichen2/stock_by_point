# coding=utf-8
import pickle

from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, BaggingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.linear_model import Perceptron
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

from sklearn.model_selection import train_test_split

from myfeatures.fdata import load_fc_list
from myfeatures.feature2 import create_feature_df, p_change_to_label
from myml.ml_train import Trainer


def get_data_and_target():
    fc_list = load_fc_list()
    feautes_df = create_feature_df(fc_list, to_label_func=p_change_to_label)

    feautes_df = feautes_df[(feautes_df['label'] == 1) | (feautes_df['label'] == 2)]

    del feautes_df['p_change']

    y = feautes_df["label"].values

    del feautes_df['label']

    X = feautes_df.values

    # print(np.isnan(X).any())

    return X, y





if __name__ == '__main__':

    X, y = get_data_and_target()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.03, random_state=1)
    sc = StandardScaler()

    sc.fit(X_train)

    X_train_std = sc.transform(X_train)
    X_test_std = sc.transform(X_test)

    print("Sample size:", len(y))

    classifier_map = {
        "knn": KNeighborsClassifier(n_neighbors=60, n_jobs=4),
        "dec_tree": DecisionTreeClassifier(max_depth=8),
        "perceptron": AdaBoostClassifier(Perceptron(max_iter=2200), n_estimators=120, algorithm='SAMME'),
        "svc_rbf": SVC(kernel="rbf", C=0.8),
        "svc_linear": SVC(kernel="linear", C=0.025),
        "GaussianNB": GaussianNB(),
        "random_forest": RandomForestClassifier(max_depth=9, n_estimators=120, max_features=40),
        "MLP": MLPClassifier(alpha=1, max_iter=1000),
        "AdaBoost": AdaBoostClassifier(DecisionTreeClassifier(max_depth=10), n_estimators=60),
    }

    for name, clf in classifier_map.items():
        Trainer(X_train_std, y_train, X_test_std, y_test).train(clf, sc, f'common_{name}')


