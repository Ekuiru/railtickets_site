CREATE OR REPLACE FUNCTION calculate_order_total(p_order_id INT)
RETURNS NUMERIC AS $$
DECLARE
    result NUMERIC(10,2);
BEGIN
    SELECT COALESCE(SUM(price), 0)
    INTO result
    FROM tickets
    WHERE order_id = p_order_id;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_available_seats_count(p_trip_id INT)
RETURNS INT AS $$
DECLARE
    result INT;
BEGIN
    SELECT COUNT(*)
    INTO result
    FROM available_seats_view
    WHERE trip_id = p_trip_id;

    RETURN result;
END;
$$ LANGUAGE plpgsql;