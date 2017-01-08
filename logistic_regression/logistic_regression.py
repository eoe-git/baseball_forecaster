import logistic_regression.data_preparation as data
import logistic_regression.fit as fit
import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read('settings.cfg')

forecasted_batting_categories = config['logistic_regression']['forecasted_batting_categories'].split(',')


def forecast_batter_stats():
    data.database_preparation()

    X_test = data.get_players_previous_season_stats()
    data.get_plot_data()
    X_train = data.get_train_data('x')
    Y_train_stats = data.get_train_data('y')

    temp = pd.DataFrame()
    # temp columns need to be added before the columns are removed for forecasting the data
    temp = data.add_id_year_and_age_for_test_data_to_temp_df(temp, X_test)

    X_test = data.drop_unused_columns_for_forecasting(X_test)
    X_train = data.drop_unused_columns_for_forecasting(X_train)
    Y_train_stats = data.drop_unused_columns_for_forecasting(Y_train_stats)

    for category in forecasted_batting_categories:
        Y_train = data.get_train_data_for_category(Y_train_stats, category)
        Y_test = fit.get_forecasted_stats(X_train, Y_train, X_test)
        temp[category] = pd.Series(Y_test)

    results = temp.values
    data.bulk_insert_forecasted_stats(results)
