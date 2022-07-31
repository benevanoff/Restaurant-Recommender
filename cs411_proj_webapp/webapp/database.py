from webapp import db
import json


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

def fetch_place_details(place_type, place_id):
    menu_query = ''
    place_query = ''
    if place_type == "bar":
        menu_query = f'SELECT food_id, dish_name FROM ServeBar sb join Food f on sb.food_id=f.id where bar_id={place_id}'
        place_query = f'SELECT res_name, address FROM Bar WHERE id={place_id}'
    if place_type == "cafe":
        menu_query = f'SELECT food_id, dish_name FROM ServeCafe sb join Food f on sb.food_id=f.id where cafe_id={place_id}'
        place_query = f'SELECT * FROM Cafe WHERE id={place_id}'
    if place_type == "restaurant":
        menu_query = f'SELECT food_id, dish_name FROM ServeRestaurant sr join Food f on sr.food_id=f.id where res_id={place_id}'
        place_query = f'SELECT * FROM Restaurant WHERE id={place_id}'

    conn = db.connect()
    menu_query_res = conn.execute(menu_query)
    menu = json.dumps([dict(e) for e in menu_query_res.fetchall()])

    place_query_res = conn.execute(place_query)
    place_res = json.dumps([dict(e) for e in place_query_res.fetchall()])
            
    place_decoded = (json.loads(place_res[1:len(place_res)-1])) # result is a list string but only one object should be returned so we can strip off [] at beginning/end
    place_name = place_decoded["res_name"]
    place_address = place_decoded["address"]

    return {"place_name" : place_name, "place_address": place_address, "menu": menu}
