from flask import Flask, flash, jsonify, render_template, request, redirect, session, url_for
import mysql.connector
from decimal import Decimal, ROUND_HALF_UP

app = Flask(__name__)
app.config['SECRET_KEY'] = '6205702651'

# Azure MySQL database connection details
config = {
'user': 'hr1',
'password': 'Himanshu198@',
'host': 'nodeeap.mysql.database.azure.com',
'database': 'login_credentials',
#'ssl_ca': 'ssl/BaltimoreCyberTrustRoot.crt.pem',
}

# Azure MySQL Database Configuration - Product Management
product_management_config = {
'user': 'hr1',
'password': 'Himanshu198@',
'host': 'nodeeap.mysql.database.azure.com',
'database': 'product_management', # Database name for product management
'port': 3306
}

# Home page
@app.route('/')
def home():
  cart = session.get('cart', [])
  # Check if user is logged in
  if 'email' in session:
    session['cart'] = cart
    firstname = session['firstname']
    return render_template('index.html', firstname=firstname, cart=cart)
  
  
  return render_template('index.html')

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'POST':
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    
    # Connect to the Azure MySQL database
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Insert user data into the 'users' table
    sql = "INSERT INTO users (firstname, lastname, email, password) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (firstname, lastname, email, password))
      
    # Commit the changes and close the connection
    conn.commit()

    #Store user details in session
    session['email'] = email
    session['firstname'] = firstname

    cursor.close()
    conn.close()

    return redirect('/login')

  return render_template('signup.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    
  
    # Connect to the Azure MySQL database
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Retrieve user data from the 'users' table
    sql = "SELECT * FROM users WHERE email = %s AND password = %s"
    cursor.execute(sql, (email, password))

    # Fetch the user data
    user = cursor.fetchone()


    if user:
      session['email'] = email
      session['firstname'] = user[1]
      session['user_id'] = user[0]

    # Close the connection
      cursor.close()
      conn.close()
      

      # User found, redirect to a success page
      return redirect('/')
    else:
      # User not found, show an error message
      error = 'Invalid credentials. Please try again.'
      return render_template('login.html', error=error)

  return render_template('login.html')

# Success page
@app.route('/success')
def success():
  return 'Login successful!'

@app.route('/logout')
def logout():
# Clear user session and redirect to home page
  session.clear()
  return redirect(url_for('home'))

#about page route
@app.route('/about')
def about():
   return render_template('about.html')

@app.route('/products/')

def products():

    # Get the search query from the URL parameters
    search_query = request.args.get('query', '')
    
    # Connect to Azure MySQL Database
    conn = mysql.connector.connect(**product_management_config)
    cursor = conn.cursor()

    # Fetch product details from the database based on product_id
    
    query = "SELECT * FROM products WHERE name LIKE %s"
    params = ('%' + search_query + '%',)
    cursor.execute(query, params)
    products = cursor.fetchall()
  
    cursor.close()
    cart = session.get('cart', [])

    return render_template('products.html', products=products, cart=cart)

# Add to Cart
@app.route('/add_to_cart/<int:product_id>/<int:quantity>', methods=['POST'])
def add_to_cart(product_id, quantity):
    # Convert product_id to string before storing in session
    product_id_str = str(product_id)
    
    # Connect to Azure MySQL Database
    conn = mysql.connector.connect(**product_management_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    cart = session.get('cart', [])

    if product:
        for item in cart:
            if item['id'] == product_id_str:
                # Product is already in the cart, update the quantity
                item['quantity'] += quantity
                break
        else:
            # Product is not in the cart, add it as a new item
            item = {
                'id': product_id_str,
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity
            }
            cart.append(item)

        # Update the cart in the session
        session['cart'] = cart

        flash('Product added to cart successfully!', 'success')
        return {'success': True}
    else:
        flash('Product not found!', 'error')
        return {'success': False}


'''
# Add to Cart
@app.route('/add_to_cart/<int:product_id>/<int:quantity>', methods=['POST'])
def add_to_cart(product_id, quantity):
   # Convert product_id to string before storing in session
    product_id_str = str(product_id)
    
    # Connect to Azure MySQL Database
    conn = mysql.connector.connect(**product_management_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    cart = session.get('cart', [])

    if product:
        item = {
            'id': product_id_str,
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity
        }
      

        # Retrieve the cart from the session or initialize it if empty
        cart = session.get('cart', [])
        cart.append(item)


        # Update the cart in the session
        session['cart'] = cart
  
        flash('Product added to cart successfully!', 'success')
        return {'success': True}
    else:
        flash('Product not found!', 'error')
        return {'sucess': False}
 '''

# Update Quantity
@app.route('/update_quantity/<int:product_id>/<action>', methods=['POST'])
def update_quantity(product_id, action):
    cart = session.get('cart', [])

    for item in cart:
        if item['id'] == str(product_id):
            if action == 'increase':
                item['quantity'] += 1
            elif action == 'decrease':
                if item['quantity'] > 1:
                    item['quantity'] -= 1

    # Update the cart in the session
    session['cart'] = cart
    return {'success': True}

# Remove from Cart
@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])

    for item in cart:
        if item['id'] == str(product_id):
            cart.remove(item)
            break

    # Update the cart in the session
    session['cart'] = cart
    return {'success': True}

# Cart Page
@app.route('/cart')
def cart_page():
  
  if 'email' in session:
      
    cart = session.get('cart', [])
    cart_total = Decimal(0)
    
    for item in cart:
        price = Decimal(item['price'])
        quantity = int(item['quantity'])
        item_total = price * quantity
        cart_total += item_total

    cart_total = cart_total.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    
    return render_template('cart.html', cart=cart, cart_total=cart_total)
  
  else:
    # User is not logged in, redirect to the login page with a flash message
    flash("Please sign in to add products to the cart or view the cart.")
    return redirect(url_for('login'))

# Product description page
@app.route('/products/<int:product_id>')
def product_description(product_id):
    # Fetch product data from the database using the product_id
    # You need to implement the logic to fetch product data from the database here
    # Connect to Azure MySQL Database
    conn = mysql.connector.connect(**product_management_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if product is None:
        # Product not found
        return render_template('404.html'), 404
    
    return render_template('description.html', product=product)



# Route for the Address Page
@app.route('/address', methods=['GET', 'POST'])
def address():
    if request.method == 'POST':
        # Retrieve the address data from the form
        name = request.form['name']
        phone_number = request.form['phone_number']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']

        # Get the user_id from the session
        user_id = session.get('user_id')
        print("User ID:", user_id) 

        if not user_id:
            flash('Please sign in to submit the address.', 'warning')
            return redirect('/login')

        try:
            # Connect to the 'product_management' database to store the address
            conn_product = mysql.connector.connect(**product_management_config)
            cursor_product = conn_product.cursor()
            

            # Insert the address data into the 'address_details' table
            sql_insert_address = "INSERT INTO address_details (user_id, name, phone_number, address, city, state, zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (user_id, name, phone_number, address, city, state, zipcode)
            cursor_product.execute(sql_insert_address, values)
            conn_product.commit()

            # Get the address_id of the inserted row
            address_id = cursor_product.lastrowid

            # Store the address_id in the session
            session['address_id'] = address_id

            
            cursor_product.close()
            conn_product.close()
            
            
            # Redirect to the payment page after successful data storage
            return redirect('/payment')

        except Exception as e:
            # Handle any errors that occur during database operations
            flash('An error occurred while storing the address.', 'danger')
            print(f"Error: {e}")

    return render_template('address.html')


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    cart = session.get('cart', [])
    cart_total = Decimal(0)

    for item in cart:
        price = Decimal(item['price'])
        quantity = int(item['quantity'])
        item_total = price * quantity
        cart_total += item_total

    cart_total = cart_total.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    user_id = session.get('user_id')

    if request.method == 'POST':
        # If the form has been submitted, process the payment and store order details in the database
        try:
            address_id = session.get('address_id')

            # Connect to the 'product_management' database to store the order details
            conn = mysql.connector.connect(**product_management_config)
            cursor = conn.cursor()

            # Insert the order details into the order_details table
            for item in cart:
                product_name = item['name']
                price = Decimal(item['price'])
                quantity = int(item['quantity'])
                total_price = price * quantity

                # Prepare the SQL query for inserting data into the order_details table
                insert_query = (
                    "INSERT INTO order_details (user_id, address_id, product_name, quantity, price, total_price) VALUES (%s, %s, %s, %s, %s, %s)"
                )
                values = (user_id, address_id, product_name, quantity, price, total_price)
                cursor.execute(insert_query, values)

            # Commit the changes to the database
            conn.commit()

            # Close the database connection
            cursor.close()
            conn.close()

            # Clear the cart from the session after successful order placement
            session['cart'] = []

            # Show a flash message after successful payment and order placement
            flash('Thank You! Your order has been placed. It will reach you soon.', 'success')
            return redirect('/payment_success')

        except Exception as e:
            # Handle any errors that occur during database operations
            flash('An error occurred while processing your order.', 'danger')
            print(f"Error: {e}")

    return render_template('payment.html', cart=cart, cart_total=cart_total)

# Route for the Payment Success Page
@app.route('/payment_success', methods=['GET'])
def payment_success():
    return render_template('payment_success.html')


if __name__ == '__main__':
  app.run(debug=True)