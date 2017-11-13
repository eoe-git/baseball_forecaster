import configparser
import pandas as pd
import sqlite3

config = configparser.ConfigParser()
config.read('settings.cfg')

database_directory = config['general']['database_directory']
database_name = config['general']['database_name']
sql_database_path = database_directory + database_name

stat_files = ['AllstarFull', 'Appearances', 'AwardsManagers', 'AwardsPlayers', 'AwardsShareManagers',
               'AwardsSharePlayers', 'Batting', 'BattingPost', 'CollegePlaying', 'Fielding', 'FieldingOF',
               'FieldingPost', 'HallOfFame', 'HomeGames', 'Managers', 'ManagersHalf', 'Master',
               'Parks', 'Pitching', 'PitchingPost', 'Salaries', 'Schools', 'SeriesPost', 'Teams', 'TeamsFranchises',
               'TeamsHalf']


def create_database():
    for file in stat_files:
        create_table(file)


def clear_database():
    for file in stat_files:
        drop_table(file)


def create_table(file):
    file_path = database_directory + file + '.csv'
    df = pd.read_csv(file_path)
    df = fix_violating_column_names(df)
    insert_table_values(df, file)


def fix_violating_column_names(df):
    for column in list(df):
        if column == '2B':
            df.rename(columns={'2B': 'DOUBLE'}, inplace=True)
        elif column == '3B':
            df.rename(columns={'3B': 'TRIPLE'}, inplace=True)
        elif '.' in column:
            column_words = column.split('.')
            fixed_column_name = column_words[0] + column_words[1].title()
            df.rename(columns={column: fixed_column_name}, inplace=True)

    return df


def drop_table(file):
    query = drop_table_query(file)
    conn = sqlite3.connect(sql_database_path)
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    conn.close()


def drop_table_query(file):
    query = """
            DROP TABLE IF EXISTS
            """ + file
    return query


def insert_table_values(df, file):
    conn = sqlite3.connect(sql_database_path)
    df.to_sql(file, conn, if_exists='append', index=False)
    conn.close()
