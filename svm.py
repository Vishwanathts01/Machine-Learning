import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
iris = load_iris()

iris.feature_names

iris.target_names

df = pd.DataFrame(iris.data,columns=iris.feature_names)
df.head()

df['target']= iris.target
df.head()

df.last_valid_index

df[df.target==2].head()

df['flower_name'] =df.target.apply(lambda x: iris.target_names[x])
df.head()

df[0:150]

df0 = df[:50]
df1 = df[50:100]
df2 = df[100:]

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline

plt.xlabel('Sepal Length')
plt.ylabel('Sepal Width')
plt.scatter(df0['sepal length (cm)'], df0['sepal width (cm)'],color="green",marker='+')
plt.scatter(df1['sepal length (cm)'], df1['sepal width (cm)'],color="blue",marker='.')
plt.scatter(df2['sepal length (cm)'], df2['sepal width (cm)'],color="Red",marker='*')

plt.xlabel('Petal Length')
plt.ylabel('Petal Width')
plt.scatter(df0['petal length (cm)'], df0['petal width (cm)'],color="green",marker='+')
plt.scatter(df1['petal length (cm)'], df1['petal width (cm)'],color="blue",marker='.')
plt.scatter(df2['petal length (cm)'], df2['petal width (cm)'],color="Red",marker='*')

from sklearn.model_selection import train_test_split

X = df.drop(['target','flower_name'], axis='columns')
y = df.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

len(X_train)
len(X_test)

from sklearn.svm import SVC
model = SVC()

model.fit(X_train, y_train)

model.score(X_test,y_test)

model.predict([[6.7,3.0,5.2,2.3]])

