CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stations (
    station_id SERIAL PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL UNIQUE,
    city VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS trains (
    train_id SERIAL PRIMARY KEY,
    train_number VARCHAR(20) NOT NULL UNIQUE,
    train_name VARCHAR(100),
    train_type VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS routes (
    route_id SERIAL PRIMARY KEY,
    train_id INT NOT NULL REFERENCES trains(train_id) ON DELETE CASCADE,
    departure_station_id INT NOT NULL REFERENCES stations(station_id),
    arrival_station_id INT NOT NULL REFERENCES stations(station_id),
    base_price NUMERIC(10,2) NOT NULL CHECK (base_price >= 0),
    travel_time_minutes INT NOT NULL CHECK (travel_time_minutes > 0)
);

CREATE TABLE IF NOT EXISTS trips (
    trip_id SERIAL PRIMARY KEY,
    route_id INT NOT NULL REFERENCES routes(route_id) ON DELETE CASCADE,
    departure_datetime TIMESTAMP NOT NULL,
    arrival_datetime TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'scheduled',
    CHECK (arrival_datetime > departure_datetime)
);

CREATE TABLE IF NOT EXISTS carriages (
    carriage_id SERIAL PRIMARY KEY,
    train_id INT NOT NULL REFERENCES trains(train_id) ON DELETE CASCADE,
    carriage_number INT NOT NULL,
    carriage_type VARCHAR(30) NOT NULL,
    seat_count INT NOT NULL CHECK (seat_count > 0),
    UNIQUE (train_id, carriage_number)
);

CREATE TABLE IF NOT EXISTS seats (
    seat_id SERIAL PRIMARY KEY,
    carriage_id INT NOT NULL REFERENCES carriages(carriage_id) ON DELETE CASCADE,
    seat_number INT NOT NULL,
    seat_class VARCHAR(30) NOT NULL,
    UNIQUE (carriage_id, seat_number)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount NUMERIC(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'new'
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    trip_id INT NOT NULL REFERENCES trips(trip_id) ON DELETE CASCADE,
    seat_id INT NOT NULL REFERENCES seats(seat_id),
    passenger_name VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    ticket_status VARCHAR(20) NOT NULL DEFAULT 'booked',
    UNIQUE (trip_id, seat_id)
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    payment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
    payment_method VARCHAR(30) NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'paid'
);