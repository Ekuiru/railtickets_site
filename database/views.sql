CREATE OR REPLACE VIEW available_seats_view AS
SELECT
    t.trip_id,
    s.seat_id,
    c.carriage_number,
    s.seat_number,
    s.seat_class
FROM trips t
JOIN routes r ON t.route_id = r.route_id
JOIN trains tr ON r.train_id = tr.train_id
JOIN carriages c ON c.train_id = tr.train_id
JOIN seats s ON s.carriage_id = c.carriage_id
LEFT JOIN tickets tk
    ON tk.trip_id = t.trip_id
   AND tk.seat_id = s.seat_id
   AND tk.ticket_status IN ('booked', 'paid')
WHERE tk.ticket_id IS NULL;