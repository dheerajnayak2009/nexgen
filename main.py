from flask import Flask, render_template, request, redirect
import requests

app = Flask(__name__)

URL = "https://sharmaji.pythonanywhere.com"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/student")
def student():
    return render_template("student.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        response = requests.post(f"{URL}/login",
                    json = {
                        "username" : username,
                        "password" : password
                    }, timeout=5)
        
        if response.status_code == 200:  # Successful login
            if response.json().get('role') == 'admin':
                return redirect("/admin")  # Redirect to admin dashboard
            elif response.json().get('role') == 'student':
                return redirect("/student")  # Redirect to student dashboard
            else:
                return redirect("/staff")  # Redirect to staff dashboard
        
        if response.status_code == 401:  # Invalid credentials
            return "Invalid username or password. Please try again."
        
        if response.status_code == 400: # Missing fields(empty data sent to sharmaji)
            return "Please fill in all the fields."
            
    return render_template("login.html")

# --- IF LOCAL, THEN UNCOMMENT THIS ---

# if __name__ == "__main__":
#     app.run(debug=True)