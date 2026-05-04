INSERT INTO users (full_name, email, password_hash, role)
VALUES
('Администратор', 'admin@railway.local', 'pbkdf2:sha256:260000$demo$demo', 'admin')
ON CONFLICT (email) DO NOTHING;

INSERT INTO stations (station_name, city) VALUES
('Москва', 'Москва'),
('Санкт-Петербург', 'Санкт-Петербург'),
('Казань', 'Казань')
ON CONFLICT (station_name) DO NOTHING;

INSERT INTO trains (train_number, train_name, train_type) VALUES
('001A', 'Красная стрела', 'Скорый'),
('045K', 'Волга', 'Фирменный')
ON CONFLICT (train_number) DO NOTHING;

INSERT INTO routes (train_id, departure_station_id, arrival_station_id, base_price, travel_time_minutes)
SELECT t.train_id, s1.station_id, s2.station_id, 3500.00, 480
FROM trains t, stations s1, stations s2
WHERE t.train_number = '001A'
  AND s1.station_name = 'Москва'
  AND s2.station_name = 'Санкт-Петербург'
ON CONFLICT DO NOTHING;

INSERT INTO trips (route_id, departure_datetime, arrival_datetime, status)
SELECT r.route_id,
       CURRENT_DATE + INTERVAL '1 day' + TIME '08:00',
       CURRENT_DATE + INTERVAL '1 day' + TIME '16:00',
       'scheduled'
FROM routes r
LIMIT 1;