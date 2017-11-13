import forecaster.batting_data_preparation as batting_data
import forecaster.batting_queries as batting_queries # remove later
import forecaster.data_config as data_config
import forecaster.database_setup as database_setup
import forecaster.model as model
import forecaster.utils as utils
import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read('settings.cfg')

forecasted_batting_categories = config['model']['forecasted_batting_categories'].split(',')
standard_batting = config['model']['standard_batting']

results_directory = 'results/' #remove later
forecast_database_name = config['general']['forecast_database_name'] #remove later


def forecast_batter_stats():
    data_config.create_config_table()
    if data_config.config_values_have_changed():
        batting_data.database_preparation()
        database_setup.create_database()
        batting_data.prepare_batting_data()
        data_config.insert_values_into_config_table()
    else:
        batting_data.clear_forecasted_stats()
        batting_data.create_forecasted_tables()

    if standard_batting == 'by_age':
        X_test = batting_data.get_player_season_stats_for_test_set('standard_batting_career_by_age')
        X_train = batting_data.get_train_data_by_age()
    elif standard_batting == 'by_exp':
        X_test = batting_data.get_player_season_stats_for_test_set('standard_batting_career_by_experience')
        X_train = batting_data.get_train_data_by_experience()
    else:
        X_test = batting_data.get_player_season_stats_for_test_set('standard_batting')
        X_train = batting_data.get_train_data('x')

    Y_train_stats = batting_data.get_train_data('y')

    results = pd.DataFrame()
    # results columns need to be added before the columns are removed for forecasting the data
    results = batting_data.add_id_year_and_age_for_test_data_to_results_df(results, X_test)

    X_test = batting_data.drop_unused_columns_for_forecasting(X_test)
    X_train = batting_data.drop_unused_columns_for_forecasting(X_train)
    Y_train_stats = batting_data.drop_unused_columns_for_forecasting(Y_train_stats)

    for category in forecasted_batting_categories:
        print('Starting: ' + category)
        Y_train = Y_train_stats.copy()
        Y_train = batting_data.get_train_data_for_category(Y_train, category)
        Y_train_array = Y_train.values.ravel()

        Y_test = model.get_forecasted_stats(X_train, Y_train, X_test, category)
        results[category] = pd.Series(Y_test)
        Y_test_array = results[category].values.ravel()

    batting_data.bulk_insert_forecasted_stats(results.values)
    utils.write_results_into_csv(results)
