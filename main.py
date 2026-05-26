from flask import Flask, render_template, request, redirect, session
import requests

app = Flask(__name__)

# Secret key for session management
app.secret_key = "your_secret_key_here"

URL = "https://sharmaji.pythonanywhere.com"


@app.route("/")
def home():
    return render_template("index.html")


# =========================
# STUDENT DASHBOARD
# =========================
@app.route("/student")
def student():

    # User not logged in
    if "role" not in session:
        return redirect("/login")

    # Wrong role
    if session["role"] != "student":
        return redirect("/login")

    return render_template("student.html")


# =========================
# STAFF DASHBOARD
# =========================
@app.route("/staff")
def staff():

    if "role" not in session:
        return redirect("/login")

    if session["role"] != "staff":
        return redirect("/login")

    return render_template("staff.html")


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
def admin():

    if "role" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/login")

    return render_template("admin.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    # Already logged in
    if "role" in session:

        if session["role"] == "admin":
            return redirect("/admin")

        elif session["role"] == "student":
            return redirect("/student")

        else:
            return redirect("/staff")

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        response = requests.post(
            f"{URL}/login",
            json={
                "username": username,
                "password": password
            },
            timeout=5
        )

        # =========================
        # SUCCESSFUL LOGIN
        # =========================
        if response.status_code == 200:

            role = response.json().get("role")

            # Create session
            session["username"] = username
            session["role"] = role

            if role == "admin":
                return redirect("/admin")

            elif role == "student":
                return redirect("/student")

            else:
                return redirect("/staff")

        # =========================
        # INVALID LOGIN
        # =========================
        if response.status_code == 401:
            error = "Invalid username or password."

        elif response.status_code == 400:
            error = "Please fill in all the fields."

    return render_template("login.html", error=error)


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():

    # Destroy session
    session.clear()

    return redirect("/login")


# =========================
# RUN LOCALLY
# =========================
if __name__ == "__main__":
    app.run(debug=True)