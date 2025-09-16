import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)
DATABASE = 'users.db'

def init_db():
    """A helper function to create and populate the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('alpha03', 'password@123'))
    conn.commit()
    conn.close()


HTML_TEMPLATE_VULN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Vulnerable Login</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f4f9; display: grid; place-content: center; min-height: 100vh; margin: 0; }
        .container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        h2 { color: #333; }
        input[type="text"] { font-size: 1rem; padding: 8px; width: 250px; margin-bottom: 1rem; border: 1px solid #ccc; border-radius: 4px; }
        input[type="submit"] { font-size: 1rem; padding: 10px 20px; border: none; background-color: #007bff; color: white; border-radius: 4px; cursor: pointer; }
        input[type="submit"]:hover { background-color: #0056b3; }
        .result { margin-top: 1.5rem; padding: 1rem; border: 1px solid #ddd; background-color: #e9e9e9; font-family: monospace; text-align: left; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login Portal</h2>
        <p>Enter your username to proceed.</p>
        <form action="/vulnerable" method="POST">
            <label for="username">Username:</label><br>
            <input type="text" id="username" name="username" autofocus>
            <br>
            <input type="submit" value="Submit">
        </form>
        
        <div class="result">
            {{ result | safe }}
        </div>
    </div>
</body>
</html>
"""

HTML_TEMPLATE_SECURE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Secure Login</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f4f9; display: grid; place-content: center; min-height: 100vh; margin: 0; }
        .container { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        h2 { color: #333; }
        input[type="text"] { font-size: 1rem; padding: 8px; width: 250px; margin-bottom: 1rem; border: 1px solid #ccc; border-radius: 4px; }
        input[type="submit"] { font-size: 1rem; padding: 10px 20px; border: none; background-color: #007bff; color: white; border-radius: 4px; cursor: pointer; }
        input[type="submit"]:hover { background-color: #0056b3; }
        .result { margin-top: 1.5rem; padding: 1rem; border: 1px solid #ddd; background-color: #e9e9e9; font-family: monospace; text-align: left; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login Portal</h2>
        <p>Enter your username to proceed.</p>
        <form action="/secure" method="POST">
            <label for="username">Username:</label><br>
            <input type="text" id="username" name="username" autofocus>
            <br>
            <input type="submit" value="Submit">
        </form>
        
        <div class="result">
            {{ result | safe }}
        </div>
    </div>
</body>
</html>
"""


@app.route('/vulnerable', methods=['GET', 'POST'])
def vuln_login():
    """Handles both displaying the form and processing the login."""
    result_message = "Awaiting submission..."
    
    if request.method == 'POST':
        username = request.form['username']
        query = f"SELECT * FROM users WHERE username = '{username}'"
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            user = cursor.fetchone()
        except sqlite3.Error as e:
            user = None
            result_message = f"An SQL error occurred: {e}"

        conn.close()
        
        result_html = f"<p><strong>Executed Query:</strong><br>{query}</p><hr>"
        if user:
            result_html += f"<h1>✅ Access Granted</h1><p>Welcome, {user[1]}!</p>"
        else:
            if "SQL error" not in result_message:
                 result_html += "<h1>❌ Access Denied</h1><p>Invalid username.</p>"
            else:
                 result_html += f"<h1>❌ Query Failed</h1><p>{result_message}</p>"
        
        result_message = result_html

    return render_template_string(HTML_TEMPLATE_VULN, result=result_message)


@app.route('/secure', methods=['GET', 'POST'])
def secure_login():
    """Handles both displaying the form and processing the login."""
    result_message = "Awaiting submission..."
    
    if request.method == 'POST':
        username = request.form['username']
        query = f"SELECT * FROM users WHERE username = ?"
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, (username,))
            user = cursor.fetchone()
        except sqlite3.Error as e:
            user = None
            result_message = f"An SQL error occurred: {e}"

        conn.close()
        
        result_html = f"<p><strong>Executed Query:</strong><br>{query}</p><hr>"
        if user:
            result_html += f"<h1>✅ Access Granted</h1><p>Welcome, {user[1]}!</p>"
        else:
            if "SQL error" not in result_message:
                 result_html += "<h1>❌ Access Denied</h1><p>Invalid username.</p>"
            else:
                 result_html += f"<h1>❌ Query Failed</h1><p>{result_message}</p>"
        
        result_message = result_html

    return render_template_string(HTML_TEMPLATE_SECURE, result=result_message)


if __name__ == '__main__':
    print("Initializing the database...")
    init_db()
    print("Database 'users.db' created with sample data.")
    # print("Starting Flask server at http://127.0.0.1:5000")
    app.run(debug=True)
