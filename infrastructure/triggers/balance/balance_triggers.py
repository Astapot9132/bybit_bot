def sql_register_trigger_balance_before_insert_check_rows_limit():
    query = f"""
    CREATE OR REPLACE TRIGGER before_insert_check_rows_limit
    BEFORE INSERT ON balance
    FOR EACH ROW
    EXECUTE FUNCTION balance_check_rows_limit();
    """
    return query

def sql_drop_trigger_balance_before_insert_check_rows():
    query = f"""
    DROP TRIGGER IF EXISTS before_insert_check_rows_limit ON balance
    """
    return query