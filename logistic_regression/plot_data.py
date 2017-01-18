import matplotlib.pyplot as plt
import configparser

config = configparser.ConfigParser()
config.read('settings.cfg')
predict_year = int(config['general']['forecast_year'])
furthest_back_year = int(config['general']['furthest_back_year'])
database_directory = config['general']['database_directory']


def plot_data(Y_train_data, Y_test_data, category, results_folder):
    plot_name = str(furthest_back_year) + '_' + str(predict_year) + '_for_' + category + '.png'
    plot_save_name = results_folder + plot_name
    plot_title = 'Stats from: ' + str(furthest_back_year) + ' - ' + str(predict_year)
    fig = plt.figure()

    ax1 = fig.add_subplot(211)
    ax1.hist(Y_train_data, 15, normed=1, facecolor='blue', alpha=0.75)
    ax1.set_title(plot_title)
    ax1.set_ylabel('Probability')
    ax1.relim()
    ax1.autoscale_view()

    ax2 = fig.add_subplot(212)
    ax2.hist(Y_test_data, 15, normed=1, facecolor='green', alpha=0.75)
    ax2.set_ylabel('Probability')
    ax2.set_xlabel(category)
    ax2.relim()
    ax2.autoscale_view()

    fig.savefig(plot_save_name, bbox_inches='tight')
    fig.clf()