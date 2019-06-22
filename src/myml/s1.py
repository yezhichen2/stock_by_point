# coding=utf-8

## 利用sklearn载入iris数据集并利用感知机进行分类(三个类别)

import sklearn
from sklearn import datasets
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.svm import SVC
from sklearn.linear_model import Perceptron

#加载iris数据集
#iris数据集为一个用于识别鸢尾花的机器学习数据集
#通过四种特征(花瓣长度,花瓣宽度,花萼长度,花萼宽度)来实现三种鸢尾花的类别划分
iris = datasets.load_iris()

#iris.data大小为150*4,代表4种特征
#这里只提取后两类特征
X = iris.data[:,[2,3]]

#标签
y = iris.target

#划分训练集和测试集
#random_state = 0表示不设定随机数种子,每一次产生的随机数不一样
X_train,X_test,y_train,y_test = train_test_split(X, y, test_size = 0.3, random_state = 0)

# 为了追求机器学习和最优化算法的最佳性能，我们将特征缩放
from sklearn.preprocessing import StandardScaler

sc = StandardScaler()

sc.fit(X_train) # 估算每个特征的平均值和标准差

# 查看特征的平均值，由于Iris我们只用了两个特征，结果是array([ 3.82857143,  1.22666667])
sc.mean_

# 查看特征的标准差，结果是array([ 1.79595918,  0.77769705])
sc.scale_

#标准化训练集
X_train_std = sc.transform(X_train)

# 注意：这里我们要用同样的参数来标准化测试集，使得测试集和训练集之间有可比性
X_test_std = sc.transform(X_test)

# 训练感知机模型

# n_iter：可以理解成梯度下降中迭代的次数
# eta0：可以理解成梯度下降中的学习率
# random_state：设置随机种子的，为了每次迭代都有相同的训练集顺序
# ppn = Perceptron(eta0=1, random_state=0)
ppn = SVC()

ppn.fit(X_train_std, y_train)

# 分类测试集，这将返回一个测试结果的数组
y_pred = ppn.predict(X_test_std)

# 计算模型在测试集上的准确性
print(accuracy_score(y_test, y_pred))

print("classification report:\n", classification_report(y_test, y_pred))
