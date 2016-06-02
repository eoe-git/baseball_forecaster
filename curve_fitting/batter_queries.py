import sqlite3
import configparser

config = configparser.ConfigParser()
config.read('settings.cfg')

database_directory = config['general']['database_directory']
database_name = config['general']['database_name']

minimum_ab_bb = int(config['general']['minimum_plate_appearances'])
furthest_back = config['general']['furthest_back_year']
furthest_forward = int(config['general']['forecast_year']) - 1


def get_player_list(predict_year):
    query = """SELECT batting.player_id, player.birth_year, batting.year,
        batting.year - player.birth_year	AS age,
        batting.ab, batting.r, batting.h, batting.double, batting.triple,
        batting.hr, batting.rbi, batting.sb, batting.bb
        FROM batting
        INNER JOIN player
        ON batting.player_id=player.player_id
        WHERE batting.year = """ + str(predict_year) + """
        AND (batting.ab + batting.bb) > """ + str(minimum_ab_bb)

    return execute_query_and_return_values(query)


def get_players_yearly_season_stats(player_id):
    query = """SELECT batting.player_id, player.birth_year, batting.year,
        batting.year - player.birth_year	AS age,
        batting.ab, batting.r, batting.h, batting.double, batting.triple,
        batting.hr, batting.rbi, batting.sb, batting.bb
        FROM batting
        INNER JOIN player
        ON batting.player_id=player.player_id
        WHERE player.player_id = '""" + str(player_id) + "'""""
        AND (batting.ab + batting.bb) > """ + str(minimum_ab_bb)

    return execute_query_and_return_values(query)


def get_other_players_season_stats_at_same_age(player_id, age):
    query = """SELECT batting.player_id, player.birth_year, batting.year,
        batting.year - player.birth_year	AS age,
        batting.ab, batting.r, batting.h, batting.double, batting.triple,
        batting.hr, batting.rbi, batting.sb, batting.bb
        FROM batting
        INNER JOIN player
        ON batting.player_id=player.player_id
        WHERE batting.player_id != '""" + player_id + """'
        AND batting.year >= """ + str(furthest_back) + """
        AND batting.year <= """ + str(furthest_forward) + """
        AND age = """ + str(age) + """
        AND (batting.ab + batting.bb) > """ + str(minimum_ab_bb)

    return execute_query_and_return_values(query)


def get_players_season_stats_for_age(player_id, age):
    query = """SELECT batting.player_id, player.birth_year, batting.year,
        batting.year - player.birth_year	AS age,
        batting.ab, batting.r, batting.h, batting.double, batting.triple,
        batting.hr, batting.rbi, batting.sb, batting.bb
        FROM batting
        INNER JOIN player
        ON batting.player_id=player.player_id
        WHERE batting.player_id = '""" + player_id + """'
        AND age = """ + str(age) + """
        AND (batting.ab + batting.bb) > """ + str(minimum_ab_bb)

    return execute_query_and_return_values(query)


def get_compared_players_yearly_season_stats(player_list):
    players_in_query = '('
    for player, i in zip(player_list, range(0, len(player_list))):
        player = player[1]
        if i != (len(player_list) - 1):
            players_in_query += "'" + player + "',"
        else:
            players_in_query += "'" + player + "')"

    query = """SELECT batting.player_id, player.birth_year, batting.year,
               batting.year - player.birth_year	AS age,
               batting.ab, batting.r, batting.h, batting.double, batting.triple,
               batting.hr, batting.rbi, batting.sb, batting.bb
                FROM batting
               INNER JOIN player
               ON batting.player_id=player.player_id
                WHERE batting.player_id in """ + players_in_query + """
              AND (batting.ab + batting.bb) > """ + str(minimum_ab_bb)

    return execute_query_and_return_values(query)


def get_queried_categories(predict_year):
    connection = sqlite3.connect(database_directory + database_name)
    cursor = connection.cursor()
    query = """SELECT batting.player_id, player.birth_year, batting.year,
        batting.year - player.birth_year	AS age,
        batting.ab, batting.r, batting.h, batting.double, batting.triple,
        batting.hr, batting.rbi, batting.sb, batting.bb
        FROM batting
        INNER JOIN player
        ON batting.player_id=player.player_id
        WHERE batting.year = """ + str(predict_year) + """
        AND (batting.ab + batting.bb) > """ + str(minimum_ab_bb)

    cursor.execute(query)
    names = list(map(lambda x: x[0], cursor.description))
    query_categories = {}
    for count, category in enumerate(names):
        query_categories[category] = count

    connection.close()

    return query_categories


def create_batting_forecast_table(full_database_path):
    connection = sqlite3.connect(full_database_path)
    cursor = connection.cursor()

    query = """ CREATE TABLE IF NOT EXISTS batting (
                player_id TEXT,
                year INTEGER,
                ab NUMERIC,
                r NUMERIC,
                h NUMERIC,
                double NUMERIC,
                triple NUMERIC,
                hr NUMERIC,
                rbi NUMERIC,
                sb NUMERIC,
                bb NUMERIC)"""

    cursor.execute(query)
    connection.close()


def insert_forecasted_stats(stats):
    forecast_database_name = 'forecast_' + database_name
    query = """ INSERT INTO batting
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    connection = sqlite3.connect(database_directory + forecast_database_name)
    cursor = connection.cursor()
    create_batting_forecast_table(database_directory + forecast_database_name)
    cursor.execute(query, stats)
    connection.commit()
    connection.close()


def execute_query_and_return_values(query):
    connection = sqlite3.connect(database_directory + database_name)
    cursor = connection.cursor()

    result_list = []
    cursor.execute(query)
    query_results = cursor.fetchall()
    result_list.extend(query_results)

    connection.close()
    return result_list
