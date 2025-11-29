# 🔧 Streamlit CRUD App (SQLite Version)

This is a simple, fully functional **Streamlit web app** for performing:

- **CRUD operations** (Create, Read, Update, Delete)
- A real-world **SQL transaction**: transferring values between rows using safe, rollback-enabled logic

It uses a **SQLite database** and is designed for **educational use**, ideal for learning database logic and deploying on **Streamlit Community Cloud**.

---

## 📦 Project Structure

```
.
├── streamlit_app.py      ✅ Main app (auto-detected by Streamlit Cloud)
├── config.py             ✅ Table & DB settings
├── database.sqlite       ✅ Sample database
├── requirements.txt      ✅ Dependencies
└── README.md             ✅ Updated with correct filename
```

---

## 🚀 Step-by-Step Guide (For Students)

### ✅ Step 1: Run the App Locally First

Before deploying anything, get it working on your own machine.

#### 🧰 Requirements:
- Python 3.8+
- pip (Python package installer)

#### 🔧 Setup Instructions:

1. Clone or download this repo
2. Open a terminal in the repo folder
3. Run:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`.

Explore the sample app with preloaded users (`Alice`, `Bob`, `Charlie`). Try adding, editing, deleting users.

---

### ☁️ Step 2: Deploy the Working Example to the Cloud

#### First, Make It Your Own:

1. Click the **"Use this template"** button on GitHub (top right)
2. Create a copy of the repo under:
   - Your **personal GitHub account** or
   - A **school/org-owned GitHub org**
3. Once your copy is created, clone it to your local machine if needed

#### Then Deploy:

1. Visit: [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Log in and click **"New app"**
3. Connect your newly created GitHub repo
4. Select the main branch and click **Deploy**

🎉 You now have a live CRUD app running with:
- A sample SQLite DB (`database.sqlite`)
- Features:
  - Add, edit, delete users

---

### 🔍 Step 3: Explore the Sample App

Open your deployed app in the browser and try the following:

- Add a new user
- Edit an existing user's name or age
- Delete someone from the list

This gives you a feel for how the app works before using your own data.

---

### 🔁 Step 4: Test the "Transfer Age" Transaction

After customizing your app with your own database and deploying it, scroll to the section titled:

> **"Transfer Age Between Users (Transactional)"**

#### What It Does:
- Transfers a specified number of "age years" from one user to another.
- Both updates occur in a **single transaction** — if anything fails, nothing is changed.

#### ✅ To Try It:
1. Select a user in the **"From (User ID)"** dropdown.
2. Select a different user in the **"To (User ID)"** dropdown.
3. Enter an age value to transfer (e.g. `2`).
4. Click **"Transfer Age"**.

#### ⚠️ Edge Cases:
- If the **"from" user** doesn’t have enough age, the transaction fails.
- Selecting the same user for both fields is prevented.
- Errors are displayed clearly, and the DB rolls back automatically.

---

### ⚙️ Step 5: Update Config for Your Own Table

When you're ready to use your own database:

1. Open `config.py` and update:
   - `DB_PATH` to your new `.sqlite` file name
   - `TABLE_NAME` to match your own table
   - `COLUMNS` with the field names (excluding `id`)

2. Replace `database.sqlite` with your exported version.

---

### 🔄 Step 6: Export Your MySQL DB to SQLite

Use a tool like DB Browser for SQLite, or try this approach:

```bash
# Export MySQL to SQL
mysqldump -u your_user -p your_db > dump.sql

# Convert SQL to SQLite (optional method)
pip install sqlite-utils
sqlite-utils convert dump.sql database.sqlite
```

Once your new `.sqlite` file is in place, commit the change to GitHub — your deployed app will automatically update.

---

## 📬 For Educators

This template is meant for:
- Class projects
- Assignments with database components
- Lightweight app demos with local DBs

Want more private app slots or memory on Streamlit Cloud? Contact: `support@streamlit.io`

---

⚠️ Heads-up: When deployed to Streamlit Cloud, your data won’t persist between app restarts or redeploys.
This is because the app reloads the original database file from GitHub each time.

✅ If you want to keep your data:
	•	Run the app locally (streamlit run streamlit_app.py)
	•	Or use a cloud-hosted database (like Supabase or MySQL)

---