import logistic_regression.data_preparation as data
import logistic_regression.fit as fit
import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read('settings.cfg')

forecasted_batting_categories = config['logistic_regression']['forecasted_batting_categories'].split(',')
stat_categories = ['ab', 'h', 'bb', 'double', 'triple', 'hr', 'r', 'rbi', 'sb']
stats_in_prediction = ['age']
name_age_and_id = ['player_id', 'year', 'age']


def curve_fit_batter_data():
    data.clear_all_train_data()
    data.clear_forecasted_stats()

    X_test = data.get_players_previous_season_stats()
    stats = data.get_player_stats()
    data.get_plot_data(stats)
    X_train = data.get_train_data('x')
    Y_train_stats = data.get_train_data('y')

    categories = list(X_test.keys())
    temp = pd.DataFrame()
    for i in categories:
        if i in name_age_and_id:
            temp[i] = pd.Series(X_test[i])
        elif i in stat_categories:
            continue
        elif i in stats_in_prediction:
            continue
        X_test = X_test.drop(i, 1)
        X_train = X_train.drop(i, 1)
        Y_train_stats = Y_train_stats.drop(i, 1)

    for category in forecasted_batting_categories:
        Y_train = data.get_train_data_for_category(Y_train_stats, category)
        Y_test = fit.get_forecasted_stats(X_train, Y_train, X_test)
        temp[category] = pd.Series(Y_test)

    for index, forecasted_stats in temp.iterrows():
        data.insert_forecasted_stats(list(forecasted_stats))
