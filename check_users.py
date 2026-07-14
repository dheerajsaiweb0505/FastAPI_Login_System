from app.database import SessionLocal
from app.models import User
from tabulate import tabulate
db = SessionLocal()

users = db.query(User).all()
table = []

for user in users:
    table.append([
        user.id,
        user.username,
        user.email
    ])



print(tabulate(
    table,
    headers=["ID", "Username", "Email"],
    tablefmt="grid"
))
db.close()