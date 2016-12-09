import configparser
from sklearn.linear_model import LogisticRegression

config = configparser.ConfigParser()
config.read('settings.cfg')


def get_forecasted_stats(X_train, Y_train, X_test):
    Y_train = Y_train.values.ravel()  # necessary to avoid warning
    lr = LogisticRegression(C=1000, random_state=0)
    lr.fit(X_train, Y_train)
    Y_test = lr.predict(X_test)
    return Y_test
