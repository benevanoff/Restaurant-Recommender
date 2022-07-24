from webapp import db


def _verify_user(username: str, password: str, conn) -> int:
    """
    it seems that several functions would benefit from verifying a user
    :return: error codes:
        0: success
        1: username not found
        2: user password no match
    """
    verify_query = f"SELECT C.password FROM cs411_proj_data.Credential C WHERE C.Username = \'{username}\'"
    verify_result = conn.execute(verify_query).fetchall()

    # checkpoints
    if len(verify_result) == 0:
        return 1
    if verify_result[0][0] != password:
        return 2

    return 0


def update_password(username: str, old_password: str, new_password: str) -> int:
    """
    midterm demo: update the password associated with a specific username
    :return: error codes:
        0: success
        1: username not found
        2: user old password no match
    """
    conn = db.connect()

    err_code = _verify_user(username, old_password, conn)

    if err_code == 0:
        # passed authentification
        update_query = f"UPDATE cs411_proj_data.Credential C SET C.Password = \'{new_password}\' WHERE C.Username = \'{username}\'"
        conn.execute(update_query)
    conn.close()

    return err_code


def delete_user(username: str, password: str) -> int:
    """
    midterm demo: delete a user entry from the Customer table
    :return: error code
        0: successul delete
        1: did not find user
        2: password does not match, so cannot delete user
    """

    conn = db.connect()
    err_code = _verify_user(username, password, conn)
    if err_code == 0:
        # passed authentification
        update_query = f"DELETE FROM cs411_proj_data.Customer C WHERE C.Username = \'{username}\'"
        conn.execute(update_query)
    conn.close()

    return err_code


def get_db_info() -> dict:
    """ returns the table name and column name of our database"""
    conn = db.connect()
    query_tablename = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES " \
                      "WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA='cs411_proj_data'"
    table_name = conn.execute(query_tablename).fetchall()
    table_dict = {t[0]: [] for t in table_name}

    for key in table_dict.keys():
        query_column = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS " \
                       f"WHERE TABLE_NAME = \'{key}\' AND TABLE_SCHEMA='cs411_proj_data'"
        column_name = conn.execute(query_column).fetchall()
        table_dict[key] = [c[0] for c in column_name]
    conn.close()
    return table_dict


def search_table_tuple(table: str, column: str, tuple_key: str) -> []:

    """
    search for an entry in the table
    :return: "" if not found, or the results
    """
    conn = db.connect()
    query_search = f"SELECT * FROM {table} WHERE {column} = \'{tuple_key}\'"
    results = conn.execute(query_search).fetchall()
    return results