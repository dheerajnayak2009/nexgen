from flask import Flask, render_template, request, redirect, session, jsonify
import requests

app = Flask(__name__)

# Secret key for session management
app.secret_key = "your_secret_key_here"

URL = "https://sharmaji.pythonanywhere.com"


# Helper function to get real client IP address
def get_client_ip():
    """Get the real client IP address even behind proxies"""
    # Check for X-Forwarded-For header (most common behind load balancers/proxies)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2)
        # The first one is the original client IP
        return forwarded_for.split(',')[0].strip()
    
    # Check for X-Real-IP header (common with nginx)
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fall back to remote_addr
    return request.remote_addr


# =========================
# GET FINGERPRINT DATA FROM FRONTEND
# =========================
@app.route("/get-fingerprint-data", methods=["POST"])
def get_fingerprint_data():
    """Store fingerprint data in session for login use"""
    data = request.json
    session["fingerprint"] = data
    return jsonify({"status": "ok"})


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

    return render_template("staff.html",
                            first_name=session.get("first_name"),
                            last_name=session.get("last_name"),
                            email=session.get("email"),
                            phone=session.get("phone"),
                            department=session.get("department"),
                            designation=session.get("designation"),
                            username=session.get("username")
                           )


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
        
        # Get real client IP
        ip_address = get_client_ip()
        user_agent = request.headers.get("User-Agent")
        
        # Get fingerprint data from session (collected by frontend)
        fingerprint = session.get("fingerprint", {})
        
        # Build complete request payload
        payload = {
            "username": username,
            "password": password,
            "ip_address": ip_address,
            "user_agent": user_agent,
            # HTTP headers
            "forwarded_for": request.headers.get("X-Forwarded-For"),
            "host": request.headers.get("Host"),
            "origin": request.headers.get("Origin"),
            "referer": request.headers.get("Referer"),
            "accept_language": request.headers.get("Accept-Language"),
            "sec_ch_ua": request.headers.get("Sec-Ch-Ua"),
            "sec_ch_platform": request.headers.get("Sec-Ch-Ua-Platform"),
            "sec_ch_mobile": request.headers.get("Sec-Ch-Ua-Mobile"),
            "method": request.method,
            "path": request.path,
            # Fingerprint data from JavaScript
            "screen_resolution": fingerprint.get("screen_resolution"),
            "viewport": fingerprint.get("viewport"),
            "timezone": fingerprint.get("timezone"),
            "timezone_offset": fingerprint.get("timezone_offset"),
            "language": fingerprint.get("language"),
            "languages": fingerprint.get("languages"),
            "platform": fingerprint.get("platform"),
            "cpu_cores": fingerprint.get("cpu_cores"),
            "device_memory": fingerprint.get("device_memory"),
            "touch_points": fingerprint.get("touch_points"),
            "cookies_enabled": fingerprint.get("cookies_enabled"),
            "online_status": fingerprint.get("online_status"),
            "connection_type": fingerprint.get("connection_type"),
            "device_pixel_ratio": fingerprint.get("device_pixel_ratio"),
            "local_storage": fingerprint.get("local_storage"),
            "session_storage": fingerprint.get("session_storage"),
            "do_not_track": fingerprint.get("do_not_track"),
            "login_id": fingerprint.get("login_id"),
            "request_id": fingerprint.get("request_id"),
            "session_id": fingerprint.get("session_id"),
            "device_id": fingerprint.get("device_id"),
            "referrer_policy": fingerprint.get("referrer_policy")
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        response = requests.post(
            f"{URL}/login",
            json=payload,
            timeout=10
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
                token = response.json().get("access_token")
                session["token"] = token
                return redirect("/admin")

            elif role == "student":
                
                first_name = response.json().get("first_name")
                last_name = response.json().get("last_name")
                roll_number = response.json().get("roll_number")
                email = response.json().get("email")
                batch_name = response.json().get("batch_name")
                student_phone = response.json().get("student_phone")
                parent_phone = response.json().get("parent_phone")
                stream = response.json().get("stream")
                target_year = response.json().get("target_year")
                gender = response.json().get("gender")

                session["first_name"] = first_name
                session["last_name"] = last_name
                session["roll_number"] = roll_number
                session["email"] = email
                session["student_phone"] = student_phone
                session["parent_phone"] = parent_phone
                session["stream"] = stream
                session["target_year"] = target_year
                session["gender"] = gender
                session["batch_name"] = batch_name
                return redirect("/student")

            else:  # role == "staff"
                # Store staff profile data in session
                first_name = response.json().get("first_name")
                last_name = response.json().get("last_name")
                email = response.json().get("email")
                phone = response.json().get("phone")
                department = response.json().get("department")
                designation = response.json().get("designation")
                
                session["first_name"] = first_name
                session["last_name"] = last_name
                session["email"] = email
                session["phone"] = phone
                session["department"] = department
                session["designation"] = designation
                return redirect("/staff")

        # =========================
        # INVALID LOGIN
        # =========================
        if response.status_code == 401:
            error = "Invalid username or password."

        elif response.status_code == 400:
            error = "Please fill in all the fields."

    # Clear fingerprint on GET request
    session.pop("fingerprint", None)
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


# =========================
# ADMIN: REGISTER STAFF
# =========================
@app.route("/admin/register-staff", methods=["GET", "POST"])
def register_staff():

    # Admin protection
    if "role" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/login")

    error = None
    success = None

    if request.method == "POST":

        payload = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "first_name": request.form.get("first_name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "department": request.form.get("department"),
            "designation": request.form.get("designation"),
        }
        
        last_name = request.form.get("last_name")
        if last_name:
            payload["last_name"] = last_name

        response = requests.post(
            f"{URL}/register_staff",
            json=payload,
            timeout=10,
            headers={"Authorization": f"Bearer {session.get('token')}"}
        )

        if response.status_code == 201:
            success = "Staff registered successfully! They can now log in with their credentials."
        else:
            try:
                error_data = response.json()
                error = error_data.get("error", "Failed to register staff. Please check the information provided.")
            except:
                error = f"Failed to register staff. Status code: {response.status_code}"

    return render_template(
        "register_staff.html",
        error=error,
        success=success
    )


# =========================
# ADMIN: CREATE BATCH
# =========================
@app.route("/admin/create-batch", methods=["GET", "POST"])
def create_batch():

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


# =========================
# ADMIN: SEARCH STUDENTS
# =========================
@app.route("/admin/search-students")
def search_students_page():

    if "role" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/login")

    return render_template("search_students.html")


# =========================
# ADMIN: STUDENT PROFILE
# =========================
@app.route("/admin/student-profile/<username>")
def student_profile(username):
    resp = requests.post(
        f"{URL}/get_student_profile",
        json={"username": username},
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


# =========================
# ADMIN: SEARCH STAFF
# =========================
@app.route("/admin/search-staff")
def search_staff_page():

    if "role" not in session:
        return redirect("/login")

    if session["role"] != "admin":
        return redirect("/login")

    return render_template("search_staff.html")


# =========================
# ADMIN: STAFF PROFILE
# =========================
@app.route("/admin/staff-profile/<username>")
def staff_profile(username):
    
    if "role" not in session:
        return redirect("/login")
    
    if session["role"] != "admin":
        return redirect("/login")
    
    try:
        resp = requests.post(
            f"{URL}/get_staff_profile",
            json={"username": username},
            headers={"Authorization": f"Bearer {session.get('token')}"}
        ).json()
        
        first_name = resp.get("first_name")
        last_name = resp.get("last_name")
        email = resp.get("email")
        phone = resp.get("phone")
        department = resp.get("department")
        designation = resp.get("designation")
        is_active = resp.get("is_active", 1)
        
        return render_template(
            "staff_profile.html",
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department=department,
            designation=designation,
            is_active=is_active,
            username=username
        )
    except Exception as e:
        return redirect("/admin/search-staff")


# =========================
# RUN LOCALLY
# =========================
if __name__ == "__main__":
    app.run(debug=True)