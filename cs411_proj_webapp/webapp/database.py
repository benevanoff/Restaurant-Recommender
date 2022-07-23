from webapp import db


def update_password(username: str, old_password: str, new_password: str) -> int:
    """
    midterm demo: update the password associated with a specific username
    :return: error codes:
        0: success
        1: username not found
        2: user old password no match
    """
    conn = db.connect()

    verify_query = f"SELECT U.password FROM cs411_proj_data.Users U WHERE U.Username = \'{username}\'"
    verify_result = conn.execute(verify_query).fetchall()

    # checkpoints
    if len(verify_result) == 0:
        return 1
    if verify_result[0][0] != old_password:
        return 2

    # passed all
    update_query = f"UPDATE cs411_proj_data.Users U SET U.Password = \'{new_password}\' WHERE U.Username = \'{username}\'"
    conn.execute(update_query)
    conn.close()

    return 0


def delete_user():
    """
    midterm demo: delete a user entry from the Customer table
    :return:
    """

    return
