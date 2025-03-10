import os
import re
import csv

def parse_filename(filename):
    """Extract table, row, glyph numbers from PNG filename."""
    match = re.match(r"t(\d+)_l(\d+)g(\d+)\.png", filename)
    if match:
        return tuple(match.groups())  # Strings for consistency
    return None

def load_metadata(meta_file):
    """Load metadata CSV into a dictionary mapping table number to its properties."""
    metadata = {}
    with open(meta_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            metadata[row['number']] = row
    return metadata

def load_dsed_file(dsed_directory, filename):
    """Extract Year and Note from a dsed file."""
    dsed_path = os.path.join(dsed_directory, filename)
    year, note = "", ""
    if os.path.isfile(dsed_path):
        with open(dsed_path, encoding='utf-8') as file:
            for line in file:
                if line.startswith("Year "):
                    year = line.split("\"")[1]
                elif line.startswith("Note "):
                    note = line.split("\"")[1]
    return year, note

def create_id(printer, font, row, glyph):
    """Generate an identifier."""
    return f"{printer}-{font}{row}{glyph}"

def generate_sidecar_files(input_dir, output_dir, dsed_dir, meta_file):
    """Generate CSV sidecar files for each PNG file in input_dir."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    metadata = load_metadata(meta_file)
    
    for filename in os.listdir(input_dir):
        if not filename.endswith(".png"):
            continue
        
        parsed = parse_filename(filename)
        if not parsed:
            continue
        
        table, row, glyph = parsed
        meta_entry = metadata.get(table)
        
        if not meta_entry:
            continue  # Skip if no metadata entry found
        
        printer, font, fascicule, plate = meta_entry['printer'], meta_entry['font'], meta_entry['fascicule'], meta_entry['plate']
        
        id_value = create_id(printer, font, row, glyph)
        
        dsed_filename = meta_entry['filename'].replace(".djvu", "_4dsed.txt")
        year, description = load_dsed_file(dsed_dir, dsed_filename)
        
        sidecar_filename = os.path.join(output_dir, filename.replace(".png", ".csv"))
        
        with open(sidecar_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["table", "row", "glyph", "id", "printer", "font", "fascicule", "year", "plate", "description"])
            writer.writerow([table, row, glyph, id_value, printer, font, fascicule, year, plate, description])
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 5:
        print("Usage: python glyphs2meta.py <input_directory> <output_directory> <dsed_directory> <meta_file>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    dsed_directory = sys.argv[3]
    metadata_filepath = sys.argv[4]

    generate_sidecar_files(input_directory, output_directory, dsed_directory, metadata_filepath)
