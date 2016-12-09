import configparser
import sys
import logistic_regression.batter_queries as batter_queries

config = configparser.ConfigParser()
config.read('settings.cfg')

database_directory = config['general']['database_directory']
database_name = config['general']['database_name']
forecast_database_name = config['general']['forecast_database_name']
x_train_database_name = config['logistic_regression']['x_train_database_name']
y_train_database_name = config['logistic_regression']['y_train_database_name']
predict_year = int(config['general']['forecast_year'])
furthest_back_year = int(config['general']['furthest_back_year'])
minimum_plate_appearances = int(config['general']['minimum_plate_appearances'])


def get_plot_data():
    player_list = get_player_list().values.tolist()
    count = 0
    for player in player_list:
        player = player[0]
        if count > 3:
            break
        player_stats = get_player_season_stats_for_career(player)
        if len(player_stats) == 1:
            continue  # cannot get predict data if sample is only 1 since current and future year are compared
        else:
            for index, season_stats in player_stats[:-1].iterrows():
                insert_train_data(season_stats, 'x')
            for index, season_stats in player_stats[1:].iterrows():
                insert_train_data(season_stats, 'y')
        count += 1


def get_train_data_for_category(Y_train, category):
    return Y_train.loc[:, [category]]


def get_player_list():
    query = batter_queries.get_player_list(predict_year, furthest_back_year, minimum_plate_appearances)
    player_list = batter_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return player_list


def get_players_previous_season_stats():
    query = batter_queries.get_players_previous_season_stats(predict_year, minimum_plate_appearances)
    player_stats = batter_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return player_stats


def get_player_season_stats_for_career(player_id):
    query = batter_queries.get_player_season_stats_for_career(player_id, predict_year, furthest_back_year,
                                                              minimum_plate_appearances)
    player_stats = batter_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return player_stats


def get_train_data(x_or_y):
    query = batter_queries.get_all_data_from_batting()
    if x_or_y == 'x':
        train_data = batter_queries.get_sql_query_results_as_dataframe(query, database_directory, x_train_database_name)
    elif x_or_y == 'y':
        train_data = batter_queries.get_sql_query_results_as_dataframe(query, database_directory, y_train_database_name)
    elif x_or_y != 'x' and x_or_y != 'y':
        print('The train data is only x or y; not ' + x_or_y)
        sys.exit()
    return train_data


def create_train_database_and_table(x_or_y):
    query = batter_queries.temp_create_batting_forecast_table()
    if x_or_y == 'x':
        batter_queries.execute_sql_query(query, database_directory, x_train_database_name)
    elif x_or_y == 'y':
        batter_queries.execute_sql_query(query, database_directory, y_train_database_name)
    elif x_or_y != 'x' and x_or_y != 'y':
        print('The train data is only x or y; not ' + x_or_y)
        sys.exit()


def clear_train_data(x_or_y):
    query = batter_queries.clear_train_data()
    if x_or_y == 'x':
        batter_queries.execute_sql_query(query, database_directory, x_train_database_name)
    elif x_or_y == 'y':
        batter_queries.execute_sql_query(query, database_directory, y_train_database_name)
    elif x_or_y != 'x' and x_or_y != 'y':
        print('The train data is only x or y; not ' + x_or_y)
        sys.exit()


def insert_train_data(stats, x_or_y):
    query = batter_queries.insert_train_data()
    if x_or_y == 'x':
        batter_queries.execute_insert_sql_query(query, stats, database_directory, x_train_database_name)
    elif x_or_y == 'y':
        batter_queries.execute_insert_sql_query(query, stats, database_directory, y_train_database_name)
    elif x_or_y != 'x' and x_or_y != 'y':
        print('The train data is only x or y; not ' + x_or_y)
        sys.exit()


def insert_forecasted_stats(stats):
    query = batter_queries.insert_forecasted_stats()
    batter_queries.execute_insert_sql_query(query, stats, database_directory, forecast_database_name)


def create_train_tables():
    create_train_database_and_table('x')
    create_train_database_and_table('y')


def clear_all_train_data():
    clear_train_data('x')
    clear_train_data('y')


def create_forecasted_tables():
    query = batter_queries.create_batting_forecast_table()
    batter_queries.execute_sql_query(query, database_directory, forecast_database_name)


def clear_forecasted_stats():
    query = batter_queries.clear_train_data()
    batter_queries.execute_sql_query(query, database_directory, forecast_database_name)


def database_preparation():
    create_forecasted_tables()
    create_train_tables()
    clear_all_train_data()
    clear_forecasted_stats()
