# -*- coding: utf-8 -*-
"""Diamond_Predictive_Analytics.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lZpD9Hv0gUx9MZeQsVcmK3VtTGy1LaVX

# DESCRIPTION

A dataset containing the prices and other attributes of almost 54,000 diamonds. The variables are as follows:

**Content**

**price** price in US dollars (\$326--\$18,823)

**carat** weight of the diamond (0.2--5.01)

**cut** quality of the cut (Fair, Good, Very Good, Premium, Ideal)

**color** diamond colour, from J (worst) to D (best)

**clarity** a measurement of how clear the diamond is (I1 (worst), SI2, SI1, VS2, VS1, VVS2, VVS1, IF (best))

**x** length in mm (0--10.74)

**y** width in mm (0--58.9)

**z** depth in mm (0--31.8)

**depth** total depth percentage = z / mean(x, y) = 2 * z / (x + y) (43--79)

**table** width of top of diamond relative to widest point (43--95)

[ggplot2 packages](https://ggplot2.tidyverse.org/reference/diamonds.html)

Dataset: [Diamond - Repository GitHub ggplot](https://github.com/tidyverse/ggplot2/tree/main/data-raw)

# BUSINESS UNDERSTANDING

The aim of this problem is to predict the ***price*** of diamonds. Predictions will be used to determine what the appropriate purchase price is for diamonds with ***certain characteristics*** so that the company can make as much profit as possible.

# DATA PREPARATION

## Libraries
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor

# %matplotlib inline

"""## Load Dataset"""

url = 'https://raw.githubusercontent.com/tidyverse/ggplot2/main/data-raw/diamonds.csv'
diamonds = pd.read_csv(url)
diamonds

diamonds.info()

diamonds.describe()

"""Dimensions x, y, or z with a value of 0 are invalid data or missing values.

## Handling Missing Value
"""

x = (diamonds.x == 0).sum()
y = (diamonds.y == 0).sum()
z = (diamonds.z == 0).sum()

print('Value 0 in column x exists:', x)
print('Value 0 in column y exists', y)
print('Value 0 in column z exists', z)

diamonds.loc[(diamonds['z']==0)]

"""All data has a value of 0 on the x and y dimensions also has a value of 0 on the z dimension"""

# Drop rows with values 'x', 'y' and 'z' = 0
diamonds = diamonds.loc[(diamonds[['x', 'y', 'z']]!=0).all(axis=1)]

# Check the data size to make sure the row has been dropped
diamonds.shape

diamonds.describe()

"""## Handling Outliers

Visualize Diamonds data with a boxplot to detect outliers
"""

sns.boxplot(x=diamonds['carat'])

sns.boxplot(x=diamonds['table'])

sns.boxplot(x=diamonds['x'])

sns.boxplot(x=diamonds['depth'])

"""## IQR (Inter Quartile Range) method"""

Q1 = diamonds.quantile(0.25)
Q3 = diamonds.quantile(0.75)
IQR = Q3-Q1

diamonds = diamonds[~((diamonds<(Q1-1.5*IQR)) | (diamonds>(Q3+1.5*IQR))).any(axis=1)]

"""The dataset is now clean and has 47,524 samples."""

diamonds.shape

sns.boxplot(x=diamonds['table'])

"""## Univariate EDA(Exploratory Data Analysis)

Dividing the dataset into two parts, namely numerical features and categorical features
"""

numerical_features = ['carat', 'depth', 'price', 'table', 'x', 'y', 'z']
categorical_features = ['cut', 'color', 'clarity']

"""### Categorical Features

#### Cut Features
"""

feature = categorical_features[0]
count = diamonds[feature].value_counts()
percent = 100*diamonds[feature].value_counts(normalize=True)

df = pd.DataFrame({'number of samples':count, 'percentages':percent.round(1)})
print(df)

count.plot(kind='bar', title=feature);

"""There are 5 categories in the Cut feature, sequentially from the most in number, namely: Ideal, Premium, Very Good, Good, and Fair. It can be concluded that more than 60% of the samples are high grade type diamonds, namely Ideal and Premium grades.

#### Color Features
"""

feature = categorical_features[1]
count = diamonds[feature].value_counts()
percent = 100*diamonds[feature].value_counts(normalize=True)

df = pd.DataFrame({'number of samples':count, 'percentages':percent.round(1)})
print(df)

count.plot(kind='bar', title=feature)
plt.xticks(rotation=0);

"""The order of the color categories from the worst to the best is J, I, H, G, F, E, and D. From the graph above, we can conclude that most of the grades are in the middle grade, namely G, F and H.

#### Clarity Features
"""

feature = categorical_features[2]
count = diamonds[feature].value_counts()
percent = 100*diamonds[feature].value_counts(normalize=True)

df = pd.DataFrame({'number of values':count, 'percentages':percent.round(1)})
print(df)

count.plot(kind='bar', title=feature);
plt.xticks(rotation=0);

"""Based on information from the variable descriptions, the Clarity feature consists of 8 categories from the worst to the best, namely: I1, SI2, SI1, VS2, VS1, VVS2, VVS1, and IF.

1. 'IF' - Internally Flawless
2. 'VVS2' - Very Very Slight Inclusions
3. 'VVS1' - Very Very Slight Inclusions
4. 'VS1' - Very Slight Inclusions
5. 'VS2' - Very Slight Inclusions
6. 'SI2' - Slight Inclusions
7. 'SI1' - Slight Inclusions
8. 'I1' - Imperfect

From the graph, we can conclude that most of the features are of low grade, namely SI1, SI2, and VS2.

### Numerical Features
"""

diamonds.hist(bins=50, figsize=(20, 15));

"""Khususnya histogram untuk variabel "price" yang merupakan fitur target (label) pada data tersbut. Dari histogram "price", kita bisa memperoleh beberapa informasi, antara lain:

* Peningkatan harga diamonds sebanding dengan penurunan jumlah sampel. Hal ini dapat kita lihat jelas dari histogram "price" yang grafiknya mengalami penurunan seiring dengan semakin banyaknya jumlah sampel (sumbu x).
* Rentang harga diamonds cukup tinggi yaitu dari skala ratusan dolar Amerika hingga sekitar $11800.

* Setengah harga berlian bernilai di bawah $2500.
* Distribusi harga miring ke kanan (right-skewed). Hal ini akan berimplikasi pada model.

## Multivariate EDA(Exploratory Data Analysis)

### Categorical Features

Check the average price for each feature to determine the effect of category features on price.
"""

cat_feature = diamonds.select_dtypes(include='object').columns.to_list()

for col in cat_feature:
  sns.catplot(data=diamonds, x=col, y='price', kind='bar',
              dodge=False, height=4, aspect=3, palette='Set3')
  plt.title("Average 'price' Relative to - {}".format(col))

"""By observing the average price relative to the above category features, we gain the following insights:


*   In the 'cut' feature, the average price tends to be similar. The range is between 3500 - 4500. The highest grade, namely the ideal grade, has the lowest average price among the other grades. Thus, the cut feature has little influence or impact on the average price.
*   In the 'color' feature, the lower the color grade, the higher the price of diamonds. From this, it can be concluded that color has a low effect on price.


*   In the 'clarity' feature, in general, diamonds with lower grades have higher prices. This means that the "clarity" feature has a low impact on price.
*   In conclusion, category features have a low effect on price.

### Numerical Features
"""

# Observing the relationship between numeric features with the pairplot() function
sns.pairplot(diamonds, diag_kind='kde')

"""In the previous pairplot chart data distribution pattern, it can be seen that 'carat', 'x', 'y', and 'z' have a high correlation with the "price" feature. While the other two features, namely 'depth' and 'table', seem to have a weak correlation because their distribution does not form a pattern.

To evaluate the correlation score, use the corr() function.
"""

plt.figure(figsize=(10, 8))
correlation_matrix = diamonds.corr().round(2)

# To print the value in the box, use the parameter annot=True
sns.heatmap(data=correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Matrix for Numeric Features', size=20)

"""The 'carat', 'x, 'y', and 'z' features have large correlation scores (above 0.9) with the 'price' target feature. That is, the 'price' feature is highly correlated with the four features. Meanwhile, the 'depth' feature has a very small correlation (0.01). So, this feature can be dropped."""

diamonds.drop(['depth'], inplace=True, axis=1)
diamonds.head()

"""# DATA PREPARATION 2

## Category Feature Encoding
"""

diamonds = pd.concat([diamonds, pd.get_dummies(diamonds['cut'],
                                               prefix='cut')], axis=1)
diamonds = pd.concat([diamonds, pd.get_dummies(diamonds['color'],
                                               prefix='color')], axis=1)
diamonds = pd.concat([diamonds, pd.get_dummies(diamonds['clarity'],
                                               prefix='clarity')], axis=1)

diamonds.drop(['cut', 'color', 'clarity'], axis=1, inplace=True)
diamonds.head()

diamonds.info()

"""## Dimension reduction with PCA(Principal Component Analysis)"""

sns.pairplot(diamonds[['x', 'y', 'z']], plot_kws={'s': 3});

"""The three diamond-size features in the 'x', 'y', and 'z' columns have a high correlation. This is because these three features have the same information."""

pca = PCA(n_components=3, random_state=123)
pca.fit(diamonds[['x', 'y', 'z']])
princ_comp = pca.transform(diamonds[['x', 'y', 'z']])
print(princ_comp)

pca.explained_variance_ratio_.round(3)

# Created a new feature named 'dimension' to replace features 'x', 'y', and 'z'.
pca = PCA(n_components=1, random_state=123)
pca.fit(diamonds[['x', 'y', 'z']])
diamonds['dimension'] = pca.transform(diamonds.loc[:, ('x', 'y', 'z')]).flatten()
diamonds.drop(['x', 'y', 'z'], axis=1, inplace=True)

diamonds.head()

"""## Train-Test-Split"""

X = diamonds.drop(['price'], axis=1)
y = diamonds['price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=123)

print(f'Total # of sample in whole dataset: {len(X)}')
print(f'Total # of sample in train dataset: {len(X_train)}')
print(f'Total # of sample in test dataset: {len(X_test)}')

"""## Standardization"""

numerical_features = ['carat', 'table', 'dimension']
scaler = StandardScaler()
scaler.fit(X_train[numerical_features])
X_train[numerical_features] = scaler.transform(X_train.loc[:, numerical_features])
X_train[numerical_features].head()

X_train[numerical_features].describe().round(4)

"""Now the mean = 0 and the standard deviation = 1.

# MODEL DEVELOPMENT

Develop a machine learning model with three algorithms. Then, it will evaluate the performance of each algorithm and determine which algorithm gives the best predictive results. The three algorithms that will be used include:


1.   K-Nearest Neighbor
2.   Random Forest

1.   Boosting Algorithm
"""

models = pd.DataFrame(index=['train_mse', 'test_mse'],
                      columns=['KNN', 'RandomForest', 'Boosting'])

"""## K-Nearest Neighbor"""

knn = KNeighborsRegressor(n_neighbors=10)
knn.fit(X_train, y_train)

models.loc['train_mse', 'KNN'] = mean_squared_error(y_pred=knn.predict(X_train),
                                                    y_true=y_train)

"""## Random Forest"""

RF = RandomForestRegressor(n_estimators=50, max_depth=16, random_state=55, n_jobs=-1)
RF.fit(X_train, y_train)

models.loc['train_mse', 'RandomForest'] = mean_squared_error(y_pred=RF.predict(X_train),
                                                             y_true=y_train)

"""## Boosting Algorithm"""

boosting = AdaBoostRegressor(learning_rate=0.05, random_state=55)
boosting.fit(X_train, y_train)
models.loc['train_mse', 'Boosting'] = mean_squared_error(y_pred=boosting.predict(X_train),
                                                         y_true=y_train)

"""## Model Evaluation"""

# Scaling the numeric features in X_test so that it has means = 0 and variances = 1.
X_test.loc[:, numerical_features] = scaler.transform(X_test[numerical_features])

mse = pd.DataFrame(columns=['train', 'test'], index=['KNN', 'RF', 'Boosting'])

model_dict = {'KNN': knn, 'RF': RF, 'Boosting':boosting}

# Calculating the Mean Squared Error of each algorithm on the train and test data.
# 1e3 aims to have the MSE value on a scale that is not too large.
for name, model in model_dict.items():
  print('name:', name)
  print('model:', model)
  mse.loc[name, 'train'] = mean_squared_error(y_true=y_train, y_pred=model.predict(X_train))/1e3
  mse.loc[name, 'test'] = mean_squared_error(y_true=y_test, y_pred=model.predict(X_test))/1e3

mse

fig, ax = plt.subplots()
mse.sort_values(by='test', ascending=False).plot(kind='barh', ax=ax, zorder=3)
ax.grid(zorder=0)

"""The Random Forest (RF) model gives the smallest error value. While the model with the Boosting algorithm has the biggest error."""

prediction = X_test.iloc[:2].copy()
prediction

pred_dict = {'y_true': y_test[:2]}
pred_dict

for name, model in model_dict.items():
  pred_dict['prediction_'+ name] = model.predict(prediction).round(1)

pd.DataFrame(pred_dict)

"""It can be seen that the prediction with Random Forest (RF) gives the closest result."""