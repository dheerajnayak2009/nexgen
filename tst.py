import requests
import random
import string

BASE_URL = "https://sharmaji.pythonanywhere.com"

first_names = [
    "Rahul", "Aarav", "Vihaan", "Rohan", "Karan",
    "Aditya", "Nikhil", "Arjun", "Siddharth", "Manav",
    "Anaya", "Ishita", "Meera", "Kavya", "Priya",
    "Sneha", "Diya", "Aditi", "Riya", "Tanvi"
]

last_names = [
    "Sharma", "Patel", "Reddy", "Verma", "Nair",
    "Gupta", "Joshi", "Kapoor", "Iyer", "Kulkarni"
]

roles = ["student", "staff"]


def generate_username():
    first = random.choice(first_names)
    last = random.choice(last_names)
    number = random.randint(100, 999)

    username = f"{first}{last}{number}"
    return username


def generate_password():
    return str(random.randint(1000, 999999))


def register_user():
    username = generate_username()
    password = generate_password()
    role = random.choice(roles)

    payload = {
        "username": username,
        "password": password,
        "role": role
    }

    try:
        response = requests.post(
            BASE_URL + "/register",
            json=payload
        )

        print("=" * 50)
        print("Username:", username)
        print("Password:", password)
        print("Role:", role)
        print("Status:", response.status_code)

        try:
            print("Response:", response.json())
        except:
            print("Response Text:", response.text)

    except Exception as e:
        print("Error:", e)


TOTAL_USERS = 50

for _ in range(TOTAL_USERS):
    register_user()