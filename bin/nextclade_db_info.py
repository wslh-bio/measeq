#!/usr/bin/env python3
"""
Write a small TSV file describing the Nextclade dataset or database that was used:
dataset folder/path, dataset name, version, and reference name / accession number
from pathogen.json.
 
Usage:
    nextclade_db_info.py --db_dir <db_dir> [--out_dir <out_dir>]
"""
 
import argparse
import csv
import json
import logging
import os
import re
import shutil
import sys
import zipfile
 
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
 
 
def prepare_db_dir(db_dir):
    """Extract ZIP if provided, else return directory path."""
    if zipfile.is_zipfile(db_dir):
        folder_name = os.path.splitext(os.path.basename(db_dir))[0]
        shutil.rmtree(folder_name, ignore_errors=True)
        logging.info("Extracting database ZIP %s to %s", db_dir, folder_name)
        with zipfile.ZipFile(db_dir, "r") as zip_ref:
            zip_ref.extractall(folder_name)
        return folder_name
    return db_dir
 
 
def find_pathogen_json(db_path):
    """Locate pathogen.json in the given directory (shallowest match wins)."""
    json_file = os.path.join(db_path, "pathogen.json")
    if os.path.isfile(json_file):
        return json_file
 
    matches = []
    for root, _, files in os.walk(db_path):
        if "pathogen.json" in files:
            matches.append(os.path.join(root, "pathogen.json"))
    if not matches:
        return None
 
    matches.sort(key=lambda path: (path.count(os.sep), path))
    if len(matches) > 1:
        logging.warning("Found %d pathogen.json files in %s; using %s", len(matches), db_path, matches[0])
    return matches[0]
 
 
def get_db_name_and_output_path(raw_db_dir, extracted_db_dir, json_path, out_dir="."):
    """
    Work out the database name and the path of the output TSV.
    """
    logging.info("Determining the dataset name.")
    json_dir = os.path.realpath(os.path.dirname(json_path))
    extracted_real = os.path.realpath(extracted_db_dir)
 
    if zipfile.is_zipfile(raw_db_dir):
        base_path = os.path.splitext(os.path.realpath(raw_db_dir))[0]
        rel_subpath = os.path.relpath(json_dir, extracted_real)
        full_db_path = base_path if rel_subpath == "." else os.path.join(base_path, rel_subpath)
    else:
        full_db_path = json_dir

    # Looks at the file path
    parts = [p for p in os.path.normpath(full_db_path).split(os.sep) if p]
 
    db_folder_name = parts[-1] if parts else "unknown_db"
 
    # Searching backwards until it finds a nextrain folder
    for idx in range(len(parts) - 1, -1, -1):
        if parts[idx].lower() == "nextstrain":
            db_folder_name = "/".join(parts[idx:])
            break
 
    # Build a safe TSV path from the folder name
    safe_name = db_folder_name.replace("/", "_").replace("\\", "_")
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", safe_name).strip("_") or "nextclade_dataset"
 
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{safe_name}_db_info.tsv")
 
    return safe_name, out_path
 
 
def build_db_info(json_path, db_folder_name):
    """Extract dataset info from pathogen.json and include db_name."""
    with open(json_path, encoding="utf-8") as fh:
        data = json.load(fh)
 
    attrs = data.get("attributes") if isinstance(data.get("attributes"), dict) else {}
    ref = data.get("reference") if isinstance(data.get("reference"), dict) else {}
 
    name = attrs.get("name") or data.get("name", "Unknown")
    ref_name = attrs.get("reference name") or ref.get("name", "Unknown")
    ref_acc = attrs.get("reference accession") or ref.get("accession", "Unknown")
 
    if isinstance(data.get("version"), dict):
        version = data.get("version").get("tag") or data.get("version").get("name")
    else:
        version = data.get("version")
 
    for label, value in (
        ("name", name),
        ("version", version),
        ("reference name", ref_name),
        ("reference accession", ref_acc),
    ):
        if not value or value == "Unknown":
            logging.warning("No dataset %s found in %s; writing 'Unknown'", label, json_path)
 
    return {
        "db_name": db_folder_name,
        "nextclade_db_name": name,
        "nextclade_db_version": version or "Unknown",
        "nextclade_db_reference_name": ref_name,
        "nextclade_db_reference_accession": ref_acc,
    }
 
 
def write_tsv(db_info, out_tsv):
    """Write the dataset information as a one-row TSV with a header."""
    logging.info("Writing database info to %s", out_tsv)
    try:
        with open(out_tsv, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(db_info), delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerow(db_info)
    except OSError as e:
        logging.error("Failed to write TSV: %s", e)
        return 7
    logging.info("Database info TSV written successfully.")
    return 0
 
 
class CompileResults(argparse.ArgumentParser):
    """Custom ArgumentParser that prints help on error."""
 
    def error(self, message):
        self.print_help()
        sys.stderr.write(f"\nERROR DETECTED: {message}\n")
        sys.exit(1)
 
 
def main():
    """Parse arguments, build the dataset summary, and write it to a TSV."""
    parser = CompileResults(
        prog="nextclade_db_info.py",
        description="Get Nextclade database information",
        epilog="Example usage: nextclade_db_info.py --db_dir <db_dir> --out_dir <out_dir>",
    )
    parser.add_argument(
        "--db_dir",
        required=True,
        help="Directory containing pathogen.json or ZIP",
    )
    parser.add_argument(
        "--out_dir",
        default=".",
        help="Directory to write the output TSV (default: current directory)",
    )
    args = parser.parse_args()
 
    logging.info("Preparing database directory.")
    db_dir = prepare_db_dir(args.db_dir)
 
    logging.info("Finding pathogen.json.")
    json_file = find_pathogen_json(db_dir)
    if json_file is None:
        logging.error("pathogen.json not found in %s", db_dir)
        return 2

    logging.info("Determinging dataset name and sanitizing dataset name for tsv file and filename.")
    db_name, out_path = get_db_name_and_output_path(args.db_dir, db_dir, json_file, out_dir=args.out_dir)
 
    logging.info("Building database info.")
    info = build_db_info(json_file, db_name)
 
    return write_tsv(info, out_path)
 

if __name__ == "__main__":
    sys.exit(main())
