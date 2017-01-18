ignored_stats = ['pa', 'g', 'ab']
stats_per_pa = ['h', 'double', 'triple', 'hr', 'r', 'rbi', 'bb', 'so', 'ibb', 'hbp', 'sh', 'sf', 'g_idp']
special_stats = ['sb', 'cs']


def modify_base_running_stat_to_be_per_oppertunity(x, stats):
    stats[x] = stats[x].astype(float)
    temp = stats
    for index, row in temp.iterrows():
        sb_opp = (int(row['h']) - int(row['triple']) - int(row['hr'])) + int(row['bb'])
        x_value = int(row[x])
        if sb_opp == 0:
            # x_per_y = 0
            x_per_y = 0.01  # some small number
        else:
            y_value = sb_opp
            # x_value = int(row[x])
            # x_per_y = x_value / y_value
            x_per_y = (x_value / y_value) * 600
        stats.set_value(index, x, x_per_y)
    return stats


def modify_base_running_stat_per_oppertunity_to_be_the_actual_stat(x, stats):
    temp = stats
    for index, row in temp.iterrows():
        sb_opp = (int(row['h']) - int(row['triple']) - int(row['hr'])) + int(row['bb'])
        y_value = sb_opp
        x_per_y = float(row[x])
        # x_value = x_per_y * y_value
        x_value = (x_per_y * y_value) / 600
        stats.set_value(index, x, x_value)
    stats[x] = stats[x].astype(int)
    return stats


def modify_stat_x_to_be_per_y(x, y, stats):
    stats[x] = stats[x].astype(float)
    temp = stats
    for index, row in temp.iterrows():
        x_value = int(row[x])
        y_value = int(row[y])
        # x_per_y = x_value / y_value
        x_per_y = (x_value / y_value) * 600
        stats.set_value(index, x, x_per_y)
    return stats


def modify_stat_x_per_y_to_be_x(x, y, stats):
    temp = stats
    for index, row in temp.iterrows():
        x_per_y = float(row[x])
        y_value = int(row[y])
        # x_value = x_per_y * y_value
        x_value = (x_per_y * y_value) / 600
        stats.set_value(index, x, x_value)
    stats[x] = stats[x].astype(int)
    return stats


def prepare_stats_for_predict(stats, category):
    if category in ignored_stats:
        return stats
    elif category in stats_per_pa:
        stats = modify_stat_x_to_be_per_y(category, 'pa', stats)
        return stats
    elif category in special_stats:
        stats = modify_base_running_stat_to_be_per_oppertunity(category, stats)
        return stats
    else:
        print(category + " is not a valid category")


def prepare_stats_for_forecast(stats, category):
    if category in ignored_stats:
        stats[category] = stats[category].astype(int)
        return stats
    elif category in stats_per_pa:
        stats = modify_stat_x_per_y_to_be_x(category, 'pa', stats)
        return stats
    elif category in special_stats:
        stats = modify_base_running_stat_per_oppertunity_to_be_the_actual_stat(category, stats)
        return stats
    else:
        print(category + " is not a valid category")