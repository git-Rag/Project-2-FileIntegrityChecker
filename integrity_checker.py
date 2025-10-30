import os
import hashlib
import json
import logging
from datetime import datetime

# -----------------------------
# 1️⃣ Setup Logging
# -----------------------------
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "integrity_log.txt")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------
# 2️⃣ Helper: Calculate Hash
# -----------------------------
def calculate_hash(file_path, algorithm="sha256"):
    """Calculate and return hash of a file using the given algorithm."""
    try:
        hasher = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error hashing file {file_path}: {e}")
        return None

# -----------------------------
# 3️⃣ Scan Directory & Generate Hashes
# -----------------------------
def scan_directory(directory):
    """Scan a directory and return a dictionary of file paths and hashes."""
    file_hashes = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            hash_value = calculate_hash(file_path)
            if hash_value:
                file_hashes[file_path] = hash_value
    return file_hashes

# -----------------------------
# 4️⃣ Compare Hashes (Detect Changes)
# -----------------------------
def compare_hashes(old_hashes, new_hashes):
    """Compare stored hashes with new ones and detect modifications."""
    modified = []
    missing = []
    new_files = []

    # Check for modified or missing files
    for file, old_hash in old_hashes.items():
        if file not in new_hashes:
            missing.append(file)
        elif new_hashes[file] != old_hash:
            modified.append(file)

    # Check for new files
    for file in new_hashes.keys():
        if file not in old_hashes:
            new_files.append(file)

    return modified, missing, new_files

# -----------------------------
# 5️⃣ Save Hashes to File
# -----------------------------
def save_hashes(file_hashes, filename="reference_hashes.json"):
    with open(filename, "w") as f:
        json.dump(file_hashes, f, indent=4)

# -----------------------------
# 6️⃣ Load Existing Hash File
# -----------------------------
def load_hashes(filename="reference_hashes.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

# -----------------------------
# 7️⃣ Main Function
# -----------------------------
def main():
    directory = input("Enter the directory path to scan: ").strip()
    if not os.path.exists(directory):
        print("❌ Directory not found!")
        return

    print("\n🔍 Scanning directory...")
    logging.info(f"Scanning started for directory: {directory}")
    new_hashes = scan_directory(directory)
    old_hashes = load_hashes()

    modified, missing, new_files = compare_hashes(old_hashes, new_hashes)

    # Save current state
    save_hashes(new_hashes)

    # -----------------------------
    # 8️⃣ Logging Results
    # -----------------------------
    logging.info(f"Scan completed at {datetime.now()}")
    logging.info(f"Modified files: {modified}")
    logging.info(f"Missing files: {missing}")
    logging.info(f"New files: {new_files}")

    # -----------------------------
    # 9️⃣ Print Report
    # -----------------------------
    print("\n📋 Scan Results:")
    print(f"Modified files: {len(modified)}")
    print(f"Missing files: {len(missing)}")
    print(f"New files: {len(new_files)}")

    if modified:
        print("\n⚠️ Modified Files:")
        for f in modified:
            print(" -", f)

    if missing:
        print("\n❌ Missing Files:")
        for f in missing:
            print(" -", f)

    if new_files:
        print("\n🆕 New Files:")
        for f in new_files:
            print(" -", f)

    print("\n✅ Scan completed! Results logged in 'logs/integrity_log.txt'.")

# -----------------------------
# 10️⃣ Entry Point
# -----------------------------
if __name__ == "__main__":
    main()
