import forecaster.batting_data_preparation as batting_data
import forecaster.data_config as data_config
import forecaster.model as model
import forecaster.plot_data as plot_data
import forecaster.utils as utils
import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read('settings.cfg')

forecasted_batting_categories = config['model']['forecasted_batting_categories'].split(',')


def forecast_batter_stats():
    data_config.create_config_table()
    if data_config.config_values_have_changed():
        batting_data.database_preparation()
        batting_data.get_plot_data()
        data_config.insert_values_into_config_table()
    else:
        batting_data.clear_forecasted_stats()
        batting_data.create_forecasted_tables()

    results_folder = utils.get_results_folder_path()
    results_file = results_folder + 'Results.txt'

    X_test = batting_data.combine_yearly_stats_and_remove_years_that_dont_meet_min_pa(
        batting_data.get_players_previous_season_stats())
    X_train = batting_data.get_train_data('x_train')
    Y_train_stats = batting_data.get_train_data('y_train')

    temp = pd.DataFrame()
    # temp columns need to be added before the columns are removed for forecasting the data
    temp = batting_data.add_id_year_and_age_for_test_data_to_temp_df(temp, X_test)

    X_test = batting_data.drop_unused_columns_for_forecasting(X_test)
    X_train = batting_data.drop_unused_columns_for_forecasting(X_train)
    Y_train_stats = batting_data.drop_unused_columns_for_forecasting(Y_train_stats)

    with open(results_file, mode='wt') as myfile:
        utils.add_basic_settings_to_files(myfile)

        for category in forecasted_batting_categories:
            print('Starting: ' + category)
            print('Forecasting: ' + category, file=myfile)
            Y_train = Y_train_stats.copy()
            Y_train = batting_data.get_train_data_for_category(Y_train, category)
            Y_train_array = Y_train.values.ravel()

            Y_test = model.get_forecasted_stats(X_train, Y_train, X_test, category, myfile)
            temp[category] = pd.Series(Y_test)
            Y_test_array = temp[category].values.ravel()
            plot_data.plot_data(Y_train_array, Y_test_array, category, results_folder)
            print('___________________________________________', file=myfile)

    results = temp.values
    batting_data.bulk_insert_forecasted_stats(results)
