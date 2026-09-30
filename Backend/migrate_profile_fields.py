import sqlite3
from pathlib import Path

DB_PATH = Path("bugsense.db")

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"Database not found: {DB_PATH.resolve()}"
    )

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

try:
    # Read existing columns first
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = {
        row[1] for row in cursor.fetchall()
    }

    print("Existing users columns:")
    print(sorted(existing_columns))
    print()

    migrations = {
        "primary_skills":
            "ALTER TABLE users ADD COLUMN primary_skills TEXT",

        "specialization":
            "ALTER TABLE users ADD COLUMN specialization VARCHAR(150)",

        "experience":
            "ALTER TABLE users ADD COLUMN experience VARCHAR(150)",

        "updated_at":
            "ALTER TABLE users ADD COLUMN updated_at DATETIME"
    }

    for column_name, sql in migrations.items():

        if column_name in existing_columns:
            print(f"SKIPPED: {column_name} already exists")
            continue

        cursor.execute(sql)
        print(f"ADDED: {column_name}")

    connection.commit()

    print("\nMigration completed successfully.")

    # Verify final table structure
    cursor.execute("PRAGMA table_info(users)")
    final_columns = [
        row[1] for row in cursor.fetchall()
    ]

    print("\nFinal users columns:")

    for column in final_columns:
        print(f" - {column}")

except Exception as error:

    connection.rollback()

    print("\nMigration failed.")
    print(error)

    raise

finally:
    connection.close()