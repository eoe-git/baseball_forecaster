import operator
import configparser
import curve_fitting.batter_queries as batter_queries

config = configparser.ConfigParser()
config.read('settings.cfg')

number_of_closest_players = int(config['curve_fitting']['number_of_closest_players'])
predict_year = config['curve_fitting']['polynomial_order']
number_of_points_for_weight = int(config['curve_fitting']['number_of_points_for_weight'])
player_age_range = range(16, 51)


def get_player_first_and_last_year(player_yearly_seasonal_stats):
    first_year_age = 0
    last_year_age = 0
    is_first_year = True
    for season_stats in player_yearly_seasonal_stats:
        if is_first_year:
            is_first_year = False
            last_year_age = season_stats[3]
        first_year_age = season_stats[3]
    first_and_last_year_age = last_year_age, first_year_age
    return first_and_last_year_age


def get_dictionary_with_only_stat_for_player(player_season_stats_list, stat):
    dictionary_with_only_stat_for_player = {}
    for compare_stat_year in player_season_stats_list:
        dictionary_with_only_stat_for_player[compare_stat_year[0]] = compare_stat_year[stat]
    return dictionary_with_only_stat_for_player


def get_difference_between_player_stats(season_stats, compared_player_dictionary, stat):
    for key, value in compared_player_dictionary.items():
        compared_player_dictionary[key] = abs(value - season_stats[stat])
    sorted_dictionary = sorted(compared_player_dictionary.items(), key=operator.itemgetter(1))
    return sorted_dictionary


def get_matching_player_count(sorted_player_dictionary, group_size):
    number_of_players = len(sorted_player_dictionary)
    if number_of_players < group_size:
        return number_of_players
    else:
        return group_size


def get_closest_matching_players(sorted_player_dictionary, age):
    closest_matching_players = []
    number_of_players = get_matching_player_count(sorted_player_dictionary, number_of_closest_players)
    for x in range(0, number_of_players):
        entry = sorted_player_dictionary[x]
        matching_player_id = entry[0]
        value = age, matching_player_id
        closest_matching_players.append(value)
    return closest_matching_players


def player_has_stats_for_that_age(query_results):
    there_is_a_result = False
    try:
        test = query_results[0]
        there_is_a_result = True
    except Exception:
        pass
    return there_is_a_result


def get_distance_from_playing_career_range(first_year, last_year, tested_age):
    distance = 0
    if tested_age < first_year:
        distance = first_year - tested_age
    elif tested_age > last_year:
        distance = tested_age - last_year
    return distance


def get_weight_term(test_age, actual_age, loop_age, years_experience, players_matched, maximum_matches, distance):
    term1 = 1 - (abs(loop_age - test_age) / (distance + years_experience + 1))
    term2 = 1 - (abs(actual_age - test_age) / (years_experience + 1))
    term3 = (players_matched / maximum_matches)
    weight_term = term1 * term2 * term3
    return weight_term


def get_plot_data(cursor, stat, player_id):
    player_yearly_seasonal_stats = batter_queries.get_players_yearly_season_stats(cursor, player_id)
    first_and_last_year_age = get_player_first_and_last_year(player_yearly_seasonal_stats)
    first_year_age = first_and_last_year_age[0]
    last_year_age = first_and_last_year_age[1]
    years_experience = last_year_age - first_year_age

    plot_list = []
    for season_stats in player_yearly_seasonal_stats:
        age_in_season_stats = season_stats[3]
        other_players_season_stats_at_same_age = batter_queries.get_other_players_season_stats_at_same_age\
            (cursor, player_id, age_in_season_stats)
        other_players_season_stats_at_same_age = get_dictionary_with_only_stat_for_player\
            (other_players_season_stats_at_same_age, stat)
        sorted_compared_player_dictionary = get_difference_between_player_stats\
            (season_stats, other_players_season_stats_at_same_age, stat)
        closest_matching_players = get_closest_matching_players(sorted_compared_player_dictionary, age_in_season_stats)
        if len(closest_matching_players) == 0:
            continue
        compared_players_yearly_season_stats = batter_queries.get_compared_players_yearly_season_stats \
            (cursor, closest_matching_players)

        stat_mean_list = []
        for age in player_age_range:
            stat_mean = 0.0
            number_of_players = 0

            for other_player_seasonal_stats in compared_players_yearly_season_stats:
                season_stat_age = other_player_seasonal_stats[3]
                if season_stat_age == age:
                    stat_mean += other_player_seasonal_stats[stat]
                    number_of_players += 1

            if number_of_players == 0:
                continue

            stat_mean /= number_of_players
            stat_mean_with_age_and_player_count = age, stat_mean, number_of_players
            stat_mean_list.append(stat_mean_with_age_and_player_count)

        for mean_and_age_and_player_count in stat_mean_list:
            age = mean_and_age_and_player_count[0]
            distance_from_career = get_distance_from_playing_career_range(first_year_age, last_year_age, age)
            weight_term = get_weight_term(age_in_season_stats, last_year_age, age, years_experience,
                                          mean_and_age_and_player_count[2], number_of_closest_players,
                                          distance_from_career)
            number_of_points = int(number_of_points_for_weight * weight_term) + 1
            mean_and_age = mean_and_age_and_player_count[0], mean_and_age_and_player_count[1]
            for q in range(1, number_of_points):
                plot_list.append(mean_and_age)

    return plot_list
