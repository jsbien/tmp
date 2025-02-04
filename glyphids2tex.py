import os
import re
import csv
from collections import defaultdict

def parse_filename(filename):
    """Extract number1, number2, number3 from filename."""
    match = re.match(r"t(\d+)_l(\d+)g(\d+)\.png", filename)
    if match:
        return tuple(map(int, match.groups())), filename  # Convert numbers to int for sorting
    return None

def load_metadata(metadata_file):
    """Load metadata CSV into a dictionary mapping number1 to its symbol."""
    metadata = {}
    with open(metadata_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # Skip header row
        for row in reader:
            if len(row) < 3:
                continue
            number1, _, name = row[:3]
            try:
                number1 = int(number1)  # Convert to int for consistency
            except ValueError:
                continue  # Skip malformed rows

            # Generate 2-letter symbol
            symbol = name[:2]  # Default to first 2 letters
            match = re.match(r"([A-Za-z]+)(\d+)?", name)
            if match:
                letters, digits = match.groups()
                symbol = letters[:2] + (digits if digits else "")

            metadata[number1] = symbol
    return metadata

# def load_metadata(metadata_file):
#     """Load metadata CSV into a dictionary mapping number1 to its symbol."""
#     metadata = {}
#     with open(metadata_file, newline='', encoding='utf-8') as csvfile:
#         reader = csv.reader(csvfile)
#         for row in reader:
#             if len(row) < 3:
#                 continue
#             number1, _, name = row[:3]
#             number1 = int(number1)  # Convert to int for consistency

#             # Generate 2-letter symbol
#             symbol = name[:2]  # Default to first 2 letters
#             match = re.match(r"([A-Za-z]+)(\d+)?", name)
#             if match:
#                 letters, digits = match.groups()
#                 symbol = letters[:2] + (digits if digits else "")

#             metadata[number1] = symbol
#     return metadata

def generate_tex_files(input_dir, output_dir, metadata_file):
    """Generate LaTeX files based on grouped image filenames and metadata."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    metadata = load_metadata(metadata_file)

    # Group files by t<number1>
    grouped_files = defaultdict(list)
    
    for filename in sorted(os.listdir(input_dir)):  # Ensure alphabetical order
        parsed = parse_filename(filename)
        if parsed:
            (number1, number2, number3), fname = parsed
            grouped_files[number1].append((number2, number3, fname))

    # Process each group and create a .tex file
    for number1, files in grouped_files.items():
        tex_filename = f"t{number1:02d}_glyphids.tex"
        tex_path = os.path.join(output_dir, tex_filename)

        symbol = metadata.get(number1, f"X{number1}")  # Default if missing

        with open(tex_path, "w") as tex_file:
            # Write preamble
            tex_file.write("\\glpismo\n")

            # Write file references
            for i, (number2, number3, file_name) in enumerate(sorted(files), start=1):
                glyph_id = f"{symbol}-{number1:02d}{number2:02d}{number3:02d}"
                tex_file.write(f"% {i}\n{{\\PTglyphid{{{glyph_id}}}}}\n")

            # Write postamble
            tex_file.write("//\n")
            tex_file.write("%%% Local Variables:\n")
            tex_file.write("%%% mode: latex\n")
            tex_file.write("%%% TeX-engine: luatex\n")
            tex_file.write("%%% TeX-master: shared\n")
            tex_file.write("%%% End:\n")

        print(f"Generated {tex_filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python glyphids2tex.py <input_directory> <output_directory> <metadata_file>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    metadata_filepath = sys.argv[3]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)

    if not os.path.isfile(metadata_filepath):
        print(f"Error: {metadata_filepath} is not a valid file.")
        sys.exit(1)

    generate_tex_files(input_directory, output_directory, metadata_filepath)
