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

# Connect to the SQLite database
conn = sqlite3.connect(DB_FILE_PATH)
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

# Update existing rows or insert new rows from profile data
for record in records:
    login = record.get("login", "").strip()
    if not login:
        continue

    github_id = record.get("id")
    avatar_url = (record.get("avatar_url") or "").strip()
    profile_url = (record.get("profile_url") or "").strip()
    contributions = record.get("contributions", 0)
    name = (record.get("name") or "").strip()
    email = (record.get("email") or "").strip()
    company = (record.get("company") or "").strip()
    blog = (record.get("blog") or "").strip()
    location = (record.get("location") or "").strip()
    bio = (record.get("bio") or "").strip()
    public_repos = record.get("public_repos", 0)
    followers = record.get("followers", 0)
    following = record.get("following", 0)
    created_at = (record.get("created_at") or "").strip()
    updated_at = (record.get("updated_at") or "").strip()

    # Attempt to UPDATE an existing row
    cursor.execute("""
        UPDATE User_Profiles
        SET
            GitHub_ID = ?,
            Avatar_URL = ?,
            Profile_URL = ?,
            Contributions = ?,
            Name = ?,
            Email = ?,
            Company = ?,
            Blog = ?,
            Location = ?,
            Bio = ?,
            Public_Repos = ?,
            Followers = ?,
            Following = ?,
            Created_At = ?,
            Updated_At = ?
        WHERE Login = ?
    """, (
        github_id, avatar_url, profile_url, contributions,
        name, email, company, blog, location, bio,
        public_repos, followers, following, created_at, updated_at,
        login,
    ))

    # If no rows were updated, INSERT a new one
    if cursor.rowcount == 0:
        cursor.execute("""
            INSERT INTO User_Profiles (
                Login, GitHub_ID, Avatar_URL, Profile_URL, Contributions,
                Name, Email, Company, Blog, Location, Bio,
                Public_Repos, Followers, Following, Created_At, Updated_At
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            login, github_id, avatar_url, profile_url, contributions,
            name, email, company, blog, location, bio,
            public_repos, followers, following, created_at, updated_at,
        ))

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()

print(f"Database updated from {JSON_FILE_PATH} successfully.")
