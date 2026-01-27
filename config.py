import os
from contextlib import contextmanager

from psycopg2 import pool
import logging
import psycopg2
import time
import secrets
JWT_TOKEN = os.environ.get('JWT_TOKEN')

SUPABASE_S3_ENDPOINT = os.environ.get('SUPABASE_S3_ENDPOINT')#url of S3

SUPABASE_ACCESS_KEY = os.environ.get('SUPABASE_ACCESS_KEY')

SUPABASE_SECRET_KEY = os.environ.get('SUPABASE_SECRET_KEY')#secret access kay

SUPABASE_PROJECT_REF = os.environ.get('SUPABASE_PROJECT_REF')  # project ref url

SECRET_KEY = os.environ.get('SECRET_KEY')

DATABASE_URL = os.environ.get('DATABASE_URL')  # Supabase Postgres

BUCKET_NAME = 'prytysecure'

PRESIGNED_EXPIRES = 24 * 3600

FILES_TABLE ="""
            CREATE TABLE IF NOT EXISTS files (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                filename VARCHAR(255) NOT NULL,
                save_key VARCHAR(500) NOT NULL UNIQUE,
                download_url VARCHAR(500) UNIQUE,
                expires_at TIMESTAMPTZ,
                user_id VARCHAR(150),
                ip INET,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                safe_token VARCHAR(500) UNIQUE NOT NULL
            );
            
            
            CREATE INDEX IF NOT EXISTS idx_files_expires_at
            ON files(expires_at) WHERE expires_at IS NOT NULL;
            
            
                        
            CREATE INDEX IF NOT EXISTS idx_files_filename
            ON files(filename);
            
            CREATE INDEX IF NOT EXISTS idx_files_ip
            ON files(ip);
            """
def commonplace_text(world):
    #make user input better! exemple:
    # userinput = sql Attack_tools ---> sqlattacktools |or:
    # userinput = sQlAtT_ack_too ls --->sqlattacktools
    if world:
        return world.lower().strip().replace(' ','').replace('_','')
    else:
        return ''

def create_users_sql(url=DATABASE_URL):
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    try:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                salt VARCHAR(100) NOT NULL UNIQUE,
                hashed_password VARCHAR(500) NOT NULL,
                email VARCHAR(100) DEFAULT NULL UNIQUE
            )
        ''')

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"error: {e}")
    finally:
        cur.close()
        conn.close()

def time_delay(start_time):
    try:
        delay = time.time() - start_time
        if delay < 0.8:
            time.sleep(0.8 - delay)
    except Exception as e:
        logging.error(f'time delay error:{e}')
        delay = time.time() - start_time
        if delay < 0.8:
            time.sleep(0.8 - delay)




main_pool = pool.SimpleConnectionPool(minconn=1, maxconn=25, dsn=DATABASE_URL)


def create_files_table(url:str=DATABASE_URL,create_files_table_sql:str=FILES_TABLE):
    try:
        with psycopg2.connect(url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_files_table_sql)
                conn.commit()
    except Exception as e:
        logging.error(f'create files table error:{e}')
        print(f'create files table error:{e}')


@contextmanager
def get_conn(conn_commit:bool=True):
    conn = main_pool.getconn()
    try:
        yield conn
        if conn_commit:
            conn.commit()
        else:
            conn.rollback()
    except Exception as e:
        conn.rollback()
        logging.error(f'{e}')
        raise
    finally:
        main_pool.putconn(conn)

@contextmanager
def get_cursor(conn_commit:bool=True):
    with get_conn(conn_commit) as conn:
        with conn.cursor() as cursor:
            try:
                yield cursor
            finally:
                cursor.close()
