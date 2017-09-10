import configparser

config = configparser.ConfigParser()
config.read('settings.cfg')

results_directory = 'results/'


def write_results_into_csv(results):
    csv_file_name = 'results.csv'
    csv_file_path = results_directory + csv_file_name
    results.to_csv(csv_file_path, index=False)

