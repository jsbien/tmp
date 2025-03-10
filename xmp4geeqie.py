import os
import subprocess
import sys

def generate_xmp_files(image_dir):
    """Runs ExifTool to generate Geeqie-compatible XMP files for all PNG images in a directory."""
    if not os.path.exists(image_dir):
        print(f"Error: Directory {image_dir} does not exist.")
        sys.exit(1)
    
    command = [
        "exiftool",
        "-ext", "png",
        "-XMP:all=",
        "-tagsfromfile", "@",
        "-XMP:all",
        "-o", "%d%f.png.gq.xmp",
        image_dir
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"XMP files successfully generated in {image_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error running ExifTool: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_geeqie_xmp.py <image_directory>")
        sys.exit(1)
    
    image_directory = sys.argv[1]
    generate_xmp_files(image_directory)
