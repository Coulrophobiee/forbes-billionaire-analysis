import pandas as pd
import sqlite3

class Database():

    def __init__(self):
        pass

    def save_dataframe_to_db(self, df:pd.DataFrame, table_name:str):
        conn = sqlite3.connect("data/database.db")
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        print("Database created!")