# coding=utf-8
import pickle
from sklearn.metrics import accuracy_score, classification_report


class Trainer(object):

    def __init__(self, X_train_std, y_train, X_test_std, y_test):
        self.X_train_std = X_train_std
        self.y_train = y_train
        self.X_test_std = X_test_std
        self.y_test = y_test

    def train(self, clf, sc, name):
        clf.fit(self.X_train_std, self.y_train)
        # 分类测试集，这将返回一个测试结果的数组
        y_pred = clf.predict(self.X_test_std)

        # 计算模型在测试集上的准确性
        score = accuracy_score(self.y_test, y_pred)
        print(f"[{name}] accuracy_score: {score}")

        print("classification report:\n", classification_report(self.y_test, y_pred))

        with open(f"dump/clf_{name}.pkl", "wb+") as pkl:
            pickle.dump((clf, sc), pkl)

