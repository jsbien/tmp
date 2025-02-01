def split_into_chunks(image, output_dir, file_basename, log_file):
    """Split the image into chunks using vertical gaps and save them."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Assuming input images are already binary
    binary = gray

    # Log the shape and pixel values of the binary image
    log_message(log_file, f"Binary image shape: {binary.shape}")
    log_message(log_file, f"Unique pixel values in binary image: {np.unique(binary)}")

    gaps = find_vertical_gaps(binary, log_file)
    log_message(log_file, f"Detected gaps: {gaps}")

    chunk_number = 0
    prev_gap_end = 0

    for gap_start, gap_end in gaps:
        # Extract the chunk between the previous gap and the current gap
        chunk_image = binary[:, prev_gap_end:gap_start]
        if chunk_image.shape[1] > 0:  # Ignore empty chunks
            padded_chunk = cv2.copyMakeBorder(chunk_image, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=255)

            chunk_number += 1
            chunk_dir = os.path.join(output_dir, os.path.splitext(file_basename)[0] + ".glyph")
            os.makedirs(chunk_dir, exist_ok=True)

            output_path = os.path.join(chunk_dir, f"chunk_{chunk_number:02d}_{os.path.splitext(file_basename)[0]}.png")
            cv2.imwrite(output_path, padded_chunk)

            log_message(log_file, f"Chunk {chunk_number}: Columns [{prev_gap_end}:{gap_start}] saved to {output_path}")

        prev_gap_end = gap_end + 1

    # Handle the last chunk after the final gap
    if prev_gap_end < binary.shape[1]:
        chunk_image = binary[:, prev_gap_end:]
        padded_chunk = cv2.copyMakeBorder(chunk_image, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=255)

        chunk_number += 1
        chunk_dir = os.path.join(output_dir, os.path.splitext(file_basename)[0] + ".glyph")
        os.makedirs(chunk_dir, exist_ok=True)

        output_path = os.path.join(chunk_dir, f"chunk_{chunk_number:02d}_{os.path.splitext(file_basename)[0]}.png")
        cv2.imwrite(output_path, padded_chunk)

        log_message(log_file, f"Final chunk {chunk_number}: Columns [{prev_gap_end}:{binary.shape[1]}] saved to {output_path}")

    if chunk_number == 0:
        log_message(log_file, f"No chunks detected for file: {file_basename}")

    return chunk_number

def find_vertical_gaps(binary, log_file):
    """Find vertical gaps composed of columns of white pixels."""
    height, width = binary.shape
    gaps = []

    in_gap = False
    gap_start = 0

    for x in range(width):
        if np.all(binary[:, x] == 255):  # Column is fully white
            if not in_gap:
                gap_start = x
                in_gap = True
        else:
            if in_gap:
                gaps.append((gap_start, x - 1))
                log_message(log_file, f"Gap found: Columns [{gap_start}:{x - 1}]")
                in_gap = False

    if in_gap:  # Handle gap ending at the last column
        gaps.append((gap_start, width - 1))
        log_message(log_file, f"Gap found: Columns [{gap_start}:{width - 1}]")

    if not gaps:
        log_message(log_file, "No gaps detected; the entire line might be one chunk.")

    return gaps
