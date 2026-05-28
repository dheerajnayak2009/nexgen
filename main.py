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
    

    return render_template("student.html",
                            first_name=session.get("first_name"),
                            last_name=session.get("last_name"),
                            roll_number=session.get("roll_number"),
                            email=session.get("email"),
                            student_phone=session.get("student_phone"),
                            parent_phone=session.get("parent_phone"),
                            stream=session.get("stream"),
                            target_year=session.get("target_year"),
                            gender=session.get("gender"),
                            username=session.get("username"),
                            batch_name=session.get("batch_name")
                           )


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

        data = request.get_json(silent=True) or {}

        username = data.get("username")
        password = data.get("password")

        fingerprint = data.get("fingerprint", {})

        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
        user_agent = request.headers.get("User-Agent")

        response = requests.post(
        f"{URL}/login",
        json={
            "username": username,
            "password": password,

            "ip_address": ip_address,
            "forwarded_for": request.headers.get("X-Forwarded-For"),
            "host": request.headers.get("Host"),
            "origin": request.headers.get("Origin"),
            "referer": request.headers.get("Referer"),

            "user_agent": user_agent,
            "accept_language": request.headers.get("Accept-Language"),
            "sec_ch_ua": request.headers.get("Sec-CH-UA"),
            "sec_ch_platform": request.headers.get("Sec-CH-UA-Platform"),
            "sec_ch_mobile": request.headers.get("Sec-CH-UA-Mobile"),

            "method": request.method,
            "path": request.path,

            "fingerprint": fingerprint
        },
        timeout=5
    )
        # =========================
        # SUCCESSFUL LOGIN
        # =========================
        if response.status_code == 200:

            role = response.json().get("role")

            session["username"] = username
            session["role"] = role

            if role == "admin":
                session["token"] = response.json().get("access_token")

            elif role == "student":

                session["first_name"] = response.json().get("first_name")
                session["last_name"] = response.json().get("last_name")
                session["roll_number"] = response.json().get("roll_number")
                session["email"] = response.json().get("email")
                session["student_phone"] = response.json().get("student_phone")
                session["parent_phone"] = response.json().get("parent_phone")
                session["stream"] = response.json().get("stream")
                session["target_year"] = response.json().get("target_year")
                session["gender"] = response.json().get("gender")
                session["batch_name"] = response.json().get("batch_name")

            return {
                "success": True,
                "role": role
            }, 200

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
# ADMIN: REGISTER STUDENT   
# =========================
@app.route("/admin/register-student", methods=["GET", "POST"])
def register_student():

    # Admin protection
    if "role" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/login")

    error = None
    success = None

    if request.method == "POST":

        response = requests.post(
            f"{URL}/register_student",
            json={
                "username": request.form.get("username"),
                "password": request.form.get("password"),
                "first_name": request.form.get("first_name"),
                "last_name": request.form.get("last_name"),
                "roll_number": request.form.get("roll_number"),
                "batch_name": request.form.get("batch_name"),
                "email": request.form.get("email"),
                "student_phone": request.form.get("student_phone"),
                "parent_phone": request.form.get("parent_phone"),
                "stream": request.form.get("stream"),
                "target_year": request.form.get("target_year"),
                "gender": request.form.get("gender"),
                # "current_role": session["role"]
            },
            timeout=5, 
            headers={"Authorization": f"Bearer {session.get('token')}"}
        )

        if response.status_code == 201:
            success = "Student registered successfully"

        else:
            error = response.json().get("error")

    return render_template(
        "register_student.html",
        error=error,
        success=success
    )

@app.route("/admin/create-batch", methods=["GET", "POST"])
def create_batch():

    # Admin protection
    if "role" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/login")

    error = None
    success = None

    if request.method == "POST":

        response = requests.post(
            f"{URL}/add_batch",
            json={
                "batch_name": request.form.get("batch_name"),
                "course": request.form.get("course"),
                "year": request.form.get("year")
            },
            timeout=5,
            headers={"Authorization": f"Bearer {session.get('token')}"}
        )

        if response.status_code == 201:
            success = "Batch created successfully"

        else:
            error = response.json().get("error")    
    
    existing_batches = requests.get(f"{URL}/get_batches").json()

    return render_template(
        "create_batch.html",
        error=error,
        success=success,
        existing_batches=existing_batches
    )

@app.route("/admin/search-students")
def search_students_page():

    if "role" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/login")

    return render_template("search_students.html")

@app.route("/admin/student-profile/<username>")
def student_profile(username):
    # get some data
    resp = requests.post(
        f"{URL}/get_student_profile",
        json={
            "username": username
        },
        headers={"Authorization": f"Bearer {session.get('token')}"}
    ).json()
    first_name = resp.get("first_name")
    last_name = resp.get("last_name")
    roll_number = resp.get("roll_number")
    batch_name = resp.get("batch_name")
    email = resp.get("email")
    student_phone = resp.get("student_phone")
    parent_phone = resp.get("parent_phone")
    stream = resp.get("stream")
    target_year = resp.get("target_year")
    gender = resp.get("gender")
    return render_template(
        "student_profile.html",
        first_name=first_name,
        last_name=last_name,
        roll_number=roll_number,
        batch_name=batch_name,
        email=email,
        student_phone=student_phone,
        parent_phone=parent_phone,
        stream=stream,
        target_year=target_year
    )
    

#     {
#     "access": 1,
#     "batch_id": 1,
#     "email": "ddnayak103@gmail.com",
#     "first_name": "DHEERAJ",
#     "gender": "Male",
#     "last_name": "NAYAK",
#     "parent_phone": "911",
#     "roll_number": "209",
#     "stream": "PCMC",
#     "student_phone": "911",
#     "target_year": 2027,
#     "username": "ddnayak"
# }
    

# =========================
# RUN LOCALLY
# =========================
# if __name__ == "__main__":
#     app.run(debug=True)