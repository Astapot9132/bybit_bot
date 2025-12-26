
from infrastructure.models.order_models.enums import OrderStatusEnum, OrderTypeEnum


def sql_register_store_proc_update_revenue_row_after_fill_order():
    query = f"""
    CREATE OR REPLACE FUNCTION update_revenue_row_after_fill_order()
    RETURNS TRIGGER AS $$
    DECLARE
        new_revenue_usd NUMERIC;
        new_revenue_btc NUMERIC;
    BEGIN
        IF OLD.status != NEW.status AND NEW.type = '{OrderTypeEnum.buy.value}' THEN
            
            IF OLD.status = '{OrderStatusEnum.placed.value}' AND NEW.status = '{OrderStatusEnum.filled.value}' THEN
            
                IF NEW.order_executed_value IS NULL OR NEW.order_quantity IS NULL OR NEW.order_fact_price IS NULL THEN
                    RAISE EXCEPTION 'order_executed_value, order_quantity, order_fact_price ДОЛЖНЫ БЫТЬ ЗАПОЛНЕНЫ';
                END IF;
    
                new_revenue_usd := NEW.order_executed_value * 0.4 / (100 + 0.4);
                new_revenue_btc := NEW.order_quantity * 0.4 / (100 + 0.4);
                
                UPDATE revenue
                SET 
                    filled_orders = filled_orders + 1,
                    revenue_usd = COALESCE(revenue_usd, 0) + new_revenue_usd,
                    revenue_btc = COALESCE(revenue_btc, 0) + new_revenue_btc,
                    current_avg_price = ROUND(((COALESCE(current_avg_price, 0)::NUMERIC * COALESCE(current_quantity, 0) + NEW.order_fact_price * NEW.order_quantity) / NULLIF((COALESCE(current_quantity, 0) + NEW.order_quantity), 0))::NUMERIC, 8),
                    current_quantity = COALESCE(current_quantity, 0) + NEW.order_quantity,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.revenue_id;
                    
            ELSIF OLD.status = '{OrderStatusEnum.filled.value}' AND NEW.status = '{OrderStatusEnum.placed.value}' THEN
    
                new_revenue_usd := NEW.order_executed_value * 0.4 / (100 + 0.4);
                new_revenue_btc := NEW.order_quantity * 0.4 / (100 + 0.4);
                
                UPDATE revenue
                SET 
                    filled_orders = filled_orders - 1,
                    revenue_usd = revenue_usd - new_revenue_usd,
                    revenue_btc = revenue_btc - new_revenue_btc,
                    current_avg_price = ROUND(((COALESCE(current_avg_price, 0)::NUMERIC * COALESCE(current_quantity, 0) - NEW.order_fact_price * NEW.order_quantity) / NULLIF((COALESCE(current_quantity, 0) - NEW.order_quantity), 0))::NUMERIC, 8),
                    current_quantity = current_quantity - NEW.order_quantity,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.revenue_id;
    
            END IF;
    
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    return query

def sql_drop_store_proc_update_revenue_row_after_fill_order():

    query = """
        DROP FUNCTION IF EXISTS update_revenue_row_after_fill_order
    """
    return query