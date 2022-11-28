import psycopg2
from psycopg2.extensions import connection


def create_db(conn: connection):
    cur = conn.cursor()
    cur.execute("""
    DROP TABLE IF EXISTS phone_number;
    DROP TABLE IF EXISTS users;
    """)
    conn.commit()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS users(
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(40) NOT NULL,
                last_name VARCHAR(40) NOT NULL,
                email VARCHAR(40) NOT NULL
            );
    """)
    cur.execute("""
            CREATE TABLE IF NOT EXISTS phone_number(
                id SERIAL PRIMARY KEY,
                user_id INTEGER not null references users(id),
                number VARCHAR(40) UNIQUE
            );
        """)

    conn.commit()
    cur.close()


def add_client(conn: connection,
               first_name: str,
               last_name: str,
               email: str,
               phones=None):
    cur = conn.cursor()
    cur.execute(
        """
    INSERT INTO users(first_name,last_name,email) VALUES (%s,%s,%s);
    """, (
            first_name,
            last_name,
            email,
        ))
    conn.commit()
    cur.execute(
        """
    SELECT id FROM users WHERE first_name=%s AND last_name=%s AND email=%s;
    """, (first_name, last_name, email))
    id = cur.fetchone()
    cur.execute("INSERT INTO phone_number(user_id,number) VALUES (%s, %s)",
                (id, phones))
    cur.close()


def add_phone(conn: connection, client_id, phone):
    cur = conn.cursor()
    cur.execute("SELECT number FROM phone_number WHERE user_id=%s",
                (client_id, ))
    value = cur.fetchone()
    print(value)
    if value == (None, ):
        cur.execute(
            """
        UPDATE phone_number
        SET number=%s 
        WHERE user_id=%s
        """, (phone, client_id))
    else:
        cur.execute(
            "INSERT INTO phone_number(user_id, number) VALUES (%s ,%s)",
            (client_id, phone))

    conn.commit()
    cur.close()


def change_client(conn: connection,
                  client_id,
                  first_name=None,
                  last_name=None,
                  email=None,
                  phones=None):
    cur = conn.cursor()
    # cur.execute("""
    # UPDATE users u
    # JOIN phone_number pn ON pn.user_id=u.id
    # SET first_name=%s, last_name=%s, email=%s, number=%s
    # WHERE u.id=%s;
    # """, (first_name, last_name, email, phones, client_id,))
    cur.execute(
        """
    UPDATE users
    SET first_name=%s, last_name=%s, email=%s
    WHERE id=%s;
    """, (first_name, last_name, email, client_id))
    cur.execute(
        """
    UPDATE phone_number
    SET number=%s
    WHERE user_id=%s
    """, (phones, client_id))

    conn.commit()
    cur.close()


def delete_phone(conn: connection, client_id, phone):
    cur = conn.cursor()
    cur.execute(
        """
    DELETE FROM phone_number WHERE user_id=%s AND number=%s
    
    """, (client_id, phone))
    conn.commit()
    cur.close()


def delete_client(conn: connection, client_id):
    cur = conn.cursor()
    cur.execute(
        """
    DELETE FROM phone_number
    where user_id=%s;
    DELETE FROM users
    WHERE id = %s;

    """, (client_id, client_id))
    conn.commit()
    cur.close()


def find_client(conn: connection,
                first_name=None,
                last_name=None,
                email=None,
                phone=None):
    cur = conn.cursor()
    cur.execute(
        """
    SELECT u.id,first_name,last_name,email,number FROM users u
    JOIN phone_number p ON p.user_id= u.id
    GROUP BY u.id,first_name, last_name, email, number
    HAVING first_name=%s AND last_name=%s AND email=%s AND number=%s
    """, (
            first_name,
            last_name,
            email,
            phone,
        ))
    print(cur.fetchone())
    cur.close()


with psycopg2.connect(host="89.223.120.167",
                      port="5432",
                      database="vkinder_db",
                      user="postgres",
                      password="postgres") as conn:
    create_db(conn)
    add_client(
        conn,
        'Meow',
        'Bark',
        "i'mNotCat@gmail.com",
    )
    add_phone(conn, 1, '+79785105248')
    add_client(conn, 'Bark', 'Meow', 'This is some random email',
               '88005553535')
    add_phone(conn, 2, '1234341234')
    change_client(conn, 1, 'Tets', 'Test1', 'Test@email', '88001234')
    find_client(conn, 'Tets', 'Test1', 'Test@email', '88001234')
    delete_phone(conn, 1, '+79785105248')
    delete_client(conn, 2)
