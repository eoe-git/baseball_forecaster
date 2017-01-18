import configparser
import os

config = configparser.ConfigParser()
config.read('settings.cfg')

forecasted_batting_categories = config['logistic_regression']['forecasted_batting_categories'].split(',')
predict_year = int(config['general']['forecast_year'])
furthest_back_year = int(config['general']['furthest_back_year'])
database_directory = config['general']['database_directory']


def add_basic_settings_to_files(file):
    print('Forecasting: ' + str(predict_year), file=file)
    print('Forecasted Categories: ' + ', '.join(x for x in forecasted_batting_categories), file=file)
    print('Using stats from ' + str(furthest_back_year) + ' to ' + str(predict_year - 1), file=file)
    print('___________________________________________', file=file)


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.chmod(database_directory + 'Plotting/', 0o777)
        os.makedirs(d)


def get_results_folder_path():
    new_folder_name = 'Plotting/' + str(furthest_back_year) + '_' + str(predict_year) + '/'
    results_folder = database_directory + new_folder_name
    ensure_dir(results_folder)
    return results_folder
