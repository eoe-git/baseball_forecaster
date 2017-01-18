import logistic_regression.data_preparation as data
import logistic_regression.fit as fit
import logistic_regression.data_config as data_config
import logistic_regression.stat_prep as stat_prep
import logistic_regression.plot_data as plot_data
import logistic_regression.utils as utils
import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read('settings.cfg')

forecasted_batting_categories = config['logistic_regression']['forecasted_batting_categories'].split(',')
is_ratio_stats = False


def forecast_batter_stats():
    data_config.create_config_table()
    if data_config.config_values_have_changed():
        data.database_preparation()
        data.get_plot_data()
        data_config.insert_values_into_config_table()
    else:
        data.clear_forecasted_stats()
        data.create_forecasted_tables()

    results_folder = utils.get_results_folder_path()
    results_file = results_folder + 'Results.txt'

    X_test = data.combine_yearly_stats_and_remove_years_that_dont_meet_min_pa(data.get_players_previous_season_stats())
    X_train = data.get_train_data('x')
    Y_train_stats = data.get_train_data('y')

    temp = pd.DataFrame()
    # temp columns need to be added before the columns are removed for forecasting the data
    temp = data.add_id_year_and_age_for_test_data_to_temp_df(temp, X_test)

    X_test = data.drop_unused_columns_for_forecasting(X_test)
    X_train = data.drop_unused_columns_for_forecasting(X_train)
    Y_train_stats = data.drop_unused_columns_for_forecasting(Y_train_stats)

    # Pa needs to be the first category predicted
    if forecasted_batting_categories[0] != 'pa':
        print('ERROR, pa is not the first category in forecasting_batting_categories')

    with open(results_file, mode='wt') as myfile:
        utils.add_basic_settings_to_files(myfile)

        for category in forecasted_batting_categories:
            print('Starting: ' + category)
            print('Forecasting: ' + category, file=myfile)
            Y_train = Y_train_stats.copy()
            if is_ratio_stats:
                Y_train = stat_prep.prepare_stats_for_predict(Y_train, category)
            Y_train = data.get_train_data_for_category(Y_train, category)
            Y_train_array = Y_train.values.ravel()

            Y_test = fit.get_forecasted_stats(X_train, Y_train, X_test, category, myfile)
            temp[category] = pd.Series(Y_test)
            if is_ratio_stats:
                temp = stat_prep.prepare_stats_for_forecast(temp, category)
            Y_test_array = temp[category].values.ravel()
            plot_data.plot_data(Y_test_array, Y_train_array, category, results_folder)
            print('___________________________________________', file=myfile)

    results = temp.values
    data.bulk_insert_forecasted_stats(results)
