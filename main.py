from flask import Flask, render_template

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/login")
def login():
    return render_template("login.html")

# --- IF LOCAL, THEN UNCOMMENT THIS ---

# if __name__ == "__main__":
#     app.run(debug=True)