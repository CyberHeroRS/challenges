import hashlib
import random
import secrets
import os

from faker import Faker
from pymongo import MongoClient


def get_db():
    user = os.environ["MONGO_INITDB_ROOT_USERNAME"]
    pswd = os.environ["MONGO_INITDB_ROOT_PASSWORD"]
    conn_str = f"mongodb://{user}:{pswd}@localhost:27017/"
    print(f"Connecting to: {conn_str}")
    client = MongoClient(conn_str)
    return client["intranet"]

print("FLAG: " + os.environ["FLAG"])
print("Starting connection")

db = get_db()

print("Connected")

# Clear existing data
db.employees.delete_many({})
db.notes.delete_many({})


# Generate fake data

fake = Faker('en_US')


def secure_password():
    spouse_firstname = fake.first_name()
    spouse_lastname = fake.last_name()
    year_of_birth = str(random.randint(1950, 2000))
    password_parts = [spouse_firstname, spouse_lastname, year_of_birth]
    random.shuffle(password_parts)
    passwd = "".join(password_parts)
    print(f"Password: {passwd}")
    return passwd


DEPARTMENTS = [
    "HR",
    "Marketing",
    "IT",
    "Customer Service",
]

ceo_id = random.randint(1, 10000)

rows = []
for i in range(10000):
    first_name = fake.first_name()
    last_name = fake.last_name()
    is_ceo = i == ceo_id
    password = secure_password()
    row = {
        "first_name": first_name,
        "last_name": last_name,
        "employee_number": random.randint(1, 10000) * 10000 + i,
        "department": random.choice(DEPARTMENTS),
        "email": f"{first_name}.{last_name}@example.com".lower(),
        "phone_number": f"555-{random.randint(100, 999)}-{random.randint(100, 999)}",
        "is_public": random.choice([True, False]),
        "password": hashlib.sha1(password.encode()).hexdigest(),
    }
    if is_ceo:
        row["department"] = "CEO"
        row["is_public"] = False
        if os.environ.get("DEBUG"):
            print("CEO employee num:", row["employee_number"])
            print("CEO PASSWORD:", password)
            print("CEO HASH:", row["password"])
    rows.append(row)

db.employees.insert_many(rows)

# Add some notes (and the flag)

notes = []
for department in DEPARTMENTS + ["CEO"]:
    for i in range(random.randint(10, 50)):
        note = "\n".join(fake.paragraphs(nb=random.randint(1, 5)))
        notes.append({
            "title": fake.sentence(nb_words=random.randint(3, 5)),
            "department": department,
            "content": note,
            "created_at": fake.date_time(),
        })

notes[random.randint(0, len(notes) - 1)] |= {
    "title": "Secret CEO Note",
    "department": "CEO",
    "content": f"""
Look at me, I'm the CEO!

Here's a flag to prove it: {os.environ["FLAG"]}

"""
}

db.notes.insert_many(notes)