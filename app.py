from functools import wraps
import csv
from io import StringIO

from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from db import get_connection


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                flash('Сначала выполните вход в систему.')
                return redirect(url_for('login'))
            return view(*args, **kwargs)
        return wrapped

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            full_name = request.form['full_name'].strip()
            email = request.form['email'].strip().lower()
            password = request.form['password']

            if not full_name or not email or not password:
                flash('Все поля обязательны для заполнения.')
                return render_template('register.html')

            password_hash = generate_password_hash(password)
            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute('SELECT user_id FROM users WHERE email = %s', (email,))
                existing = cur.fetchone()
                if existing:
                    flash('Пользователь с таким email уже существует.')
                    return render_template('register.html')

                cur.execute(
                    '''
                    INSERT INTO users (full_name, email, password_hash)
                    VALUES (%s, %s, %s)
                    ''',
                    (full_name, email, password_hash)
                )
                conn.commit()
                flash('Регистрация успешно завершена.')
                return redirect(url_for('login'))
            finally:
                cur.close()
                conn.close()

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email'].strip().lower()
            password = request.form['password']

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    '''
                    SELECT user_id, full_name, password_hash, role
                    FROM users
                    WHERE email = %s
                    ''',
                    (email,)
                )
                user = cur.fetchone()
            finally:
                cur.close()
                conn.close()

            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['user_id']
                session['full_name'] = user['full_name']
                session['role'] = user['role']
                flash('Вход выполнен успешно.')
                return redirect(url_for('search_trips'))

            flash('Неверный email или пароль.')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Вы вышли из системы.')
        return redirect(url_for('index'))

    @app.route('/search', methods=['GET', 'POST'])
    def search_trips():
        trips = []
        departure_station = ''
        arrival_station = ''
        date = ''

        if request.method == 'POST':
            departure_station = request.form['departure_station'].strip()
            arrival_station = request.form['arrival_station'].strip()
            date = request.form['date']

            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    '''
                    SELECT
                        t.trip_id,
                        tr.train_number,
                        tr.train_name,
                        s1.station_name AS departure_station,
                        s2.station_name AS arrival_station,
                        t.departure_datetime,
                        t.arrival_datetime,
                        r.base_price
                    FROM trips t
                    JOIN routes r ON t.route_id = r.route_id
                    JOIN trains tr ON r.train_id = tr.train_id
                    JOIN stations s1 ON r.departure_station_id = s1.station_id
                    JOIN stations s2 ON r.arrival_station_id = s2.station_id
                    WHERE LOWER(s1.city) = LOWER(%s)
                    AND LOWER(s2.city) = LOWER(%s)
                    AND DATE(t.departure_datetime) = %s
                    AND t.status = 'scheduled'
                    ORDER BY t.departure_datetime
                    ''',
                    (departure_station, arrival_station, date)
                )
                trips = cur.fetchall()
            finally:
                cur.close()
                conn.close()

        return render_template(
            'search.html',
            trips=trips,
            departure_station=departure_station,
            arrival_station=arrival_station,
            date=date
        )

    @app.route('/book/<int:trip_id>', methods=['GET', 'POST'])
    @login_required
    def book_ticket(trip_id):
        conn = get_connection()
        cur = conn.cursor()
        try:
            if request.method == 'POST':
                seat_id = int(request.form['seat_id'])
                passenger_name = request.form['passenger_name'].strip()
                price = request.form['price']

                if not passenger_name:
                    flash('Введите ФИО пассажира.')
                    return redirect(url_for('book_ticket', trip_id=trip_id))

                cur.execute(
                    '''
                    INSERT INTO orders (user_id, status)
                    VALUES (%s, 'new')
                    RETURNING order_id
                    ''',
                    (session['user_id'],)
                )
                order_id = cur.fetchone()['order_id']

                cur.execute(
                    '''
                    INSERT INTO tickets (
                        order_id, trip_id, seat_id, passenger_name, price, ticket_status
                    )
                    VALUES (%s, %s, %s, %s, %s, 'paid')
                    ''',
                    (order_id, trip_id, seat_id, passenger_name, price)
                )

                cur.execute(
                    '''
                    INSERT INTO payments (order_id, amount, payment_method, payment_status)
                    VALUES (%s, %s, 'card', 'paid')
                    ''',
                    (order_id, price)
                )

                conn.commit()
                flash('Билет успешно оформлен.')
                return redirect(url_for('my_tickets'))

            cur.execute(
                '''
                SELECT trip_id, seat_id, carriage_number, seat_number, seat_class
                FROM available_seats_view
                WHERE trip_id = %s
                ORDER BY carriage_number, seat_number
                ''',
                (trip_id,)
            )
            seats = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        return render_template('booking.html', seats=seats, trip_id=trip_id)

    @app.route('/my_tickets')
    @login_required
    def my_tickets():
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''
                SELECT
                    tk.ticket_id,
                    tk.passenger_name,
                    tk.price,
                    tk.ticket_status,
                    tr.train_number,
                    s1.station_name AS departure_station,
                    s2.station_name AS arrival_station,
                    t.departure_datetime
                FROM tickets tk
                JOIN orders o ON tk.order_id = o.order_id
                JOIN trips t ON tk.trip_id = t.trip_id
                JOIN routes r ON t.route_id = r.route_id
                JOIN trains tr ON r.train_id = tr.train_id
                JOIN stations s1 ON r.departure_station_id = s1.station_id
                JOIN stations s2 ON r.arrival_station_id = s2.station_id
                WHERE o.user_id = %s
                ORDER BY t.departure_datetime DESC
                ''',
                (session['user_id'],)
            )
            tickets = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        return render_template('my_tickets.html', tickets=tickets)

    @app.route('/export_my_tickets')
    @login_required
    def export_my_tickets():
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''
                SELECT
                    tk.ticket_id,
                    tk.passenger_name,
                    tr.train_number,
                    s1.station_name AS departure_station,
                    s2.station_name AS arrival_station,
                    t.departure_datetime,
                    tk.price,
                    tk.ticket_status
                FROM tickets tk
                JOIN orders o ON tk.order_id = o.order_id
                JOIN trips t ON tk.trip_id = t.trip_id
                JOIN routes r ON t.route_id = r.route_id
                JOIN trains tr ON r.train_id = tr.train_id
                JOIN stations s1 ON r.departure_station_id = s1.station_id
                JOIN stations s2 ON r.arrival_station_id = s2.station_id
                WHERE o.user_id = %s
                ORDER BY t.departure_datetime DESC
                ''',
                (session['user_id'],)
            )
            rows = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'ticket_id',
            'passenger_name',
            'train_number',
            'departure_station',
            'arrival_station',
            'departure_datetime',
            'price',
            'ticket_status'
        ])

        for row in rows:
            writer.writerow([
                row['ticket_id'],
                row['passenger_name'],
                row['train_number'],
                row['departure_station'],
                row['arrival_station'],
                row['departure_datetime'],
                row['price'],
                row['ticket_status']
            ])

        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=my_tickets.csv'
        return response

    @app.route('/admin', methods=['GET', 'POST'])
    @login_required
    def admin():
        if session.get('role') != 'admin':
            flash('Доступ разрешён только администратору.')
            return redirect(url_for('index'))

        conn = get_connection()
        cur = conn.cursor()
        try:
            if request.method == 'POST':
                train_number = request.form['train_number'].strip()
                train_name = request.form['train_name'].strip()
                train_type = request.form['train_type'].strip()

                if not train_number or not train_name or not train_type:
                    flash('Все поля формы добавления поезда обязательны.')
                else:
                    cur.execute(
                        '''
                        INSERT INTO trains (train_number, train_name, train_type)
                        VALUES (%s, %s, %s)
                        ''',
                        (train_number, train_name, train_type)
                    )
                    conn.commit()
                    flash('Поезд успешно добавлен.')

            cur.execute('SELECT * FROM trains ORDER BY train_number')
            trains = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        return render_template('admin.html', trains=trains)

    @app.route('/export_trains')
    @login_required
    def export_trains():
        if session.get('role') != 'admin':
            flash('Доступ разрешён только администратору.')
            return redirect(url_for('index'))

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                '''
                SELECT train_id, train_number, train_name, train_type
                FROM trains
                ORDER BY train_number
                '''
            )
            rows = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['train_id', 'train_number', 'train_name', 'train_type'])

        for row in rows:
            writer.writerow([
                row['train_id'],
                row['train_number'],
                row['train_name'],
                row['train_type']
            ])

        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=trains_report.csv'
        return response

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)