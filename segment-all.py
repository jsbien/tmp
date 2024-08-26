import os
import sys
import shutil
import glob
import subprocess

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def process_directory(directory):
    png_files = glob.glob(os.path.join(directory, '*_mask.png'))
    all_csv_files = []
    
    for png_file in png_files:
        # Split the filename and extension
        filename = os.path.basename(png_file)
        name, ext = os.path.splitext(filename)
        
        # Remove the _mask suffix from the name
        if name.endswith('_mask'):
            base_name = name[:-5]  # Remove the '_mask' part
        else:
            base_name = name  # Fallback in case '_mask' is not present
        
        # Debugging output
        print(f"Processing file: {png_file}")
        print(f"Base name derived: {base_name}")
        
        output_dir = os.path.join(directory, base_name)
        
        # Step 1: Create the subdirectory for the file
        create_directory_if_not_exists(output_dir)
        
        # Step 2: Run the segmentation script using subprocess
        # Extract just the filename without any leading directory components
        filename = os.path.basename(png_file)

        # Use this filename when calling the segmentation script
        try:
            subprocess.run(['python3', 'segment_character_table.py', filename], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {png_file}: {e}")
            continue
        
        # Move the generated images to the appropriate directory
        for file in glob.glob(f"{name}_line_*.png"):
            shutil.move(file, output_dir)
        
        # Track the generated CSV file for concatenation
        csv_file = f"{base_name}.csv"
        if os.path.exists(csv_file):
            all_csv_files.append(csv_file)
    
    # Step 3: Concatenate all CSV files into one
    concatenate_csv_files(all_csv_files, os.path.join(directory, 'all_tables.csv'))

def concatenate_csv_files(csv_files, output_file):
    with open(output_file, 'w') as outfile:
        for i, fname in enumerate(csv_files):
            with open(fname) as infile:
                if i != 0:
                    infile.readline()  # Skip the header for all but the first file
                shutil.copyfileobj(infile, outfile)
            os.remove(fname)  # Optionally remove the individual CSV files after concatenation

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python segment-all.py <directory_path>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    process_directory(directory_path)
    print(f"Processing completed. All tables are concatenated into 'all_tables.csv'.")
