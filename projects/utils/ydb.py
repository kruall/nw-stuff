import ydb

from lib.common import variables


driver = None
pool = None
session = None


def init():
    if driver is None:
        driver = ydb.Driver(endpoint=variables.ydb_enpoint, database=variables.ydb_database)
        driver.wait(fail_fast=True, timeout=5)
        pool = ydb.SessionPool(driver)
        session = driver.table_client.session().create()


def run_preprared_query(query, **kwargs):
    prepared_query = session.prepare(query)
    return session.transaction(ydb.SerializableReadWrite()).execute(
        prepared_query, {
            '$' + key: value for key, value in kwargs.items()
        },
        commit_tx=True
    )
