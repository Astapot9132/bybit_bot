def sql_register_trigger_before_update_check_updated_at(table_name: str):
    query = f"""
    CREATE OR REPLACE TRIGGER before_update_check_updated_at
    BEFORE INSERT ON {table_name}
    FOR EACH ROW
    EXECUTE FUNCTION before_update_check_updated_at();
    """
    return query

def sql_drop_trigger_before_update_check_updated_at(table_name: str):
    query = f"""
    DROP TRIGGER IF EXISTS before_update_check_updated_at ON {table_name}
    """
    return query