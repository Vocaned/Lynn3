import discord
import os
import psycopg2
import logging

# $ createdb lynnDB

conn = psycopg2.connect(database="lynnDB",
                        user = "postgres",
                        password = "pass123",
                        host = "127.0.0.1",
                        port = "5432")
conn.set_session(autocommit=True)

cur = conn.cursor()

# Update from commit [75519d]: ALTER TABLE users DROP COLUMN classicube, DROP COLUMN minecraft; ALTER TABLE guilds ADD COLUMN customcommands TEXT;

cur.execute('''CREATE TABLE IF NOT EXISTS guilds
            (id BIGINT PRIMARY KEY      NOT NULL,
            disabledmodules TEXT,
            prefix          TEXT,
            customcommands  TEXT);''')

cur.execute('''CREATE TABLE IF NOT EXISTS users
            (id BIGINT PRIMARY KEY      NOT NULL,
            location   TEXT);''')

async def setUser(id, key, value):
    cur.execute('SELECT * FROM users WHERE id = %s', (id,))
    res = cur.fetchone()
    if not res:
        cur.execute('''INSERT INTO users (id, location, classicube, minecraft)
                    VALUES (%s, '', '', '')''', (id,))
        cur.execute('SELECT * FROM users WHERE id = %s', (id,))
        res = cur.fetchone()

    cur.execute('UPDATE users SET {} = %s WHERE id = %s'.format(key), (value, id))

async def setGuild(id, key, value):
    cur.execute('SELECT * FROM guilds WHERE id = %s', (id,))
    res = cur.fetchone()
    if not res:
        cur.execute('''INSERT INTO guilds (id, disabledmodules, prefix)
                    VALUES (%s, '', '')''', (id,))
        cur.execute('SELECT * FROM guilds WHERE id = %s', (id,))
        res = cur.fetchone()

    # 'UPDATE guild SET %s = %s WHERE id = %s' doesn't work since %s includes quotes
    cur.execute('UPDATE guilds SET {} = %s WHERE id = %s'.format(key), (value, id))

async def getValue(table, id, key):
    # There's probably some workaround for this, but for now this could cause sql injection issues
    # if called with untrusted data
    cur.execute(f'SELECT {key} FROM {table} WHERE id = {id}')
    res = cur.fetchone()
    if not res:
        return None
    return res[0]