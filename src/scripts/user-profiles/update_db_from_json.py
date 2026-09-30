import json
import sqlite3

# File paths
JSON_FILE_PATH = "data/user-profiles/user_profiles.json"
DB_FILE_PATH = "data/user-profiles/user_profiles.db"

# Read JSON data
try:
    with open(JSON_FILE_PATH, "r") as json_file:
        profile_data = json.load(json_file)
except FileNotFoundError:
    raise FileNotFoundError(
        f"Profile data file not found: '{JSON_FILE_PATH}'. "
        "Run fetch_user_profiles.py first to generate it."
    )

records = profile_data["data"]

# Connect to the SQLite database and perform all operations within a context manager
with sqlite3.connect(DB_FILE_PATH) as conn:
    cursor = conn.cursor()

    # Create table with the user profile schema if it doesn't exist
    cursor.execute("""
CREATE TABLE IF NOT EXISTS User_Profiles (
    Login TEXT,
    GitHub_ID INTEGER,
    Avatar_URL TEXT,
    Profile_URL TEXT,
    Contributions INTEGER,
    Name TEXT,
    Email TEXT,
    Company TEXT,
    Blog TEXT,
    Location TEXT,
    Bio TEXT,
    Public_Repos INTEGER,
    Followers INTEGER,
    Following INTEGER,
    Created_At TEXT,
    Updated_At TEXT,
    PRIMARY KEY (Login)
)
""")

    # Upsert each record using INSERT OR REPLACE for efficiency
    for record in records:
        login = record.get("login", "").strip()
        if not login:
            continue

        cursor.execute("""
            INSERT OR REPLACE INTO User_Profiles (
                Login, GitHub_ID, Avatar_URL, Profile_URL, Contributions,
                Name, Email, Company, Blog, Location, Bio,
                Public_Repos, Followers, Following, Created_At, Updated_At
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            login,
            record.get("id"),
            (record.get("avatar_url") or "").strip(),
            (record.get("profile_url") or "").strip(),
            record.get("contributions", 0),
            (record.get("name") or "").strip(),
            (record.get("email") or "").strip(),
            (record.get("company") or "").strip(),
            (record.get("blog") or "").strip(),
            (record.get("location") or "").strip(),
            (record.get("bio") or "").strip(),
            record.get("public_repos", 0),
            record.get("followers", 0),
            record.get("following", 0),
            (record.get("created_at") or "").strip(),
            (record.get("updated_at") or "").strip(),
        ))

print(f"Database updated from {JSON_FILE_PATH} successfully.")
