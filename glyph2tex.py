import os
import re
from collections import defaultdict

def parse_filename(filename):
    """Extract number1, number2, number3 from filename."""
    match = re.match(r"t(\d+)_l(\d+)g(\d+)\.png", filename)
    if match:
        return tuple(map(int, match.groups())), filename  # Convert numbers to int for sorting
    return None

def generate_tex_files(input_dir, output_dir):
    """Generate LaTeX files based on grouped image filenames."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Group files by t<number1>
    grouped_files = defaultdict(list)
    
    for filename in sorted(os.listdir(input_dir)):  # Ensure alphabetical order
        parsed = parse_filename(filename)
        if parsed:
            (number1, number2, number3), fname = parsed
            grouped_files[number1].append(fname)

    # Process each group and create a .tex file
    for number1, files in grouped_files.items():
        tex_filename = f"t{number1:02d}_glyphs.tex"
        tex_path = os.path.join(output_dir, tex_filename)

        with open(tex_path, "w") as tex_file:
            # Write preamble
            tex_file.write("\\exdisplay \\bg \\gla\n")

            # Write file references
            for i, file_name in enumerate(sorted(files), start=1):
                tex_file.write(f"% {i}\n{{\\PTglyph{{5}}{{{file_name}}}}}\n")

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
    if len(sys.argv) != 3:
        print("Usage: python glyph2tex.py <input_directory> <output_directory>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)

    generate_tex_files(input_directory, output_directory)
