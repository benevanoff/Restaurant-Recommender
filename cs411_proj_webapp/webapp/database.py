from webapp import db


def _verify_user(username: str, password: str, conn) -> int:
    """
    it seems that several functions would benefit from verifying a user
    :return: error codes:
        0: success
        1: username not found
        2: user password no match
    """
    verify_query = f"SELECT U.password FROM cs411_proj_data.Users U WHERE U.Username = \'{username}\'"
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
        update_query = f"UPDATE cs411_proj_data.Users U SET U.Password = \'{new_password}\' WHERE U.Username = \'{username}\'"
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
        update_query = f"DELETE FROM cs411_proj_data.Users U WHERE U.Username = \'{username}\'"
        conn.execute(update_query)
    conn.close()

    return err_code
