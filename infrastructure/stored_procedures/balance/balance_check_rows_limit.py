
def sql_register_store_proc_balance_check_rows_limit():
    query = """
    CREATE OR REPLACE FUNCTION balance_check_rows_limit()
    RETURNS TRIGGER AS $$
    BEGIN
        IF (SELECT COUNT(*) FROM balance) >= 1 THEN
            RAISE EXCEPTION 'Нельзя вставить более одной записи в таблицу с балансом';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    return query

def sql_drop_store_proc_balance_check_rows_limit():

    query = """
        DROP FUNCTION IF EXISTS balance_check_rows_limit
    """
    return query