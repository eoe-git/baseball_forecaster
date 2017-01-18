import numpy as np
import logistic_regression.data_preparation as data
import pandas as pd


def min_max_mean_median_compare(Y_test, Y_train, file):
    Y_test_max = np.amax(Y_test)
    Y_train_max = np.amax(Y_train)
    Y_test_min = np.amin(Y_test)
    Y_train_min = np.amin(Y_train)
    Y_test_mean = np.average(Y_test)
    Y_train_mean = np.average(Y_train)
    Y_test_median = np.median(Y_test)
    Y_train_median = np.median(Y_train)

    Y_test_results = 'Min: ' + str(Y_test_min) + ' Max: ' + str(Y_test_max) + ' Mean: ' + str(Y_test_mean) + \
                     ' Median: ' + str(Y_test_median)
    print(Y_test_results, file=file)
    Y_compare_results = 'Min: ' + str(Y_test_min - Y_train_min) + ' Max: ' + str(Y_test_max - Y_train_max) + \
                        ' Mean: ' + str(Y_test_mean - Y_train_mean) + ' Median: ' + str(Y_test_median - Y_train_median)
    print(Y_compare_results, file=file)


def get_results_score_with_actuals(model, X_test_std, Y_test, category):
    X_test = data.combine_yearly_stats_and_remove_years_that_dont_meet_min_pa(data.get_players_previous_season_stats())
    player_list = X_test['player_id']
    Y_test_actual_values = np.empty(len(player_list), dtype=int)
    Y_test_temp = Y_test.copy()
    i = 0
    count = 0
    for player in player_list:
        player_actual_values = data.get_actual_forecast_year_values(player)
        if len(player_actual_values) == 0:
            Y_test_temp = np.delete(Y_test_temp, i, axis=0)
            Y_test_actual_values = np.delete(Y_test_actual_values, i, axis=0)
            X_test_std = np.delete(X_test_std, i, axis=0)
            count += 1
            continue  # since the index is based on the number of rows do not move if one of the rows is removed
        else:
            player_actual_values = data.combine_player_stats_for_year(player_actual_values)
            player_actual_values = data.remove_any_stats_that_dont_meet_min_pa(player_actual_values)
            # Remove any values that are ignored due to min pa, even if they have stats
            if len(player_actual_values) == 0:
                Y_test_temp = np.delete(Y_test_temp, i, axis=0)
                Y_test_actual_values = np.delete(Y_test_actual_values, i, axis=0)
                X_test_std = np.delete(X_test_std, i, axis=0)
                count += 1
                continue  # since the index is based on the number of rows do not move if one of the rows is removed
            else:
                Y_test_actual_values[i] = player_actual_values[category].values[0]
        i += 1
    test_accuracy = model.score(X_test_std, Y_test_actual_values)
    return test_accuracy


