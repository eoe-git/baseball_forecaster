import curve_fitting.data_preparation as data
import curve_fitting.batter_queries as batter_queries
import curve_fitting.fit as fit
import configparser
import threading
from queue import Queue

config = configparser.ConfigParser()
config.read('settings.cfg')

stat_range = range(4, 13)
database_directory = config['general']['database_directory']
database_name = config['general']['database_name']
predict_year = int(config['general']['forecast_year']) - 1
threads = int(config['general']['threads'])

lock = threading.Lock()
q = Queue()


def forecast_player_stat(player_stats, categories):
    with lock:
        forecasted_stats = [player_stats[categories['player_id']], int(player_stats[categories['year']]) + 1]
        for stat in stat_range:
            player_id = player_stats[categories['player_id']]
            plot_data = data.get_plot_data(stat, player_id)
            forecasted_result = fit.forecasted_result_for_stat(plot_data, player_stats[categories['age']])
            forecasted_stats.append(forecasted_result)
        batter_queries.insert_forecasted_stats(forecasted_stats)


def worker():
    while True:
        item = q.get()
        forecast_player_stat(item[0], item[1])
        q.task_done()


def curve_fit_batter_data():
    categories = batter_queries.get_queried_categories(predict_year)
    player_list = batter_queries.get_player_list(predict_year)

    for i in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        t.start()

    for player_stats in player_list:
        q.put((player_stats, categories))

    q.join()
