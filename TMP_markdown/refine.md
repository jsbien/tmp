# Phase 5 Specification: Processing Speckles from Logs

## Introduction

During the review of `segment-all` outputs, many speckles were erroneously recognized as characters. These speckles have been marked manually in the log files. This phase involves converting these notes into a format suitable for further processing using a Python script named `collect-speckles.py`.

The script should also preserve other notes made in the log files for potential use later.

---

## Objective

The script processes logs to:
1. Update log files with modified content.
2. Move speckle images to a new directory (`speckles`) for further inspection.
3. Append speckle-related data to a new CSV file (`speckles.csv`) for indexing.

---

## Inputs

- **Directory Argument**: The script accepts a directory name as input.
- **Subdirectory Contents**:
  - `.log` files: Logs to be processed.
  - Index files (`.csv`): Metadata for processing speckles.
  - Snippet graphic files: Image files corresponding to speckles.

---

## Outputs

- **Directory Structure**:
  - Processed data will be saved in a `speckles` subdirectory of the provided directory.
- **File Outputs**:
  - `speckles.csv`: A CSV file with speckle-related data for indexing.
  - Updated `.log` files: Stored in the original `.log` file's directory.

---

## Processing Steps

### 1. Identify Relevant `.log` Files

- Look for `.log` files containing speckle identifiers (`-`).
- Ignore metadata in logs, including:
  - The header (first line).
  - The timestamp (last line).
  - Lines after `Invalid strips (no letterboxes):`.

#### Log Content Syntax

```plaintext
<line number>: <letterboxes count> <optional speckle identifiers and other comments>
```

#### Examples:

```plaintext
1: 1 -l
1: 30 -22-24
3: 44 -38
```

---

### 2. Extract Speckle Identifiers

Speckle identifiers can be:
- **Numerical Identifiers** (`-<number>`):
  - May appear multiple times in a line.
  - Can be interspersed with other notes.
- **Line Identifiers** (`-l`).

#### Examples:

```plaintext
1: 1 -l
1: 30 -22-24
```

---

### 3. Convert Speckle Identifiers

#### **Index Form**:
- For numerical identifiers: `l <line number> b <letterbox number>`.
- For line identifiers: `l <line number>`.

**Examples**:
- `1: 30 -22-24` → `l 1 b 22`, `l 1 b 24`.
- `1: 1 -l` → `l 1`.

#### **Snippet Form**:
- Similar to the index form, but with:
  - All numbers padded to 3 digits.
  - Underscores (`_`) instead of spaces.
  - `line` and `box` prefixes instead of `l` and `b`.

**Examples**:
- `1: 30 -22-24` → `line_001 box_22`, `line_001 box_24`.
- `1: 1 -l` → `line_001`.

---

### 4. Extract Metadata from Logs

#### Log File Name:
- Format: `<table-id>-<timestamp>.log`
- Extract `<table-id>` for processing.

#### Header Line:
- Example: `Arguments: input_file=masks/m89.tiff, djvu_file=Wirzbięta-15_PT11_566.djvu, output_directory=89`
- Extract the base name of `djvu_file` (e.g., `Wirzbięta-15_PT11_566`) as the `table-name`.

---

### 5. Locate Relevant Index File

- The `.csv` file corresponding to the log is:
  - The only `.csv` file in the same directory.
  - Named `<table-name>.csv`.

---

### 6. Actions for Speckle Identifiers

#### **Numeric Speckle Identifiers (`-<number>`)**:

1. **Move Image Files**:
   - Match the snippet form using the regular expression `*<snippet form>*`.
   - Move the file to the `speckles` directory.

2. **Update `speckles.csv`**:
   - Append the corresponding line from the `.csv` file, matching `*<snippet form>*`.

   > **Note**: Only one matching line should exist in the index.

3. **Update the Log File**:
   - Copy the `.log` file and rename it with the current timestamp.
   - Add a new timestamp line above the existing one.
   - Place all relevant speckle IDs in brackets.

   **Examples**:
   - Original log entry: `1: 30 -22-24`
   - Updated log entry: `1: 30 [-22][-24]`

#### **Line Speckle Identifiers (`-l`)**:

1. Process as a numeric speckle identifier, but:
   - Multiple matching lines/files may exist for line identifiers.

2. Update the Log File:
   - If no numeric identifiers exist, create a new log file.
   - Add the entire line speckle identifier in brackets.
   - Renumber remaining lines.

---

### 7. Implementation Plan

1. **Directory Traversal**:
   - Locate `.log` files containing speckle identifiers (`-`).

2. **Log Parsing**:
   - Extract numeric (`-<number>`) and line (`-l`) speckle identifiers.
   - Determine corresponding image and `.csv` files.

3. **File Operations**:
   - Move speckle image files to the `speckles` directory.
   - Update `.log` files and save new versions.
   - Append data to `speckles.csv`.

4. **Error Handling**:
   - Handle missing files gracefully with appropriate logging.

---

## Error Handling

- **Missing Files**:
  - Log missing `.csv` or image files with clear error messages.
- **Unexpected Log Structure**:
  - Skip processing and log an error if the log structure does not match expectations.

---

## Notes

- The script should maintain all existing metadata in `.log` files.
- Snippet forms and index forms should strictly follow the specified format.
