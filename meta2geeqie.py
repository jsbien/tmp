import os
import xml.etree.ElementTree as ET
import pandas as pd

def update_xmp_with_csv(xmp_file, csv_file, output_xmp):
    """Update the existing XMP file with metadata from a CSV file."""
    # Ensure the CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found: {csv_file}")
        return
    
    # Load CSV metadata
    csv_data = pd.read_csv(csv_file)
    
    # Read and parse the XMP file
    tree = ET.parse(xmp_file)
    root = tree.getroot()
    
    # Locate RDF:Description node
    rdf_description = root.find(".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
    
    if rdf_description is None:
        print(f"Error: RDF Description not found in XMP file: {xmp_file}")
        return
    
    # Locate RDF:Bag node within dc:subject
    rdf_bag = rdf_description.find(".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag")
    
    if rdf_bag is None:
        # Create RDF:Bag if it does not exist
        rdf_bag = ET.SubElement(rdf_description, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag")
    
    # Add CSV metadata to the XMP file
    for _, row in csv_data.iterrows():
        metadata_values = [
            str(row['id']), str(row['printer']), str(row['font']), str(row['fascicule']),
            str(row['year']), str(row['plate']), str(row['description'])
        ]
        
        for value in metadata_values:
            if value and not any(li.text == value for li in rdf_bag):
                ET.SubElement(rdf_bag, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li").text = value
    
    # Save updated XMP file
    with open(output_xmp, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
    print(f"Updated XMP file saved: {output_xmp}")

def process_directory(input_dir, output_dir):
    """Process all XMP and corresponding CSV files in the input directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file in os.listdir(input_dir):
        if file.endswith(".xmp"):
            base_name = file.replace(".png.gq.xmp", "")
            csv_file = os.path.join(input_dir, base_name + ".csv")
            xmp_file = os.path.join(input_dir, file)
            output_xmp = os.path.join(output_dir, file)
            
            if os.path.exists(csv_file):
                update_xmp_with_csv(xmp_file, csv_file, output_xmp)
            else:
                print(f"Warning: No CSV file found for {file}, skipping update.")

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python meta2geeqie.py <input_directory> <output_directory>")
        sys.exit(1)
    
    input_directory = os.path.abspath(sys.argv[1])
    output_directory = os.path.abspath(sys.argv[2])
    
    process_directory(input_directory, output_directory)
