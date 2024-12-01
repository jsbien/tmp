# ChatGPG - JSB specification, 2024-12-01
import os
import sys
from datetime import datetime

def parse_log_timestamp(file_path):
    """
    Extract the timestamp from the last line of the log file.
    """
    try:
        with open(file_path, "r") as log_file:
            lines = log_file.readlines()
            if not lines:
                raise ValueError("Log file is empty.")
            # Extract the last line and parse it as a timestamp
            last_line = lines[-1].strip()
            if last_line.startswith("Timestamp:"):
                timestamp_str = last_line.split("Timestamp:")[1].strip()
                return datetime.fromisoformat(timestamp_str)
            else:
                raise ValueError("No valid timestamp found in the last line.")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def find_edited_logs(directory):
    """
    Find and list .log files in the given directory where the modification time
    is later than the timestamp in the log.
    """
    log_files = []
    total_files_checked = 0

    # Collect all .log files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".log"):
                log_files.append(os.path.join(root, file))
                total_files_checked += 1

    # Sort log files alphabetically by their full paths
    log_files.sort()

    # Check each log file for modification time vs. timestamp
    edited_logs = []
    for file_path in log_files:
        log_timestamp = parse_log_timestamp(file_path)

        if log_timestamp:
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if mod_time > log_timestamp:
                edited_logs.append(file_path)

    # Print results
    for log_file in edited_logs:
        print(f"Edited log: {log_file}")
    print(f"Total edited logs: {len(edited_logs)} out of {total_files_checked} checked.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_edited.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    find_edited_logs(directory)
