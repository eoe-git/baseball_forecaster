import configparser
import curve_fitting.curve_fitting as curve_fitting
import logistic_regression.logistic_regression as logistic_regression

config = configparser.ConfigParser()
config.read('settings.cfg')

database_directory = config['general']['database_directory']
database_name = config['general']['database_name']

logistic_regression.curve_fit_batter_data()
