def sql_register_store_proc_trade_settings_check_rows_limit():
    query = """
    CREATE OR REPLACE FUNCTION trade_settings_check_rows_limit()
    RETURNS TRIGGER AS $$
    BEGIN
        IF (SELECT COUNT(*) FROM trade_settings) >= 1 THEN
            RAISE EXCEPTION 'Нельзя вставить более одной записи в таблицу с настройками торговли';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    return query

def sql_drop_store_proc_trade_settings_check_rows_limit():

    query = """
        DROP FUNCTION IF EXISTS trade_settings_check_rows_limit
    """
    return query