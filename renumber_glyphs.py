import os
import re
import shutil
from collections import defaultdict
from datetime import datetime

def log_message(log_file, message):
    """Helper function to write messages to the log file and print to console."""
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")
    print(message)

def parse_filename(filename):
    """Extract number1, number2, number3 (handling + and - cases) from filename."""
    match = re.match(r"m(\d+)_R_lines_(\d+)_chunk_(\d+)([+-]\d+)?\.png", filename)
    if match:
        number1, number2, number3, extra = match.groups()
        number1, number2, number3 = map(int, (number1, number2, number3))
        extra_number = int(extra[1:]) if extra else None
        return filename, number1, number2, number3, extra_number
    return None

def rename_files(input_dir, output_dir):
    """Rename files while keeping order and continuity in number2 and number3."""
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    log_file = os.path.join(output_dir, "renumber_log.txt")
    log_message(log_file, f"Script invoked: renumber_glyphs.py {input_dir} {output_dir}")
    
    # Step 1: Read and parse all valid filenames
    file_data = []
    for filename in sorted(os.listdir(input_dir)):  # Ensure alphabetical order
        parsed = parse_filename(filename)
        if parsed:
            file_data.append(parsed)

    # Step 2: Process files grouped by number1
    grouped_files = defaultdict(list)
    for filename, number1, number2, number3, extra_number in file_data:
        grouped_files[number1].append((filename, number2, number3, extra_number))

    # Step 3: Rename files with continuous number2 and number3 values
    stats_max_number2 = {}  # Max number2 per number1
    total_files = len(file_data)

    for number1, files in grouped_files.items():
        files.sort(key=lambda x: (x[1], x[2], x[3] if x[3] else 0))  # Sort by number2, then number3, then extra
        
        new_number2_map = {}  # Old number2 -> New number2
        new_number2_counter = 1

        number2_groups = defaultdict(list)  # To process each number2 separately
        for f in files:
            number2_groups[f[1]].append(f)

        for old_number2, grouped_files in sorted(number2_groups.items()):  
            new_number2_map[old_number2] = new_number2_counter
            new_number2 = new_number2_counter
            new_number2_counter += 1

            # Now, renumber number3 fully sequentially
            new_number3_counter = 1  # Start at g01

            for filename, number2, number3, extra_number in sorted(grouped_files, key=lambda x: (x[2], x[3] if x[3] else 0)):
                new_name = f"t{number1:02d}_l{new_number2:02d}g{new_number3_counter:02d}"
                new_number3_counter += 1  # Ensure next file gets a new number

                new_name += ".png"
                shutil.copy(os.path.join(input_dir, filename), os.path.join(output_dir, new_name))

                # Log renaming action
                log_message(log_file, f"Renamed: {filename} -> {new_name}")

                # Update statistics
                stats_max_number2[number1] = max(stats_max_number2.get(number1, 0), new_number2)

    # Step 4: Print and log statistics
    log_message(log_file, "\nStatistics:")
    for number1, max_n2 in stats_max_number2.items():
        log_message(log_file, f"Max number2 for {number1:02d}: {max_n2:02d}")

    log_message(log_file, f"Total number of files: {total_files}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python renumber_glyphs.py <input_directory> <output_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)

    rename_files(input_directory, output_directory)
