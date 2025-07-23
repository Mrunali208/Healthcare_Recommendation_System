import pandas as pd
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load the CSV
df = pd.read_csv("data/users.csv")

# Only hash rows that are still in plain-text (non-hashed)
def needs_hashing(pwd):
    return isinstance(pwd, str) and len(pwd) < 64  # SHA256 is 64 hex chars

df["password_hash"] = df["password_hash"].apply(lambda x: hash_password(x) if needs_hashing(x) else x)

# Remove any accidental whitespace in usernames
df["username"] = df["username"].str.strip()

# Remove duplicates (keeping latest)
df = df.drop_duplicates(subset=["username"], keep="last")

# Save back
df.to_csv("data/users.csv", index=False)
print("✅ Migration complete!")
