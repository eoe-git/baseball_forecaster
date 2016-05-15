import curve_fitting.data_preparation as data
import curve_fitting.batter_queries as batter_queries
import curve_fitting.fit as fit
import configparser

config = configparser.ConfigParser()
config.read('settings.cfg')

stat_range = range(4, 13)
database_directory = config['general']['database_directory']
database_name = config['general']['database_name']
predict_year = int(config['general']['forecast_year']) - 1


def curve_fit_batter_data(cursor):
    categories = batter_queries.get_queried_categories(cursor, predict_year)
    player_list = batter_queries.get_player_list(cursor, predict_year)
    for player_stats in player_list:
        forecasted_stats = [player_stats[categories['player_id']], player_stats[categories['year']]]
        for stat in stat_range:
            player_id = player_stats[categories['player_id']]
            plot_data = data.get_plot_data(cursor, stat, player_id)
            forecasted_result = fit.forecasted_result_for_stat(plot_data, player_stats[categories['age']])
            forecasted_stats.append(forecasted_result)
        batter_queries.insert_forecasted_stats(database_directory, database_name, forecasted_stats)
