CREATE TABLE IF NOT EXISTS passengers (
    passenger_id SERIAL PRIMARY KEY,
    passport_num INTEGER,
    full_name VARCHAR(255) NOT NULL,
    phone INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS aircrafts (
    aircraft_id SERIAL PRIMARY KEY,
    registration_num VARCHAR(255),
    model VARCHAR(255) NOT NULL,
    manufacture_date DATE NOT NULL,
    ready_for_dep BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS routes (
    route_id SERIAL PRIMARY KEY,
    dep_airport VARCHAR(255),
    arr_airport VARCHAR(255) NOT NULL,
    ticket_price INTEGER NOT NULL,
    duration INTEGER NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS flights (
    flight_id SERIAL PRIMARY KEY,
    departure TIMESTAMP WITH TIME ZONE,
    is_cancelled BOOLEAN NOT NULL,
    aircraft_id SERIAL,
    route_id SERIAL,
    FOREIGN KEY (aircraft_id) REFERENCES aircrafts(aircraft_id),
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

CREATE TABLE IF NOT EXISTS flights_x_passengers (
    flight_id SERIAL,
    passenger_id SERIAL,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
	CONSTRAINT pkey PRIMARY KEY (flight_id, passenger_id)
);

CREATE TABLE IF NOT EXISTS pilots (
    pilot_id SERIAL PRIMARY KEY,
    flight_time INTEGER CHECK (flight_time >= 0),
    full_name VARCHAR(255) NOT NULL,
    phone INTEGER NOT NULL,
    aircraft_id SERIAL,
    FOREIGN KEY (aircraft_id) REFERENCES aircrafts(aircraft_id)
);