import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, make_scorer
import datetime as dt


feature_df = pd.read_csv('features.csv')
#print feature_df.describe()

store_df = pd.read_csv('stores.csv')
#print store_df.describe()

train_df = pd.read_csv('train.csv')
#print train_df.describe()
#print train_df.head()

test_df = pd.read_csv('test.csv')
#print test_df.head()

#Mapping data for building training data
new_df = pd.merge(train_df, store_df, on='Store', how='left')
#print new_df.head()
#print new_df.describe()

new2_df = pd.merge(new_df, feature_df, on=('Store','Date'), how='left')
#print new2_df.describe()

new2_df['Date'] = pd.to_datetime(new2_df['Date'])
#print new2_df['Date'].head()
new2_df['Date']= new2_df['Date'].map(dt.datetime.toordinal)

#print new2_df.head()

#print(pd.get_dummies(new2_df["Type"].head()))
dummies = pd.get_dummies(new2_df['Type'], prefix = 'Type')
new2_df = pd.concat([new2_df, dummies], axis =1)
new2_df.drop(['Type'], axis =1, inplace = True)
#print new2_df.head()


row_ids = new2_df[new2_df["IsHoliday_x"] != new2_df.IsHoliday_y].index
print row_ids
new2_df.drop(['IsHoliday_y'], axis =1, inplace = True)
new2_df = new2_df.rename(columns = {'IsHoliday_x':'IsHoliday'})

dummies = pd.get_dummies(new2_df['IsHoliday'], prefix = 'IsHoliday')
new2_df = pd.concat([new2_df, dummies], axis =1)
new2_df.drop(['IsHoliday'], axis =1, inplace = True)
new2_df.drop(['Store'], axis =1, inplace = True)
#print new2_df.head()

y = new2_df.pop('Sales')

X_train, X_test, y_train, y_test = train_test_split(new2_df, y, test_size = 0.3, random_state = 0)


# Define error measure for official scoring : RMSE
scorer = make_scorer(mean_squared_error, greater_is_better = False)

def rmse_cv_train(model):
    rmse= np.sqrt(-cross_val_score(model, X_train, y_train, scoring = scorer, cv = 10))
    return(rmse)

def rmse_cv_test(model):
    rmse= np.sqrt(-cross_val_score(model, X_test, y_test, scoring = scorer, cv = 10))
    return(rmse)

# Linear Regression
lr = LinearRegression()
lr.fit(X_train, y_train)

# Look at predictions on training and validation set
print("RMSE on Training set :", rmse_cv_train(lr).mean())
print("RMSE on Test set :", rmse_cv_test(lr).mean())
y_train_pred = lr.predict(X_train)
y_test_pred = lr.predict(X_test)

#Creating test data
newtest_df = pd.merge(test_df, store_df, on='Store', how='left')
#print newtest_df.head()
#print newtest_df.describe()

newtest_df = pd.merge(newtest_df, feature_df, on=('Store','Date'), how='left')
#print newtest_df.describe()


newtest_df['Date'] = pd.to_datetime(newtest_df['Date'])
#print new2_df['Date'].head()
newtest_df['Date']= newtest_df['Date'].map(dt.datetime.toordinal)

#print newtest_df.head()

#print(pd.get_dummies(newtest_df["Type"].head()))
dummies = pd.get_dummies(newtest_df['Type'], prefix = 'Type')
newtest_df = pd.concat([newtest_df, dummies], axis =1)
newtest_df.drop(['Type'], axis =1, inplace = True)
#print newtest_df.head()

newtest_df.drop(['IsHoliday_y'], axis =1, inplace = True)
newtest_df = newtest_df.rename(columns = {'IsHoliday_x':'IsHoliday'})

dummies = pd.get_dummies(newtest_df['IsHoliday'], prefix = 'IsHoliday')
newtest_df = pd.concat([newtest_df, dummies], axis =1)
newtest_df.drop(['IsHoliday'], axis =1, inplace = True)
newtest_df.drop(['Store'], axis =1, inplace = True)
#print newtest_df.head()

newtest_df.pop('SalesForecast')


SalesForecast_pred = lr.predict(newtest_df)
df12 = pd.DataFrame(SalesForecast_pred)
#print SalesForecast_pred
test_df.pop('SalesForecast')
test_df = test_df.join(df12)
test_df = test_df.rename(columns = {'0':'SalesForecast'})

#print test_df.describe()
test_df.to_csv('final.csv')
print "saved results"
