import forecaster.batting_queries as batting_queries
import forecaster.data_config as data_config
import configparser
import pandas as pd

config = configparser.ConfigParser()
config.read('settings.cfg')

database_directory = config['general']['database_directory']
database_name = config['general']['database_name']
forecast_database_name = config['general']['forecast_database_name']
predict_year = int(config['general']['forecast_year'])
furthest_back_year = int(config['general']['furthest_back_year'])
minimum_plate_appearances = int(config['general']['minimum_plate_appearances'])
forecasted_batting_categories = config['model']['forecasted_batting_categories'].split(',')
results_directory = 'results/'

non_stat_categories = ['player_id', 'birth_year']
id_year_and_age = ['player_id', 'year', 'age']


def get_plot_data():
    player_list = get_player_list().values.tolist()
    for player in player_list:
        player = player[0]
        player_stats = get_player_season_stats_for_career(player)
        player_stats = combine_player_stats_for_year(player_stats)
        player_stats = remove_any_stats_that_dont_meet_min_pa(player_stats)
        if len(player_stats) == 1:
            continue  # cannot get predict data if sample is only 1 since current and future year are compared
        else:
            X_train = player_stats[:-1].values
            Y_train = player_stats[1:].values
            bulk_insert_train_data(X_train, 'x_train')
            bulk_insert_train_data(Y_train, 'y_train')


def combine_player_stats_for_year(season_stats):
    cols = ['player_id', 'birth_year', 'year', 'age']
    season_stats = season_stats.groupby(cols, as_index=False, sort=False).sum()
    return season_stats


def remove_any_stats_that_dont_meet_min_pa(season_stats):
    temp = season_stats
    for i, season in season_stats.iterrows():
        plate_appearances = season['ab'] + season['bb'] + season['hbp'] + season['sh'] + season['sf']
        if plate_appearances < minimum_plate_appearances:
            temp.drop(i, inplace=True)
    temp = temp.reset_index(drop=True)
    return temp


def combine_yearly_stats_and_remove_years_that_dont_meet_min_pa(career_stats):
    career_stats = combine_player_stats_for_year(career_stats)
    career_stats_meeting_min_pa = remove_any_stats_that_dont_meet_min_pa(career_stats)
    return career_stats_meeting_min_pa


def get_train_data_for_category(Y_train, category):
    return Y_train.loc[:, [category]]


def drop_unused_columns_for_forecasting(data):
    categories = list(data.keys())
    for i in categories:
        if i in non_stat_categories:
            data = data.drop(i, 1)
    return data


def add_id_year_and_age_for_test_data_to_results_df(temp, X_test):
    for i in id_year_and_age:
        # The year cannot be the first column added
        if i == 'year':
            temp[i] = predict_year
        else:
            temp[i] = pd.Series(X_test[i])
    return temp


def get_player_list():
    query = batting_queries.get_player_list(predict_year, furthest_back_year)
    player_list = batting_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return player_list


def get_players_previous_season_stats():
    query = batting_queries.get_players_previous_season_stats(predict_year)
    player_stats = batting_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return player_stats


def get_player_season_stats_for_career(player_id):
    query = batting_queries.get_player_season_stats_for_career(player_id, predict_year, furthest_back_year)
    player_stats = batting_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return player_stats


def get_actual_forecast_year_values(player_id):
    query = batting_queries.get_actual_forecast_year_values_for_player(player_id, predict_year)
    forecast_year_stats = batting_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return forecast_year_stats


def get_train_data(x_or_y):
    query = batting_queries.get_all_data_from_batting(x_or_y)
    train_data = batting_queries.get_sql_query_results_as_dataframe(query, results_directory, forecast_database_name)
    return train_data


def create_train_database_and_table(x_or_y):
    query = batting_queries.temp_create_batting_forecast_table(x_or_y)
    batting_queries.execute_sql_query(query, results_directory, forecast_database_name)


def clear_train_data(x_or_y):
    query = batting_queries.clear_train_data(x_or_y)
    batting_queries.execute_sql_query(query, results_directory, forecast_database_name)


def bulk_insert_train_data(stats, x_or_y):
    query = batting_queries.insert_train_data(x_or_y)
    batting_queries.execute_bulk_insert_sql_query(query, stats, results_directory, forecast_database_name)


def bulk_insert_forecasted_stats(stats):
    query = batting_queries.insert_forecasted_stats(forecasted_batting_categories)
    batting_queries.execute_bulk_insert_sql_query(query, stats, results_directory, forecast_database_name)


def create_train_tables():
    create_train_database_and_table('x_train')
    create_train_database_and_table('y_train')


def clear_all_train_data():
    clear_train_data('x_train')
    clear_train_data('y_train')


def create_forecasted_tables():
    query = batting_queries.create_batting_forecast_table(forecasted_batting_categories)
    batting_queries.execute_sql_query(query, results_directory, forecast_database_name)


def clear_forecasted_stats():
    # query = batter_queries.clear_train_data()
    query = batting_queries.remove_forecast_table()
    batting_queries.execute_sql_query(query, results_directory, forecast_database_name)


def database_preparation():
    clear_forecasted_stats()
    create_forecasted_tables()
    create_train_tables()
    data_config.create_config_table()
    clear_all_train_data()
    data_config.clear_config_table()
