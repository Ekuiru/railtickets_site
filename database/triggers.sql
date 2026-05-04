CREATE OR REPLACE FUNCTION update_order_total()
RETURNS TRIGGER AS $$
DECLARE
    v_order_id INT;
BEGIN
    v_order_id := CASE
        WHEN TG_OP = 'DELETE' THEN OLD.order_id
        ELSE NEW.order_id
    END;

    UPDATE orders
    SET total_amount = calculate_order_total(v_order_id)
    WHERE order_id = v_order_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_order_total ON tickets;

CREATE TRIGGER trg_update_order_total
AFTER INSERT OR UPDATE OR DELETE ON tickets
FOR EACH ROW
EXECUTE FUNCTION update_order_total();

CREATE OR REPLACE FUNCTION create_train_structure()
RETURNS TRIGGER AS $$
DECLARE
    v_carriage_id INT;
    v_carriage_number INT;
    v_seat_number INT;
    v_carriage_type VARCHAR(30);
    v_seat_class VARCHAR(30);
    v_carriage_count INT;
    v_seats_per_carriage INT;
BEGIN
    -- Базовые шаблоны по типу поезда
    IF LOWER(NEW.train_type) = LOWER('Сапсан') THEN
        v_carriage_count := 10;
        v_seats_per_carriage := 40;
        v_carriage_type := 'сидячий';
        v_seat_class := 'business';
    ELSIF LOWER(NEW.train_type) = LOWER('Фирменный') THEN
        v_carriage_count := 8;
        v_seats_per_carriage := 36;
        v_carriage_type := 'купе';
        v_seat_class := 'coupe';
    ELSIF LOWER(NEW.train_type) = LOWER('Скорый') THEN
        v_carriage_count := 8;
        v_seats_per_carriage := 54;
        v_carriage_type := 'плацкарт';
        v_seat_class := 'economy';
    ELSE
        v_carriage_count := 6;
        v_seats_per_carriage := 40;
        v_carriage_type := 'сидячий';
        v_seat_class := 'standard';
    END IF;

    FOR v_carriage_number IN 1..v_carriage_count LOOP
        INSERT INTO carriages (train_id, carriage_number, carriage_type, seat_count)
        VALUES (NEW.train_id, v_carriage_number, v_carriage_type, v_seats_per_carriage)
        RETURNING carriage_id INTO v_carriage_id;

        FOR v_seat_number IN 1..v_seats_per_carriage LOOP
            INSERT INTO seats (carriage_id, seat_number, seat_class)
            VALUES (v_carriage_id, v_seat_number, v_seat_class);
        END LOOP;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS trg_create_train_structure ON trains;

CREATE TRIGGER trg_create_train_structure
AFTER INSERT ON trains
FOR EACH ROW
EXECUTE FUNCTION create_train_structure();