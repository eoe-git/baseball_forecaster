import sqlite3
import configparser

config = configparser.ConfigParser()
config.read('settings.cfg')

minimum_ab_bb = int(config['general']['minimum_plate_appearances'])
furthest_back = config['general']['furthest_back_year']
furthest_forward = int(config['general']['forecast_year']) - 1


def get_player_list(cursor, predict_year):
    query = """SELECT batting.player_id, player.birth_year, batting.year,
        batting.year - player.birth_year	AS age,
        batting.ab, batting.r, batting.h, batting.double, batting.triple,
        batting.hr, batting.rbi, batting.sb, batting.bb
        FROM batting
        INNER JOIN player
        ON batting.player_id=player.player_id
        WHERE batting.year = """ + str(predict_year) + """
        AND (batting.ab + batting.bb) > """ + str(minimum_ab_bb)

    return execute_query_and_return_values(cursor, query)


def get_players_yearly_season_stats(cursor, player_id):
    query = """SELECT batting.player_id, player.birth_year, batting.year,
        batting.year - player.birth_year	AS age,
        batting.ab, batting.r, batting.h, batting.double, batting.triple,
        batting.hr, batting.rbi, batting.sb, batting.bb
        FROM batting
        INNER JOIN player
        ON batting.player_id=player.player_id
        WHERE player.player_id = '""" + str(player_id) + "'""""
        AND (batting.ab + batting.bb) > """ + str(minimum_ab_bb)

    return execute_query_and_return_values(cursor, query)


def get_other_players_season_stats_at_same_age(cursor, player_id, age):
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

    return execute_query_and_return_values(cursor, query)


def get_players_season_stats_for_age(cursor, player_id, age):
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

    return execute_query_and_return_values(cursor, query)


def get_compared_players_yearly_season_stats(cursor, player_list):
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

    return execute_query_and_return_values(cursor, query)


def get_queried_categories(cursor, predict_year):
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

    return query_categories


def create_batting_forecast_table(cursor):
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


def insert_forecasted_stats(database_directory, database_name, stats):
    database_name = 'forecast_' + database_name
    query = """ INSERT INTO batting
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    connection = sqlite3.connect(database_directory + database_name)
    cursor = connection.cursor()
    create_batting_forecast_table(cursor)
    cursor.execute(query, stats)
    connection.commit()
    connection.close()


def execute_query_and_return_values(cursor, query):
    result_list = []
    cursor.execute(query)
    query_results = cursor.fetchall()
    result_list.extend(query_results)
    return result_list
