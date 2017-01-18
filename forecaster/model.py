import forecaster.forecasted_results_compare as results_compare
import configparser
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import mutual_info_regression
from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import f_regression

config = configparser.ConfigParser()
config.read('settings.cfg')
predict_year = int(config['general']['forecast_year'])

regression_config = configparser.ConfigParser()
regression_config.read('forecaster/batting_model_settings.cfg')


def get_forecasted_stats(X_train, Y_train, X_test, category, file):
    scaler = StandardScaler()

    Y_train = Y_train.values.ravel().astype(float)  # necessary to avoid warning
    X_train_std = scaler.fit_transform(X_train)
    X_test_std = scaler.transform(X_test)

    # Support Vector Regression
    forecaster_type = str(config['model']['forecaster'])
    if forecaster_type == 'standard':
        k_selected = int(regression_config[category]['K_selected'])
        c = int(regression_config[category]['C'])
        epsilon = float(regression_config[category]['epsilon'])
        gamma = float(regression_config[category]['gamma'])

        k_best = SelectKBest(mutual_info_regression, k=k_selected)
        k_best.fit_transform(X_train_std, Y_train)
        selected_features = X_test.columns[k_best.transform(np.arange(len(X_test.columns)).reshape(1, -1))]
        print(str(selected_features), file=file)
        X_train_std = k_best.transform(X_train_std)
        X_test_std = k_best.transform(X_test_std)

        svr = SVR(C=c, epsilon=epsilon, gamma=gamma)
        svr.fit(X_train_std, Y_train)
        Y_test = svr.predict(X_test_std)
        train_score = svr.score(X_train_std, Y_train)
        model = svr
    else:
        parameters = {'C': [1, 10, 100], 'gamma': [0.001, 0.01, 0.1], 'epsilon': [0.1, 1, 10]}
        k_selected = int(regression_config[category]['K_selected'])

        k_best = SelectKBest(mutual_info_regression, k=k_selected)
        k_best.fit_transform(X_train_std, Y_train)
        selected_features = X_test.columns[k_best.transform(np.arange(len(X_test.columns)).reshape(1, -1))]
        print(str(selected_features), file=file)
        X_train_std = k_best.transform(X_train_std)
        X_test_std = k_best.transform(X_test_std)

        svr = SVR()
        clf = GridSearchCV(svr, parameters, cv=5)
        clf.fit(X_train_std, Y_train)
        print(str(clf.best_estimator_), file=file)
        Y_test = clf.predict(X_test_std)
        train_score = clf.score(X_train_std, Y_train)
        model = clf

    Y_test = np.rint(Y_test)
    results_compare.min_max_mean_median_compare(Y_test, Y_train, file)
    print('Train Data Score: ' + str(train_score), file=file)

    if predict_year < 2016:
        test_score = results_compare.get_results_score_with_actuals(model, X_test_std, Y_test, category)
        print('Test Data Score: ' + str(test_score), file=file)
    return Y_test
