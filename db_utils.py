from typing import Optional, Dict, Any

import datetime
import uuid
import json
import pymysql
import pymysql.cursors

def get_organization_app(conn: pymysql.connections.Connection, uuid: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves an organization application record from the database based on the provided UUID.

    Parameters:
    conn (pymysql.connections.Connection): The database connection object.
    uuid (str): The UUID of the organization application to retrieve.

    Returns:
    dict: A dictionary containing the organization application record, or None if no record is found.

    Raises:
    pymysql.MySQLError: If an error occurs while querying the database.

    Notes:
    - The UUID is expected to be in standard format with hyphens. This function removes the hyphens before querying.
    - Ensure the database connection (conn) is properly established before calling this function.
    - The returned dictionary keys will correspond to the columns in the 'organization_apps' table.
    """
    uuid = str(uuid).replace('-', '')

    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM organization_apps WHERE uuid = %s"
            cursor.execute(sql, (uuid))
            organization_app = cursor.fetchone()
    except pymysql.MySQLError as e:
        raise

    return organization_app

def get_or_create_space(conn: pymysql.connections.Connection, organization_id: int, space_code: str, space_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a space record from the database based on the provided organization ID and space code.
    If the space does not exist, it creates a new space record with the provided details.

    Parameters:
    conn (pymysql.connections.Connection): The database connection object.
    organization_id (int): The ID of the organization to which the space belongs.
    space_code (str): The code of the space to retrieve or create.
    space_name (str): The name of the space to create if it does not exist.

    Returns:
    dict: A dictionary containing the space record.

    Raises:
    pymysql.MySQLError: If an error occurs while querying or inserting into the database.

    Notes:
    - Ensure the database connection (conn) is properly established before calling this function.
    - The returned dictionary keys will correspond to the columns in the 'spaces' table.
    - If a new space is created, the function will return the newly created record.
    """
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM spaces WHERE organization_id = %s AND space_code = %s"
            cursor.execute(sql, (organization_id, space_code))
            space = cursor.fetchone()

            if space is None:
                sql_insert = "INSERT INTO spaces (organization_id, space_code, space_name) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert, (organization_id, space_code, space_name))

                space_id = cursor.lastrowid

                sql_select = "SELECT * FROM spaces WHERE id = %s"
                cursor.execute(sql_select, (space_id))

                space = cursor.fetchone()

    except pymysql.MySQLError as e:
        raise

    return space

def get_or_create_participant(conn: pymysql.connections.Connection, organization_id: int, space: Dict[str, Any], participant_code: str, participant_user_code: str, participant_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a participant record from the database based on the provided organization ID, space, and participant code.
    If the participant does not exist, it creates a new participant record with the provided details.

    Parameters:
    conn (pymysql.connections.Connection): The database connection object.
    organization_id (int): The ID of the organization to which the participant belongs.
    space (dict): A dictionary containing the space details, including the space ID and open result days.
    participant_code (str): The code of the participant to retrieve or create.
    participant_user_code (str): The user code of the participant.
    participant_name (str): The name of the participant.

    Returns:
    dict: A dictionary containing the participant record.

    Raises:
    pymysql.MySQLError: If an error occurs while querying or inserting into the database.

    Notes:
    - Ensure the database connection (conn) is properly established before calling this function.
    - The returned dictionary keys will correspond to the columns in the 'participants' table.
    - If a new participant is created, a unique UUID is generated for the participant.
    - The result closed at date is calculated based on the current date and the open result days from the space dictionary.
    """
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM participants WHERE organization_id = %s AND space_id = %s AND participant_code = %s"
            cursor.execute(sql, (organization_id, space['id'], participant_code))
            participant = cursor.fetchone()

            if participant is None:
                exist = True
                while exist:
                    participant_uuid = uuid.uuid4().hex
                    sql = "SELECT * FROM participants WHERE uuid = %s"
                    cursor.execute(sql, (participant_uuid))

                    exist_participant = cursor.fetchone()

                    if exist_participant is None:
                        result_closed_at = (datetime.datetime.now() + datetime.timedelta(days=space['open_result_days']))
                        result_closed_at = result_closed_at.strftime('%Y-%m-%d %H:%M:%S.%f')

                        sql_insert = "INSERT INTO participants (uuid, organization_id, space_id, participant_code, participant_user_code, participant_name, result_closed_at) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        cursor.execute(sql_insert, (participant_uuid, organization_id, space['id'], participant_code, participant_user_code, participant_name, result_closed_at))

                        participant_id = cursor.lastrowid

                        sql_select = "SELECT * FROM participants WHERE id = %s"
                        cursor.execute(sql_select, (participant_id))

                        participant = cursor.fetchone()
                        exist = False

    except pymysql.MySQLError as e:
        raise

    return participant

def create_face_auth_log(conn: pymysql.connections.Connection, organization_id: int, space_id: int, participant_id: int, authentication_code: str, is_authenticated: bool, reason: Dict[str, Any], logs: Dict[str, Any], threshold: float) -> bool:
    """
    Creates a new face authentication log record in the database.

    Parameters:
    conn (pymysql.connections.Connection): The database connection object.
    organization_id (int): The ID of the organization.
    space_id (int): The ID of the space.
    participant_id (int): The ID of the participant.
    authentication_code (str): The authentication code for the face authentication event.
    is_authenticated (bool): Whether the authentication was successful.
    reason (dict): A dictionary containing the reason for the authentication result.
    logs (dict): A dictionary containing the detailed logs of the authentication process.
    threshold (float): The threshold value used for the authentication.

    Returns:
    bool: True if the log entry was created successfully.

    Raises:
    pymysql.MySQLError: If an error occurs while inserting the log entry into the database.

    Notes:
    - Ensure the database connection (conn) is properly established before calling this function.
    - The 'reason' and 'logs' parameters are converted to JSON format before being stored in the database.
    - The function returns True if the insertion is successful.
    """
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO face_auth_logs (authentication_code, organization_id, space_id, participant_id, is_authenticated, reason, logs, threshold) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (authentication_code, organization_id, space_id, participant_id, is_authenticated, json.dumps(reason), json.dumps(logs), threshold))

    except pymysql.MySQLError as e:
        raise

    return True
