from simshelpers.database.database import Database


if __name__ == "__main__":
    database = Database()
    database.list_databases(to_print=True)
    database.set_database("ssfm_simulations")
    database.list_tables(to_print=True)
    df = database.select_from_table("dudley_ssfm")
    print(df)
