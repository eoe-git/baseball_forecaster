import sqlite3
import pandas as pd


def get_player_list(predict_year, furthest_back, minimum_pa):
    query = """
            SELECT
                DISTINCT batting.player_id
            FROM
                batting
            INNER JOIN
                player ON batting.player_id = player.player_id
            WHERE
                batting.year >= """ + str(furthest_back) + """
                AND batting.year <= """ + str(predict_year - 1) + """
                AND (batting.ab + batting.bb) >  """ + str(minimum_pa) + """
            """
    return query


def get_players_previous_season_stats(predict_year, minimum_pa):
    query = """
            SELECT
                batting.player_id, player.birth_year, batting.year,
                batting.year - player.birth_year	AS age,
                batting.g, batting.ab, batting.h, batting.double, batting.triple,
                batting.hr, batting.r, batting.rbi, batting.sb, batting.cs, batting.bb,
                batting.so, batting.ibb, batting.hbp, batting.sh, batting.sf, batting.g_idp
            FROM
                batting
            INNER JOIN
                player ON batting.player_id=player.player_id
            WHERE
                batting.year = """ + str(predict_year - 1) + """
                AND (batting.ab + batting.bb) > """ + str(minimum_pa)
    return query


def get_player_season_stats_for_career(player_id, predict_year, furthest_back, minimum_pa):
    query = """
            SELECT
                batting.player_id, player.birth_year, batting.year,
                batting.year - player.birth_year	AS age,
                batting.g, batting.ab, batting.h, batting.double, batting.triple,
                batting.hr, batting.r, batting.rbi, batting.sb, batting.cs, batting.bb,
                batting.so, batting.ibb, batting.hbp, batting.sh, batting.sf, batting.g_idp
            FROM
                batting
            INNER JOIN
                player ON batting.player_id=player.player_id
            WHERE
                player.player_id = '""" + str(player_id) + "'""""
                AND batting.year >= """ + str(furthest_back) + """
                AND batting.year <= """ + str(predict_year - 1) + """
                AND (batting.ab + batting.bb) >  """ + str(minimum_pa)
    return query


def create_batting_forecast_table():
    query = """
            CREATE TABLE IF NOT EXISTS batting (
                player_id TEXT,
                year INTEGER,
                age INTEGER,
                ab NUMERIC,
                h NUMERIC,
                bb NUMERIC,
                double NUMERIC,
                triple NUMERIC,
                hr NUMERIC,
                r NUMERIC,
                rbi NUMERIC,
                sb NUMERIC)"""

    return query


def temp_create_batting_forecast_table():
    query = """
            CREATE TABLE IF NOT EXISTS batting (
                player_id TEXT,
                year INTEGER,
                birth_year INTEGER,
                age INTEGER,
                g NUMERIC,
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
                hdp NUMERIC,
                sh NUMERIC,
                sf NUMERIC,
                g_idp NUMERIC)"""

    return query


def insert_forecasted_stats():
    query = """
            INSERT INTO
                batting
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
    return query


def insert_train_data():
    query = """
            INSERT INTO
                batting
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
    return query


def clear_train_data():
    query = """
            DELETE
            FROM
                batting
            """
    return query


def get_all_data_from_batting():
    query = """
            SELECT
                *
            FROM
                batting
            """
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
