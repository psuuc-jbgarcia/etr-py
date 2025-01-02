from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import random

app = Flask(__name__)
app.secret_key = "yoursecretkey" # Random 10-digit number

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_crud_system'

mysql = MySQL(app)

# ---- Routes ----

# Login route
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()  # Fetch a single record
        cursor.close()

        if user:
            # Store user details in session
            session['logged_in'] = True
            session['user_id'] = user[0]  # Assuming id is the first column
            session['role'] = user[7]     # The role is in the 8th column (index 7)
            session['name'] = f"{user[1]} {user[2]}"  # first_name is in index 1, last_name in index 2
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


# Home route
@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template('index.html', name=session['name'], role=session['role'])

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Products management (CRUD for Regular User)
@app.route('/products', methods=['GET', 'POST'])
def products():
    if not session.get('logged_in') or session['role'] != 'regular':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        # Create a new product
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']
        status = request.form['status']

        cursor.execute("""
            INSERT INTO products (name, description, price, stock, category, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, description, price, stock, category, status))
        mysql.connection.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))

    cursor.execute("SELECT * FROM products")
    products_list = cursor.fetchall()
    cursor.close()

    return render_template('products.html', products=products_list, name=session['name'], role=session['role'])

@app.route('/product/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']
        status = request.form['status']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO products (name, description, price, stock, category, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, description, price, stock, category, status))
        mysql.connection.commit()
        cursor.close()
        flash('Product added successfully!', 'success')
        return redirect(url_for('products'))

    return render_template('add_product.html', name=session['name'], role=session['role'])


@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
    product = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']
        status = request.form['status']

        cursor.execute("""
            UPDATE products SET name = %s, description = %s, price = %s, stock = %s, category = %s, status = %s
            WHERE id = %s
        """, (name, description, price, stock, category, status, id))
        mysql.connection.commit()
        cursor.close()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products'))

    cursor.close()
    return render_template('edit_product.html', product=product, name=session['name'], role=session['role'])


# Route to delete a product
@app.route('/product/delete/<int:id>')
def delete_product(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Product deleted successfully!', 'danger')
    return redirect(url_for('products'))

@app.route('/about')
def about():
    # Ensure the user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Get the current user's ID from the session
    user_id = session['user_id']

    # Query the database for the user's information
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()  # Fetch user data
    cursor.close()

    if user:
        # Pass the user data to the template
        return render_template('about.html', user=user, name=session['name'], role=session['role'])
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('home'))
@app.route('/customers', methods=['GET'])
def customers():
    if not session.get('logged_in') or session['role'] != 'admin':
        return redirect(url_for('login'))

    # Fetch all customers from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customers")
    customers_list = cursor.fetchall()
    cursor.close()

    return render_template('customers.html', customers=customers_list, name=session['name'], role=session['role'])

# Route to add a new customer (Admin only)
@app.route('/customer/add', methods=['GET', 'POST'])
def add_customer():
    if not session.get('logged_in') or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get data from the form
        full_name = request.form['full_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        account_status = request.form['account_status']
        registration_date = request.form['registration_date']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO customers (full_name, email, phone_number, address, account_status, registration_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (full_name, email, phone_number, address, account_status, registration_date))
        mysql.connection.commit()
        cursor.close()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('customers'))

    return render_template('add_customer.html')

# Route to edit a customer (Admin only)
@app.route('/customer/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    if not session.get('logged_in') or session['role'] != 'admin':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = %s", (id,))
    customer = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        # Get updated data from the form
        full_name = request.form['full_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        account_status = request.form['account_status']
        registration_date = request.form['registration_date']

        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE customers
            SET full_name = %s, email = %s, phone_number = %s, address = %s, account_status = %s, registration_date = %s
            WHERE id = %s
        """, (full_name, email, phone_number, address, account_status, registration_date, id))
        mysql.connection.commit()
        cursor.close()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customers'))

    return render_template('edit_customer.html', customer=customer)

# Route to delete a customer (Admin only)
@app.route('/customer/delete/<int:id>')
def delete_customer(id):
    if not session.get('logged_in') or session['role'] != 'admin':
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM customers WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    flash('Customer deleted successfully!', 'danger')
    return redirect(url_for('customers'))

if __name__ == '__main__':
    app.run(debug=True)
