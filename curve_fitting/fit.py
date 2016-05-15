import numpy as np
import configparser

config = configparser.ConfigParser()
config.read('settings.cfg')

polynomial_order = int(config['curve_fitting']['polynomial_order'])


def fit_data_into_polynomial_fit(stat_data):
    x_values = [age for (age, mean) in stat_data]
    y_values = [mean for (age, mean) in stat_data]
    x_values = np.asarray(x_values)
    y_values = np.asarray(y_values)

    fit = np.polyfit(x_values, y_values, polynomial_order)
    return fit


def forecasted_result_for_stat(stat_data, current_age):
    fit_coefficients = fit_data_into_polynomial_fit(stat_data)
    forecast = np.poly1d(fit_coefficients)
    next_years_age = current_age + 1
    return int(forecast(next_years_age))
