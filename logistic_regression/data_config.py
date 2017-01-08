import configparser
import pandas as pd
import logistic_regression.batter_queries as batter_queries

config = configparser.ConfigParser()
config.read('settings.cfg')

database_directory = config['general']['database_directory']
forecast_database_name = config['general']['forecast_database_name']


def create_config_table_query():
    query = """
            CREATE TABLE IF NOT EXISTS config (
            section TEXT,
            setting TEXT,
            value TEXT)
            """
    return query


def insert_config_value_query():
    query = """
            INSERT INTO
                config
            VALUES
                (?, ?, ?)
            """
    return query


def get_config_value_query(section, setting, value):
    query = """
            SELECT
                config.section, config.setting, config.value
            FROM
                config
            WHERE
                config.section = '""" + str(section) + """'
                AND config.setting = '""" + str(setting) + """'
                AND config.value = '""" + str(value) + "'"""
    return query


def clear_config_table_query():
    query = """
            DELETE
            FROM
                config
            """
    return query


def create_config_table():
    query = create_config_table_query()
    batter_queries.execute_sql_query(query, database_directory, forecast_database_name)


def clear_config_table():
    query = clear_config_table_query()
    batter_queries.execute_sql_query(query, database_directory, forecast_database_name)


def insert_config_value(insert_values):
    query = insert_config_value_query()
    batter_queries.execute_insert_sql_query(query, insert_values, database_directory, forecast_database_name)


def value_does_not_exist_in_config_table(section, setting, value):
    query = get_config_value_query(section, setting, value)
    results = batter_queries.get_sql_query_results_as_dataframe(query, database_directory, forecast_database_name)
    if results.__len__() == 0:
        return True
    else:
        return False


def config_values_have_changed():
    for section in config.sections():
        for setting, value in config.items(section):
            if value_does_not_exist_in_config_table(section, setting, value):
                return True
    return False


def insert_values_into_config_table():
    for section in config.sections():
        for setting, value in config.items(section):
            insert_values = section, setting, value
            insert_config_value(list(insert_values))
