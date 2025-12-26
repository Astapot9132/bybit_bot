def sql_register_trigger_after_fill_order_change_revenue_row():
    query = f"""
    CREATE OR REPLACE TRIGGER after_fill_order_change_revenue_row
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_revenue_row_after_fill_order();
    """
    return query

def sql_drop_trigger_after_fill_order_change_revenue_row():
    query = f"""
    DROP TRIGGER IF EXISTS after_fill_order_change_revenue_row ON orders
    """
    return query