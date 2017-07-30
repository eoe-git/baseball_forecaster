import sqlite3
import pandas as pd


# this will miss some players that have low AB and only play as DH
# Example year (2014) player 'giambja01' will not show up for the predict year 2015
def get_player_list(predict_year, furthest_back):
    query = """
            SELECT
                DISTINCT batting.player_id
            FROM
                batting
            INNER JOIN fielding
                ON batting.player_id = fielding.player_id
                AND batting.year=fielding.year
            WHERE
                batting.year >= """ + str(furthest_back) + """
                AND batting.year <= """ + str(predict_year - 1) + """
                AND (batting.ab + batting.bb) >= 1
                AND fielding.pos != 'P'
            """
    return query


# this will miss some players that have low AB and only play as DH
# Example year (2014) player 'giambja01' will not show up for the predict year 2015
def get_players_previous_season_stats(predict_year):
    query = """
            SELECT DISTINCT
                batting.player_id, player.birth_year, batting.year,
                batting.year - player.birth_year    AS age, batting.g,
                batting.ab + batting.bb + batting.hbp + batting.sh + batting.sf    AS pa,
                batting.ab, batting.h, batting.double, batting.triple,
                batting.hr, batting.r, batting.rbi, batting.sb, batting.cs, batting.bb,
                batting.so, batting.ibb, batting.hbp, batting.sh, batting.sf, batting.g_idp
            FROM
                batting
            INNER JOIN player
                ON batting.player_id=player.player_id
            INNER JOIN fielding
                ON player.player_id=fielding.player_id
                AND batting.year=fielding.year
            WHERE
                batting.year = """ + str(predict_year - 1) + """
                AND (batting.ab + batting.bb) >= 1
                AND fielding.pos != 'P'
            """
    return query


def get_player_season_stats_for_career(player_id, predict_year, furthest_back):
    query = """
            SELECT
                batting.player_id, player.birth_year, batting.year,
                batting.year - player.birth_year    AS age, batting.g,
                batting.ab + batting.bb + batting.hbp + batting.sh + batting.sf    AS pa,
                batting.ab, batting.h, batting.double, batting.triple,
                batting.hr, batting.r, batting.rbi, batting.sb, batting.cs, batting.bb,
                batting.so, batting.ibb, batting.hbp, batting.sh, batting.sf, batting.g_idp
            FROM
                batting
            INNER JOIN player
                ON batting.player_id=player.player_id
            WHERE
                player.player_id = '""" + str(player_id) + "'""""
                AND batting.year >= """ + str(furthest_back) + """
                AND batting.year <= """ + str(predict_year - 1) + """
                AND (batting.ab + batting.bb) >  1
            """
    return query


def get_actual_forecast_year_values_for_player(player_id, predict_year):
    query = """
            SELECT
                batting.player_id, player.birth_year, batting.year,
                batting.year - player.birth_year    AS age, batting.g,
                batting.ab + batting.bb + batting.hbp + batting.sh + batting.sf    AS pa,
                batting.ab, batting.h, batting.double, batting.triple,
                batting.hr, batting.r, batting.rbi, batting.sb, batting.cs, batting.bb,
                batting.so, batting.ibb, batting.hbp, batting.sh, batting.sf, batting.g_idp
            FROM
                batting
            INNER JOIN player
                ON batting.player_id=player.player_id
            WHERE
                batting.year = """ + str(predict_year) + """
                AND (batting.ab + batting.bb) >= 1
                AND batting.player_id = '""" + player_id + "'"""
    return query


def create_batting_forecast_table(forecasted_stats_list):
    query = """
            CREATE TABLE IF NOT EXISTS batting(
                player_id TEXT, year INTEGER, age INTEGER
            """
    for forecasted_stat in forecasted_stats_list:
        query_line = ', ' + forecasted_stat + ' NUMERIC'
        query += query_line
    query += ')'
    return query


def temp_create_batting_forecast_table(batting_table):
    query = "CREATE TABLE IF NOT EXISTS " + batting_table + """_batting(
                player_id TEXT,
                birth_year INTEGER,
                year INTEGER,
                age INTEGER,
                g NUMERIC,
                pa NUMERIC,
                ab NUMERIC,
                h NUMERIC,
                double NUMERIC,
                triple NUMERIC,
                hr NUMERIC,
                r NUMERIC,
                rbi NUMERIC,
                sb NUMERIC,
                cs NUMERIC,
                bb NUMERIC,
                so NUMERIC,
                ibb NUMERIC,
                hbp NUMERIC,
                sh NUMERIC,
                sf NUMERIC,
                g_idp NUMERIC)
                """
    return query


def create_player_career_stats_table_by_age(stat_categories):
    min_age = 16
    max_age = 50
    query = """
            CREATE TABLE IF NOT EXISTS x_career_batting_by_age(
                player_id TEXT
            """
    for age in range(min_age, max_age + 1):
        for forecasted_stat in stat_categories:
            query_line = ', ' + forecasted_stat + '_age' + str(age) + ' NUMERIC'
            query += query_line
    query += ')'
    return query


def create_player_career_stats_table_by_experience(stat_categories):
    min_age = 16
    max_age = 50

    min_exp = 0
    max_exp = max_age - min_age + 1
    query = """
            CREATE TABLE IF NOT EXISTS x_career_batting_by_experience(
                player_id TEXT
            """
    for exp in range(min_exp, max_exp):
        for forecasted_stat in stat_categories:
            query_line = ', ' + forecasted_stat + '_experience' + str(exp) + ' NUMERIC'
            query += query_line
    query += ')'
    return query


def insert_forecasted_stats(forecasted_stats_list):
    query = """
            INSERT INTO
                batting
            VALUES
                (?, ?, ?
            """
    for i in range(0, len(forecasted_stats_list)):
        query += ', ?'
    query += ')'
    return query


def insert_train_data(batting_table):
    query = """
            INSERT INTO
                """ + batting_table + """_batting
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
    return query


def insert_train_player_career_stats_by_age(stat_categories):
    min_age = 16
    max_age = 50
    query = """
            INSERT INTO
                x_career_batting_by_age
            VALUES
                (?
            """
    for i in range(min_age, max_age + 1):
        for j in range(0, len(stat_categories)):
            query += ', ?'
    query += ')'
    return query


def insert_train_player_career_stats_by_experience(stat_categories):
    min_age = 16
    max_age = 50

    min_exp = 0
    max_exp = max_age - min_age + 1
    query = """
            INSERT INTO
                x_career_batting_by_experience
            VALUES
                (?
            """
    for i in range(min_exp, max_exp):
        for j in range(0, len(stat_categories)):
            query += ', ?'
    query += ')'
    return query


def clear_train_data(batting_table):
    query = """
            DELETE
            FROM
                """ + batting_table + "_batting"
    return query


def clear_train_by_age_data():
    query = """
            DELETE
            FROM
                x_career_batting_by_age
            """
    return query


def clear_train_by_experience_data():
    query = """
            DELETE
            FROM
                x_career_batting_by_experience
            """
    return query


def remove_forecast_table():
    query = """
            DROP TABLE IF EXISTS batting
            """
    return query


def get_all_data_from_batting(batting_table):
    query = """
            SELECT
                *
            FROM
            """ + batting_table + "_batting "
    return query


def get_sql_query_results_as_dataframe(query, database_directory, database_name):
    connection = sqlite3.connect(database_directory + database_name)
    dataframe_results = pd.read_sql_query(query, connection)
    connection.close()
    return dataframe_results


def execute_sql_query(query, database_directory, database_name):
    connection = sqlite3.connect(database_directory + database_name)
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()


def execute_insert_sql_query(query, values, database_directory, database_name):
    connection = sqlite3.connect(database_directory + database_name)
    cursor = connection.cursor()
    cursor.execute(query, values)
    connection.commit()
    connection.close()


def execute_bulk_insert_sql_query(query, values, database_directory, database_name):
    connection = sqlite3.connect(database_directory + database_name)
    cursor = connection.cursor()
    cursor.executemany(query, values)
    connection.commit()
    connection.close()
