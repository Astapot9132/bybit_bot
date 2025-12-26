def sql_register_store_proc_before_update_check_updated_at():
    query = """
    CREATE OR REPLACE FUNCTION before_update_check_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        IF OLD.updated_at = NEW.updated_at THEN
            NEW.updated_at = CURRENT_TIMESTAMP;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    return query

def sql_drop_store_proc_before_update_check_updated_at():

    query = """
        DROP FUNCTION IF EXISTS before_update_check_updated_at
    """
    return query