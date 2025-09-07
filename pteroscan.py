#!/usr/bin/env python3
import os
import hashlib
import yaml
import requests
import time

# Load configuration
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

BASE_PATH = config.get("base_path", "/var/lib/pterodactyl/volumes")
API_ENDPOINT = config["api_url"]
API_KEY = config.get("api_key")
SCAN_INTERVAL = config.get("scan_interval_seconds", 300)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
    "Content-Type": "application/json"
}

def sha256_file(filepath, block_size=65536):
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(block_size), b""):
                sha256.update(chunk)
    except Exception as e:
        print(f"Error hashing {filepath}: {e}")
        return None
    return sha256.hexdigest()

def process_server(server_id):
    """Process one server's files and return JSON data."""
    server_path = os.path.join(BASE_PATH, server_id)
    file_data = []

    for root, _, files in os.walk(server_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, server_path)  # relative path
            hash_val = sha256_file(filepath)
            if hash_val:
                file_data.append({
                    "server_id": server_id,
                    "file_name": filename,
                    "file_path": relpath,
                    "sha256": hash_val
                })

    return {
        "server_id": server_id,
        "files": file_data
    }

def main():
    while True:
        for server_id in os.listdir(BASE_PATH):
            server_path = os.path.join(BASE_PATH, server_id)
            if not os.path.isdir(server_path):
                continue  # Skip non-directories

            print(f"Processing server {server_id}...")
            server_json = process_server(server_id)

            # Send data to API
            try:
                response = requests.post(API_ENDPOINT, headers=HEADERS, json=server_json)
                if response.status_code == 200:
                    print(f"Successfully sent data for {server_id}")
                else:
                    print(f"Failed for {server_id}, status: {response.status_code}, response: {response.text}")
            except Exception as e:
                print(f"Error sending data for {server_id}: {e}")

        print(f"Scan complete. Waiting {SCAN_INTERVAL} seconds...")
        time.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    main()
