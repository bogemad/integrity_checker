import sqlite3, sys
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    return conn

def create_table_statement(run_type, table_name):
    if run_type == 'compare':
        return f""" CREATE TABLE IF NOT EXISTS {table_name} (
                                        remote_path text PRIMARY KEY,
                                        local_path text NOT NULL,
                                        remote_md5 text NOT NULL,
                                        local_md5 text NOT NULL,
                                        status text NOT NULL
                                    ); """
    elif run_type == 'calc_md5':
        return f""" CREATE TABLE IF NOT EXISTS {table_name} (
                                        path text PRIMARY KEY,
                                        md5 text NOT NULL
                                    ); """
    else:
        sys.exit("Unknown run_type")

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_calc_md5_task(conn, result, table_name):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    sql = f''' INSERT INTO {table_name}(path,md5)
            VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, result)
    conn.commit()

def create_compare_task(conn, result, table_name):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """
    sql = f''' INSERT INTO {table_name}(remote_path,local_path,remote_md5,local_md5,status)
            VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, result)
    conn.commit()


def check_entry_exists(conn, table_name, column_name, value):
    """
    Check if a specific entry exists in a SQLite table.

    Parameters:
    - db_path: Path to the SQLite database.
    - table_name: Name of the table you want to check.
    - column_name: Name of the column/index you want to search.
    - value: Value of the entry you're searching for.

    Returns:
    - True if the entry exists, False otherwise.
    """
    
    # Connect to the SQLite database
    cursor = conn.cursor()

    # Use parameterized query for safety (to prevent SQL injection)
    cursor.execute(f"SELECT * FROM {table_name} WHERE {column_name} = ?", (value,))
    
    # Fetch the results
    result = cursor.fetchall()
    
    # Return True if the entry exists, False otherwise
    return len(result) > 0


