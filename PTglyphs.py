#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess

VERSION = "1.1"

def log(msg):
    print(f"[PTglyphs v{VERSION}] {msg}")

def error_exit(msg):
    log(f"ERROR: {msg}")
    sys.exit(1)

def is_dir_empty(path):
    return not any(os.scandir(path))

def confirm(prompt, dry_run=False):
    if dry_run:
        log(f"[dry-run] {prompt} -- assuming 'yes'")
        return True
    resp = input(f"{prompt} [y/N]: ").strip().lower()
    return resp in ('y', 'yes')

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 PTglyphs.py <dir> [--dry-run]")
        sys.exit(1)

    base_dir = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    glyph_test = 'glyph-test'
    if os.path.exists(glyph_test) and not is_dir_empty(glyph_test):
        error_exit("'glyph-test' directory is not empty.")

    # Step 2: Process join directory
    join_dir = os.path.join(base_dir, 'join')
    if os.path.exists(join_dir):
        if is_dir_empty(join_dir):
            error_exit(f"'{join_dir}' exists but is empty.")

        log(f"Running batch_join_chunks.py on {join_dir}")
        subprocess.run(['python3', 'batch_join_chunks.py', join_dir] + (['--dry-run'] if dry_run else []), check=True)

        # Check if + output exists
        joined_files = [f for f in os.listdir(join_dir) if '+' in f]
        if not joined_files:
            error_exit("No joined files (with '+') found in join directory.")

        log("Joined files:")
        for f in joined_files:
            log(f"  {f}")

        if not confirm("Is the join output acceptable?", dry_run=dry_run):
            error_exit("User rejected join output.")

        for f in joined_files:
            src = os.path.join(join_dir, f)
            dst = os.path.join(base_dir, f)
            log(f"Copying {src} -> {dst}")
            if not dry_run:
                shutil.copy2(src, dst)

    # Step 3: Process split directory
    split_dir = os.path.join(base_dir, 'split')
    if os.path.exists(split_dir):
        if is_dir_empty(split_dir):
            error_exit(f"'{split_dir}' exists but is empty.")

        files = os.listdir(split_dir)
        if not files:
            error_exit(f"'{split_dir}' has no files.")

        log(f"Running PT_chunk_split.py on {split_dir}")
        if not dry_run:
            subprocess.run(['python3', 'PT_chunk_split.py', split_dir], check=True)

        if not confirm("Is the split output acceptable?", dry_run=dry_run):
            error_exit("User rejected split output.")

        output_dir = os.path.join(split_dir, 'output')
        for f in os.listdir(output_dir):
            if f.endswith('contours.png'):
                continue
            src = os.path.join(output_dir, f)
            dst = os.path.join(base_dir, f)
            log(f"Copying {src} -> {dst}")
            if not dry_run:
                shutil.copy2(src, dst)

    # Step 4: Run glyph processing scripts
    if not dry_run:
        subprocess.run(['python3', 'renumber_glyphs.py', base_dir, 'glyph-test'], check=True)
        subprocess.run(['python3', 'glyphids2tex.py', 'glyph-test', 'glyphs4tex/', 'meta.csv'], check=True)
        subprocess.run(['python3', 'glyph2tex.py', 'glyph-test', 'glyphs4tex/'], check=True)

        # Copy PNGs
        for f in os.listdir('glyph-test'):
            if f.endswith('.png'):
                shutil.copy2(os.path.join('glyph-test', f), os.path.join('tables', 'glyphs', f))

        # Copy only new TeX files
        subprocess.run(['rsync', '-av', '--ignore-existing', 'glyphs4tex/', 'tables/'], check=True)

        # Step 5: Compile TeX
        os.chdir('tables')
        subprocess.run(['xelatex', '-file-line-error', '-interaction=nonstopmode', 'PTfonts.tex'], check=True)
        os.chdir('..')
    else:
        log("[dry-run] Skipping glyph processing and LaTeX compilation.")

if __name__ == "__main__":
    main()
