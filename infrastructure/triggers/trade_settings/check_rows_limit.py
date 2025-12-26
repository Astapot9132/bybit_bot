def sql_register_trigger_trade_settings_before_insert_check_rows_limit():
    query = f"""
    CREATE OR REPLACE TRIGGER before_insert_check_rows_limit
    BEFORE INSERT ON trade_settings
    FOR EACH ROW
    EXECUTE FUNCTION trade_settings_check_rows_limit();
    """
    return query

def sql_drop_trigger_trade_settings_before_insert_check_rows():
    query = f"""
    DROP TRIGGER IF EXISTS before_insert_check_rows_limit ON trade_settings
    """
    return query