import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """Allows the view that calls this access to the database"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """Closes the database"""
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def table_to_dict(table):
    """Turns multiple rows to a list of dictonaries"""
    dict_list=[]

    for row in table:
        dict_list.append(row_to_dict(row))

    return dict_list

def row_to_dict(row):
    """Turns a row from sqlite3 to a dictionary"""
    row_keys=row.keys()
    row_dict={}


    for i in range(len(row)):
        row_dict[row_keys[i]]=row[i]

    return row_dict
