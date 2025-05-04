from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import csv
import plotly
import plotly.express as px
import socket
import json
import pandas as pd

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATABASE = 'instance/products.db'


# Contribution by Krishna Desai - desaikri
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  product TEXT,
                  category TEXT,
                  sub_category TEXT,
                  brand TEXT,
                  sale_price REAL,
                  market_price REAL,
                  type TEXT,
                  rating REAL,
                  description TEXT)''')
    
    # Import CSV data if table is empty
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        with open('data/products.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                c.execute('''INSERT INTO products 
                            (product, category, sub_category, brand, sale_price, 
                             market_price, type, rating, description)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (row['product'], row['category'], row['sub_category'],
                           row['brand'], row['sale_price'], row['market_price'],
                           row['type'], row['rating'], row['description']))
    conn.commit()
    conn.close()

# Initialize database
init_db()

# @app.route('/')
# def login():
#     return render_template('login.html')

# Contribution by Manas Dani - madani
@app.route('/', methods=['GET', 'POST'])  # Add POST method
def login():
    if request.method == 'POST':
        # Simple authentication (no real validation)
        session['logged_in'] = True
        return redirect(url_for('dashboard'))  # Redirect properly
    return render_template('login.html')

# @app.route('/dashboard', methods=['POST'])
# def dashboard():
#     # Simple authentication (no real validation)
#     session['logged_in'] = True
#     return render_template('dashboard.html')

# Contribution by Manas Dani - madani
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Total product count
    c.execute("SELECT COUNT(*) FROM products")
    total_products = c.fetchone()[0]

    # Average rating
    c.execute("SELECT AVG(rating) FROM products")
    avg_rating = round(c.fetchone()[0], 2)

    # Top brand
    c.execute("SELECT brand, COUNT(*) as count FROM products GROUP BY brand ORDER BY count DESC LIMIT 1")
    top_brand = c.fetchone()[0]

    # Read full table to build graphs
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    # -------------------- Preview Graphs --------------------
    import plotly.express as px

    # 1. Average Sale Price per Category
    avg_price_df = df.groupby("category")["sale_price"].mean().sort_values(ascending=False).reset_index()
    fig1 = px.bar(avg_price_df, x="category", y="sale_price", title="Avg Sale Price per Category",
                  color_discrete_sequence=["#FDBA74"])  # Light orange

    # 2. Top 10 Brands
    top_brands = df["brand"].value_counts().nlargest(10)
    pie_colors = ["#FED7AA", "#FDBA74", "#FB923C", "#F97316", "#EA580C", "#C2410C", "#9A3412", "#7C2D12", "#78350F", "#5A1E0C"]
    fig2 = px.pie(names=top_brands.index, values=top_brands.values, title="Top 10 Brand Distribution",
                  color_discrete_sequence=pie_colors)

    # Aesthetic tweak: transparent background
    for fig in [fig1, fig2]:
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#1F2937"  # Tailwind's slate-800
        )

    preview_graphs = [
        fig1.to_html(full_html=False),
        fig2.to_html(full_html=False)
    ]

    # -------------------- Return to Dashboard Template --------------------
    return render_template(
        'dashboard.html',
        total_products=total_products,
        avg_rating=avg_rating,
        top_brand=top_brand,
        graphs=preview_graphs  # passed to HTML
    )

# Contribution by Krishna Desai - desaikri
@app.route('/view_data')
def view_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    per_page = 20
    page = int(request.args.get('page', 1))
    offset = (page - 1) * per_page

    # ORDER BY ascending now
    c.execute("SELECT COUNT(*) FROM products")
    total_rows = c.fetchone()[0]
    total_pages = (total_rows + per_page - 1) // per_page

    c.execute("SELECT * FROM products ORDER BY product_id ASC LIMIT ? OFFSET ?", (per_page, offset))
    data = c.fetchall()

    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)
    page_range = list(range(start_page, end_page + 1))

    conn.close()

    return render_template(
        'data.html',
        products=data,
        page=page,
        total_pages=total_pages,
        page_range=page_range
    )





from flask import Flask, render_template, request, redirect, url_for, session, flash

# Contribution by Krishna Desai - desaikri
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''INSERT INTO products 
                    (product, category, sub_category, brand, sale_price, 
                     market_price, type, rating, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (request.form['product'], request.form['category'],
                   request.form['sub_category'], request.form['brand'],
                   request.form['sale_price'], request.form['market_price'],
                   request.form['type'], request.form['rating'],
                   request.form['description']))
        conn.commit()
        conn.close()

        flash('✅ Product added successfully!')
        return redirect(url_for('view_data'))

    # 👇 Get brand list for suggestions
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT DISTINCT brand FROM products ORDER BY brand ASC")
    brands = [row[0] for row in c.fetchall()]
    conn.close()

    return render_template('add_data.html', brands=brands)


# Contribution by Manas Dani - madani
@app.route('/edit/<int:product_id>')
def edit_form(product_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM products WHERE product_id=?", (product_id,))
    product = c.fetchone()
    conn.close()
    return render_template('edit_data.html', product=product)

# Contribution by Manas Dani - madani
@app.route('/update/<int:product_id>', methods=['POST'])
def update_product(product_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''UPDATE products SET
                product=?, category=?, sub_category=?, brand=?,
                sale_price=?, market_price=?, type=?, rating=?, description=?
                WHERE product_id=?''',
             (request.form['product'], request.form['category'],
              request.form['sub_category'], request.form['brand'],
              request.form['sale_price'], request.form['market_price'],
              request.form['type'], request.form['rating'],
              request.form['description'], product_id))
    conn.commit()
    conn.close()
    return redirect(url_for('view_data'))

# Contribution by Krishna Desai - desaikri
@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE product_id=?", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_data'))

# Contribution by Krishna Desai - desaikri
@app.route('/stats')
def stats():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    # Light orange palette
    light_orange = '#FDBA74'
    peach = '#FEF3C7'
    text_color = '#1F2937'

    # 1. Average Sale Price by Category
    avg_price_df = df.groupby("category", as_index=False)["sale_price"].mean().sort_values("sale_price", ascending=False)
    fig1 = px.bar(avg_price_df, x="category", y="sale_price", title="Average Sale Price per Category",
                  color_discrete_sequence=[light_orange])
    fig1.update_layout(font_color=text_color)

    # 2. Top 10 Brands - Pie Chart
    top_brands = df['brand'].value_counts().nlargest(10)
    pie_colors = ['#FDBA74', '#FCD9A0', '#FFE0B2', '#FFEDD5', '#FEC89A',
                  '#FEF3C7', '#FFDAB9', '#FFE6CC', '#FFDEAD', '#FFF3E0']
    fig2 = px.pie(names=top_brands.index, values=top_brands.values,
                  title="Top 10 Brand Distribution",
                  color_discrete_sequence=pie_colors)
    fig2.update_layout(font_color=text_color)

    # 3. Product Rating Distribution
    fig3 = px.histogram(df, x="rating", nbins=10, title="Distribution of Product Ratings",
                        color_discrete_sequence=[light_orange])
    fig3.update_layout(font_color=text_color)

    # 4. Sale Price Spread by Category (Boxplot)
    fig4 = px.box(df, x="category", y="sale_price", title="Sale Price Spread by Category",
                  color_discrete_sequence=[light_orange])
    fig4.update_layout(font_color=text_color)

    # Transparent backgrounds to blend with dashboard
    for fig in [fig1, fig2, fig3, fig4]:
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

    graphs = [fig.to_html(full_html=False) for fig in [fig1, fig2, fig3, fig4]]
    return render_template('stats.html', graphs=graphs)


# Contribution by Manas Dani - madani
@app.route('/logout')
def logout():
    # Clear the session
    session.pop('logged_in', None)
    # Redirect to login page
    return redirect(url_for('login'))

def find_open_port(start=5000, max_tries=100):
    for port in range(start, start + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    raise OSError("No open ports found!")

# if __name__ == '__main__':
#     port = find_open_port()
#     print(f"🚀 Starting Flask app on http://127.0.0.1:{port}")
#     app.run(debug=True, port=port)
#
#
# if __name__ == '__main__':
#     app.run(debug=True)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", find_open_port()))
    print(f"🚀 Starting Flask app on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
