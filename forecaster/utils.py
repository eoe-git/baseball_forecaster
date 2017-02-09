import configparser
import os

config = configparser.ConfigParser()
config.read('settings.cfg')

forecasted_batting_categories = config['model']['forecasted_batting_categories'].split(',')
predict_year = int(config['general']['forecast_year'])
furthest_back_year = int(config['general']['furthest_back_year'])
results_directory = 'results/'


def add_basic_settings_to_files(file):
    print('Forecasting: ' + str(predict_year), file=file)
    print('Forecasted Categories: ' + ', '.join(x for x in forecasted_batting_categories), file=file)
    print('Using stats from ' + str(furthest_back_year) + ' to ' + str(predict_year - 1), file=file)
    print('___________________________________________', file=file)


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.chmod(results_directory, 0o777)
        os.makedirs(d)


def get_results_folder_path():
    new_folder_name = results_directory + str(furthest_back_year) + '_' + str(predict_year) + '/'
    results_folder = results_directory + new_folder_name
    ensure_dir(results_folder)
    return results_folder


def write_results_into_csv(results):
    csv_file_name = 'results.csv'
    csv_file_path = results_directory + csv_file_name
    results.to_csv(csv_file_path, index=False)

