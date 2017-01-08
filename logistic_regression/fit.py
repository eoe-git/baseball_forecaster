from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def get_forecasted_stats(X_train, Y_train, X_test):
    scaler = StandardScaler()
    Y_train = Y_train.values.ravel()  # necessary to avoid warning

    X_train_std = scaler.fit_transform(X_train)
    X_test_std = scaler.transform(X_test)

    lr = LogisticRegression(C=1000, random_state=0)
    lr.fit(X_train_std, Y_train)
    Y_test = lr.predict(X_test_std)

    return Y_test
