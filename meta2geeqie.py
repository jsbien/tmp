import os
import xml.etree.ElementTree as ET
import pandas as pd

def update_xmp_with_csv(xmp_file, csv_file, output_xmp):
    """Update the existing XMP file with metadata from a CSV file."""
    # Load CSV metadata
    csv_data = pd.read_csv(csv_file)
    
    # Read and parse the XMP file
    tree = ET.parse(xmp_file)
    root = tree.getroot()
    
    # Locate RDF:Description node
    rdf_description = root.find(".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
    
    if rdf_description is None:
        print("Error: RDF Description not found in XMP file.")
        return
    
    # Locate RDF:Bag node within dc:subject
    rdf_bag = rdf_description.find(".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag")
    
    if rdf_bag is None:
        # Create RDF:Bag if it does not exist
        rdf_bag = ET.SubElement(rdf_description, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag")
    
    # Add CSV metadata to the XMP file
    for _, row in csv_data.iterrows():
        metadata_values = [
            row['id'], row['printer'], row['font'], str(row['fascicule']),
            str(row['year']), str(row['plate']), row['description']
        ]
        
        for value in metadata_values:
            if value and not any(li.text == value for li in rdf_bag):
                ET.SubElement(rdf_bag, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li").text = value
    
    # Save updated XMP file
    tree.write(output_xmp, encoding="utf-8", xml_declaration=True)
    print(f"Updated XMP file saved: {output_xmp}")

# Example usage
if __name__ == "__main__":
    xmp_input = "t01_l01g01.png.gq.xmp"
    csv_input = "t01_l01g01.csv"
    xmp_output = "t01_l01g01_updated.xmp"
    
    update_xmp_with_csv(xmp_input, csv_input, xmp_output)
