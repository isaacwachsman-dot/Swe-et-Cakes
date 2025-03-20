from flask import Flask, render_template, redirect, request, session, url_for
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a real secret key in production!

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='myapp',
        user='postgres',
        password='password'
    )
    return conn

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid username or password', 400
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['first_name']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        
        if existing_user:
            return 'Username already exists', 400
        
        cur.execute("INSERT INTO users (username, password, first_name) VALUES (%s, %s, %s)",
                    (username, password, name))
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT first_name FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        return render_template('dashboard.html', name=user[0])
    
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
