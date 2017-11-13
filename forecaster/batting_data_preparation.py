import forecaster.batting_queries as batting_queries
import forecaster.data_config as data_config
import forecaster.database_setup as database_setup
import configparser
import pandas as pd
import numpy as np

config = configparser.ConfigParser()
config.read('settings.cfg')

database_directory = config['general']['database_directory']
database_name = config['general']['database_name']
forecast_database_name = config['general']['forecast_database_name']
minimum_plate_appearances = int(config['general']['minimum_plate_appearances'])
predict_year = int(config['model']['forecast_year'])
furthest_back_year = int(config['model']['furthest_back_year'])
forecasted_batting_categories = config['model']['forecasted_batting_categories'].split(',')
standard_batting = config['model']['standard_batting']

results_directory = 'results/'
data_start_year = 1955
id_year_and_age = ['playerID', 'yearID', 'age']
stat_categories_list = ['yearID', 'G', 'PA', 'AB', 'H', 'DOUBLE', 'TRIPLE', 'HR', 'R', 'RBI', 'SB', 'CS', 'BB', 'SO',
                        'IBB', 'HBP', 'SH', 'SF', 'GIDP']

non_stat_categories_by_age = ['playerID', 'birthYear', 'age']

if standard_batting == 'by_age' or standard_batting == 'by_age':
    non_stat_categories = ['playerID', 'birthYear', 'yearID', 'age']
else:
    non_stat_categories = ['playerID', 'birthYear']


def prepare_batting_data():
    player_list = get_player_list().values.tolist()
    for player in player_list:
        player = player[0]
        standard_batting_stats = get_player_season_stats_for_career(player)
        standard_batting_stats = combine_player_stats_for_year(standard_batting_stats)
        standard_batting_stats = remove_any_stats_that_dont_meet_min_pa(standard_batting_stats)

        if len(standard_batting_stats) == 0:
            continue  # cannot get predict data if sample is only 1 since current and future year are compared
        else:
            standard_career_by_age = train_data_for_career_by_age(player, standard_batting_stats, stat_categories_list)
            standard_career_by_exp = train_data_for_career_by_experience(player,
                                                                         standard_batting_stats, stat_categories_list)
            bulk_insert_standard_batting_data(standard_batting_stats.values)
            bulk_insert_standard_batting_by_age_data(standard_career_by_age)
            bulk_insert_standard_batting_by_experience_data(standard_career_by_exp)


def get_test_data_by_age():
    min_age = 16
    max_age = 50

    player_list = get_test_player_list().values.tolist()
    X_test = np.array(np.empty(((max_age - min_age + 1) * len(stat_categories_list)) + 1), dtype=object)
    for player in player_list:
        player = player[0]
        player_stats = get_player_season_stats_for_career(player)
        player_stats = combine_player_stats_for_year(player_stats)
        player_stats = remove_any_stats_that_dont_meet_min_pa(player_stats)

        if len(player_stats) != 0:
            player_test_stats = test_data_for_career_by_age(player, player_stats, stat_categories_list)
            X_test = np.vstack((X_test, player_test_stats))

    X_test = np.delete(X_test, 0, axis=0)
    return X_test


def get_test_data_by_experience():
    min_age = 16
    max_age = 50

    player_list = get_test_player_list().values.tolist()
    X_test = np.array(np.empty(((max_age - min_age + 1) * len(stat_categories_list)) + 1), dtype=object)
    for player in player_list:
        player = player[0]
        player_stats = get_player_season_stats_for_career(player)
        player_stats = combine_player_stats_for_year(player_stats)
        player_stats = remove_any_stats_that_dont_meet_min_pa(player_stats)

        if len(player_stats) != 0:
            player_test_stats = test_data_for_career_by_experience(player, player_stats, stat_categories_list)
            X_test = np.vstack((X_test, player_test_stats))

    X_test = np.delete(X_test, 0, axis=0)
    return X_test


def train_data_for_career_by_age(player, player_season_stats, stat_categories):
    min_age = 16
    max_age = 50

    player_ages = player_season_stats.age
    player_years = player_season_stats.yearID.astype('float')
    player_season_stats = drop_unused_columns_for_forecasting_by_age(player_season_stats)

    player_min_age = player_ages[0]
    pad_start = np.zeros((int(player_min_age - min_age) * len(stat_categories)))

    previous_age = player_min_age
    player_stats = np.array(np.empty((int(max_age - min_age + 1) * len(stat_categories)) + 3), dtype=object)
    player_stats_base = np.array([player, 1955, 18], dtype=object)
    player_stats_base = np.concatenate((player_stats_base, pad_start))
    for age, year, season_stat in zip(player_ages, player_years, player_season_stats.itertuples()):
        player_season_stats = player_stats_base
        player_season_stats[1] = year
        player_season_stats[2] = float(age)
        season_stat_array = np.array(season_stat[1:]).astype('float')

        if age == player_min_age:
            player_season_stats = np.concatenate((player_season_stats, season_stat_array))
        elif (age - previous_age) == 1:
            player_season_stats = np.concatenate((player_season_stats, season_stat_array))
        elif (age - previous_age) > 1:
            age_diff = int(age - previous_age)
            player_season_stats = np.concatenate((player_season_stats, np.zeros(len(stat_categories) * (age_diff - 1))))
            player_season_stats = np.concatenate((player_season_stats, season_stat_array))
        elif (age - previous_age) <= 0:
            print("Error player has two entries with the same age")

        previous_age = age
        player_stats_base = player_season_stats
        pad_end = np.zeros(int(max_age - age) * len(stat_categories))
        player_season_stats = np.concatenate((player_season_stats, pad_end))
        player_stats = np.vstack((player_stats, player_season_stats))

    # remove the first entry since it was an initialized row
    player_stats = np.delete(player_stats, 0, axis=0)
    return player_stats


def train_data_for_career_by_experience(player, player_season_stats, stat_categories):
    min_age = 16
    max_age = 50

    player_ages = player_season_stats.age
    player_years = player_season_stats.yearID.astype('float')
    player_season_stats = drop_unused_columns_for_forecasting_by_age(player_season_stats)

    player_min_age = player_ages[0]
    player_exp = player_ages - player_min_age

    previous_exp = 0
    max_exp = max_age - min_age + 1
    player_stats = np.array(np.empty(int((max_age - min_age + 1) * len(stat_categories)) + 3), dtype=object)
    player_stats_base = np.array([player, 1955, 18], dtype=object)
    for exp, age, year, season_stat in zip(player_exp, player_ages, player_years, player_season_stats.itertuples()):
        player_season_stats = player_stats_base
        player_season_stats[1] = year
        player_season_stats[2] = float(age)
        season_stat_array = np.array(season_stat[1:]).astype('float')

        if exp == 0:
            player_season_stats = np.concatenate((player_season_stats, season_stat_array))
        elif (exp - previous_exp) == 1:
            player_season_stats = np.concatenate((player_season_stats, season_stat_array))
        elif (exp - previous_exp) > 1:
            exp_diff = int(exp - previous_exp)
            player_season_stats = np.concatenate((player_season_stats, np.zeros(len(stat_categories) * (exp_diff - 1))))
            player_season_stats = np.concatenate((player_season_stats, season_stat_array))
        elif (exp - previous_exp) <= 0:
            print("Error player has two entries with the same experience")

        previous_exp = exp
        player_stats_base = player_season_stats
        pad_end = np.zeros(int(max_exp - exp - 1) * len(stat_categories))
        player_season_stats = np.concatenate((player_season_stats, pad_end))
        player_stats = np.vstack((player_stats, player_season_stats))

    # remove the first entry since it was an initialized row
    player_stats = np.delete(player_stats, 0, axis=0)
    return player_stats


def test_data_for_career_by_age(player, player_season_stats, stat_categories):
    min_age = 16
    max_age = 50

    player_ages = player_season_stats.age
    player_season_stats = drop_unused_columns_for_forecasting_by_age(player_season_stats)

    player_min_age = player_ages[0]
    player_max_age = player_ages.iloc[-1]
    pad_start = np.zeros(((player_min_age - min_age) * len(stat_categories)))

    previous_age = player_min_age
    player_stats = np.array([player], dtype=object)
    player_stats = np.concatenate((player_stats, pad_start))
    for age, season_stat in zip(player_ages, player_season_stats.itertuples()):
        season_stat_array = np.array(season_stat[1:]).astype('float')

        if age == player_min_age:
            player_stats = np.concatenate((player_stats, season_stat_array))
        elif (age - previous_age) == 1:
            player_stats = np.concatenate((player_stats, season_stat_array))
        elif (age - previous_age) > 1:
            age_diff = age - previous_age
            player_stats = np.concatenate((player_stats, np.zeros(len(stat_categories) * (age_diff - 1))))
            player_stats = np.concatenate((player_stats, season_stat_array))
        elif (age - previous_age) <= 0:
            print("Error player has two entries with the same age")

        previous_age = age

    pad_end = np.zeros((max_age - player_max_age) * len(stat_categories))
    player_stats = np.concatenate((player_stats, pad_end))
    return player_stats


def test_data_for_career_by_experience(player, player_season_stats, stat_categories):
    min_age = 16
    max_age = 50

    max_exp = max_age - min_age + 1
    player_ages = player_season_stats.age
    player_season_stats = drop_unused_columns_for_forecasting_by_age(player_season_stats)

    player_min_age = player_ages[0]
    player_exp = player_ages - player_min_age
    player_min_exp = player_exp[0]
    player_max_exp = player_exp.iloc[-1]

    previous_exp = player_min_exp
    player_stats = np.array([player], dtype=object)
    for exp, season_stat in zip(player_exp, player_season_stats.itertuples()):
        season_stat_array = np.array(season_stat[1:]).astype('float')

        if exp == player_min_exp:
            player_stats = np.concatenate((player_stats, season_stat_array))
        elif (exp - previous_exp) == 1:
            player_stats = np.concatenate((player_stats, season_stat_array))
        elif (exp - previous_exp) > 1:
            exp_diff = exp - previous_exp
            player_stats = np.concatenate((player_stats, np.zeros(len(stat_categories) * (exp_diff - 1))))
            player_stats = np.concatenate((player_stats, season_stat_array))
        elif (exp - previous_exp) <= 0:
            print("Error player has two entries with the same exp")

        previous_exp = exp

    pad_end = np.zeros((max_exp - player_max_exp - 1) * len(stat_categories))
    player_stats = np.concatenate((player_stats, pad_end))
    return player_stats


def get_index_for_rows_needed_to_be_removed_for_train_data(batting_stats):
    index = []
    player_list = pd.Series(batting_stats.playerID.ravel()).unique().tolist()
    for player in player_list:
        player_stats = batting_stats[batting_stats.playerID.isin([player])]
        if len(player_stats) == 1:
            x_index = player_stats.iloc[0].name
            y_index = player_stats.iloc[0].name
        else:
            x_index = player_stats.iloc[-1].name
            y_index = player_stats.iloc[0].name
        index.append((x_index, y_index))

    return index


def remove_rows_not_for_train_set(stats, x_or_y, index):
    for i in index:
        if x_or_y == 'x':
            stats = stats.drop(i[0])
        elif x_or_y == 'y':
            stats = stats.drop(i[1])

    return stats


def combine_player_stats_for_year(season_stats):
    cols = ['playerID', 'birthYear', 'yearID', 'age']
    season_stats = season_stats.groupby(cols, as_index=False, sort=False).sum()
    return season_stats


def remove_any_stats_that_dont_meet_min_pa(season_stats):
    temp = season_stats
    for i, season in season_stats.iterrows():
        plate_appearances = season['AB'] + season['BB'] + season['HBP'] + season['SH'] + season['SF']
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


def drop_unused_columns_for_forecasting_by_age(data):
    categories = list(data.keys())
    for i in categories:
        if i in non_stat_categories_by_age:
            data = data.drop(i, 1)
    return data


def add_id_year_and_age_for_test_data_to_results_df(temp, X_test):
    for i in id_year_and_age:
        # The year cannot be the first column added
        if i == 'yearID':
            temp[i] = predict_year
        else:
            temp[i] = pd.Series(X_test[i])
    return temp


def get_player_list():
    query = batting_queries.get_player_list(data_start_year)
    player_list = batting_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return player_list


def get_test_player_list():
    query = batting_queries.get_test_player_list(predict_year)
    player_list = batting_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return player_list


def get_players_previous_season_stats(predict_year, stats):
    # get dataframe with values for predict year - 1
    query = batting_queries.get_players_previous_season_stats(predict_year)
    player_stats = batting_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return player_stats


def get_player_season_stats_for_career(player_id):
    # might remove query from this, and just directly get it from dataframe (could be faster)
    query = batting_queries.get_player_season_stats_for_career(player_id, data_start_year)
    player_stats = batting_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return player_stats


def get_actual_forecast_year_values(player_id):
    # get dataframe with values for predict year (when they exist)
    query = batting_queries.get_actual_forecast_year_values_for_player(player_id, predict_year)
    forecast_year_stats = batting_queries.get_sql_query_results_as_dataframe(query, database_directory, database_name)
    return forecast_year_stats


def get_all_standard_batting_data_within_year_range():
    query = batting_queries.get_all_standard_batting_data_within_year_range(predict_year, furthest_back_year)
    train_data = batting_queries.get_sql_query_results_as_dataframe(query, results_directory, forecast_database_name)
    return train_data


def get_all_standard_batting_career_by_age_data_within_year_range():
    query = batting_queries.get_all_standard_batting_career_by_age_data_within_year_range(predict_year,
                                                                                          furthest_back_year)
    train_data = batting_queries.get_sql_query_results_as_dataframe(query, results_directory, forecast_database_name)
    return train_data


def get_all_standard_batting_career_by_experience_data_within_year_range():
    query = batting_queries.get_all_standard_batting_career_by_experience_data_within_year_range(predict_year,
                                                                                                 furthest_back_year)
    train_data = batting_queries.get_sql_query_results_as_dataframe(query, results_directory, forecast_database_name)
    return train_data


def get_train_data(x_or_y):
    train_stats = get_all_standard_batting_data_within_year_range()
    train_data_index = get_index_for_rows_needed_to_be_removed_for_train_data(train_stats)
    train_stats = remove_rows_not_for_train_set(train_stats, x_or_y, train_data_index)
    return train_stats


def get_train_data_by_age():
    train_stats = get_all_standard_batting_career_by_age_data_within_year_range()
    train_data_index = get_index_for_rows_needed_to_be_removed_for_train_data(train_stats)
    train_stats = remove_rows_not_for_train_set(train_stats, 'x', train_data_index)
    return train_stats


def get_train_data_by_experience():
    train_stats = get_all_standard_batting_career_by_experience_data_within_year_range()
    train_data_index = get_index_for_rows_needed_to_be_removed_for_train_data(train_stats)
    train_stats = remove_rows_not_for_train_set(train_stats, 'x', train_data_index)
    return train_stats


def get_player_season_stats_for_test_set(table_name):
    query = batting_queries.get_player_season_stats_for_test_set(table_name, predict_year)
    results = batting_queries.get_sql_query_results_as_dataframe(query, results_directory, forecast_database_name)
    return results


def create_standard_batting_database_and_table():
    query = batting_queries.create_standard_batting_table()
    batting_queries.execute_sql_query(query, results_directory, forecast_database_name)


def create_standard_batting_career_by_age_table():
    query = batting_queries.create_standard_batting_career_by_age_table(stat_categories_list)
    batting_queries.execute_sql_query(query, results_directory, forecast_database_name)


def create_standard_batting_career_by_experience_table():
    query = batting_queries.create_standard_batting_career_by_experience_table(stat_categories_list)
    batting_queries.execute_sql_query(query, results_directory, forecast_database_name)


def clear_standard_batting_data():
    query = batting_queries.clear_standard_batting_data()
    batting_queries.execute_sql_query(query, results_directory, forecast_database_name)


def clear_standard_batting_by_age_data():
    query = batting_queries.clear_standard_batting_by_age_data()
    batting_queries.execute_sql_query(query, results_directory, forecast_database_name)


def clear_standard_batting_by_experience_data():
    query = batting_queries.clear_standard_batting_by_experience_data()
    batting_queries.execute_sql_query(query, results_directory, forecast_database_name)


def bulk_insert_standard_batting_data(stats):
    query = batting_queries.insert_standard_batting_data()
    batting_queries.execute_bulk_insert_sql_query(query, stats, results_directory, forecast_database_name)


def bulk_insert_standard_batting_by_age_data(stats):
    query = batting_queries.insert_standard_batting_career_stats_by_age(stat_categories_list)
    batting_queries.execute_bulk_insert_sql_query(query, stats, results_directory, forecast_database_name)


def bulk_insert_standard_batting_by_experience_data(stats):
    query = batting_queries.insert_standard_batting_career_stats_by_experience(stat_categories_list)
    batting_queries.execute_bulk_insert_sql_query(query, stats, results_directory, forecast_database_name)


def bulk_insert_forecasted_stats(stats):
    query = batting_queries.insert_forecasted_stats(forecasted_batting_categories)
    batting_queries.execute_bulk_insert_sql_query(query, stats, results_directory, forecast_database_name)


def create_train_tables():
    create_standard_batting_database_and_table()
    create_standard_batting_career_by_age_table()
    create_standard_batting_career_by_experience_table()


def clear_all_train_data():
    clear_standard_batting_data()
    clear_standard_batting_by_age_data()
    clear_standard_batting_by_experience_data()


def create_forecasted_tables():
    query = batting_queries.create_forecasted_batting_table(forecasted_batting_categories)
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
    database_setup.clear_database()
