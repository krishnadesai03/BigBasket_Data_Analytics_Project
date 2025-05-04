# 📦 BigBasket Webapp

A lightweight Flask-based product inventory & analytics tool for small retailers.  
Add, edit, and delete products in an embedded SQLite database, then explore your catalog with interactive Plotly charts—all styled with Tailwind CSS and deployed to Render.com.

---

## 🚀 Features

- **CRUD Operations**  
  - Add new products via a dynamic form  
  - Edit existing products with pre-populated fields  
  - Delete unwanted products in one click  
- **Pagination**  
  - View products 20 at a time with seamless page controls  
- **Interactive Dashboard**  
  - Summary cards: Total Products, Avg. Rating, Top Brand  
  - Quick Insights charts (bar & pie) on the main dashboard  
- **Deep Analytics**  
  - **Avg Sale Price per Category** bar chart  
  - **Top 10 Brand Distribution** pie chart  
  - **Product Ratings** histogram  
  - **Sale Price Spread** box+scatter plot  
- **Authentication**  
  - Simple login/logout flow secured by a session `SECRET_KEY`  
- **Styling**  
  - Utility-first responsive design with **Tailwind CSS**  
- **Deployment**  
  - Auto-deploy on Git push via **Render.com** (Free tier)

---

## 💠 Tech Stack

- **Backend:** Python 3 & [Flask](https://flask.palletsprojects.com/)  
- **Database:** SQLite 3 (file at `instance/products.db`)  
- **Data:** pandas & Plotly Express  
- **Frontend:** Jinja2 templates + Tailwind CSS  
- **DevOps:** Git & GitHub → auto-deploy on Render.com  

---

## 📁 Project Structure

```
adt-main/
├── app.py                  # Flask app & routes
├── requirements.txt        # Python dependencies
├── Procfile                # (optional) for Heroku-style start
├── instance/
│   └── products.db         # SQLite database
├── data/
│   └── products.csv        # Seed data for DB
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── view_data.html
│   ├── add_data.html
│   ├── edit_data.html
│   └── stats.html
├── static/                 # Tailwind CSS, JS, images
└── README.md               # ← you are here
```

---

## ⚙️ Installation & Setup

1. **Clone the repo**  
   ```bash
   git clone https://github.com/DaniManas/BigBasket_WebApp.git
   cd bigbasket_WebApp
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # macOS/Linux
   # .\venv\Scripts\activate   # Windows PowerShell
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**  
   Create a `.env` file in the project root (and add it to `.gitignore`):
   ```env
   SECRET_KEY=<your-random-secret>
   FLASK_ENV=production
   ```
   Or set them in your shell:
   ```bash
   export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   export FLASK_ENV=production
   ```

5. **Run the app**  
   ```bash
   python app.py
   ```
   Then open your browser at `http://localhost:5000`.

---

## ☁️ Deployment on Render.com

1. Push your repo to GitHub.  
2. On Render, create a **New Web Service** linked to your GitHub repo.  
3. Set the **Start Command** to:
   ```bash
   python app.py
   ```
   Or for production:
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
4. Add the same environment variables (`SECRET_KEY`, `FLASK_ENV`) in Render’s **Environment** panel.  
5. Deploy—your live URL will be something like `https://bigbasket-webapp-1.onrender.com`.

---

## 🤝 Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/YourFeature`)  
3. Commit your changes (`git commit -m "Add YourFeature"`)  
4. Push to your fork (`git push origin feature/YourFeature`)  
5. Open a Pull Request on this repo  

Please follow the existing code style and include clear commit messages.

---

## 📄 License

This project is released under the [MIT License](LICENSE).

---

> Built with ❤️ by **Manas Dani** & **Krishna Desai**
