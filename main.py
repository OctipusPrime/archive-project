import os
import sys
import shutil
from utils import process_directory, generate_readme
from dotenv import load_dotenv
from openai import AzureOpenAI
import argparse

load_dotenv()

# Load environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
ARCHIVE_BASE_DIR = os.getenv("ARCHIVE_BASE_DIR", "/Users/yanbarta/Library/Mobile Documents/iCloud~md~obsidian/Documents/The Foundation/Archive")

# Create the OpenAI client
openai_client = AzureOpenAI(azure_endpoint=AZURE_OPENAI_ENDPOINT, api_key=AZURE_OPENAI_API_KEY, api_version="2024-04-01-preview")

def main():
    """
    Main driver:
      - Accept project directory as a command line argument.
      - Optionally accept an archive directory as a second command line argument.
      - Create archive output inside the specified or default archive directory, named 'archive_<project_dir_name>'.
      - Recursively skip 'venv', 'data', and the script file itself.
      - Only create directories in the archive if they contain (directly or indirectly) .py files.
      - Each .py file is exported to .md (fenced code block), preserving structure.
    """
    parser = argparse.ArgumentParser(description='Archive a project directory into Obsidian.')
    parser.add_argument('project_dir', type=str, help='Path to the project directory.')
    parser.add_argument('archive_base_dir', type=str, nargs='?', default=ARCHIVE_BASE_DIR, help='Path to the archive base directory.')
    parser.add_argument('--no-readme', action='store_true', help='Do not generate a README file.')
    parser.add_argument('--no-file-description', action='store_true', help='Do not generate descriptions for each file.')
    args = parser.parse_args()

    project_dir = args.project_dir
    archive_base_dir = args.archive_base_dir
    no_readme = args.no_readme
    no_file_description = args.no_file_description

    if not os.path.isdir(project_dir):
        print(f"The path '{project_dir}' is not a valid directory.")
        sys.exit(1)
    
    dir_name = os.path.basename(os.path.abspath(project_dir))
    archive_dir_name = dir_name

    # The final path in the specified or default archive directory
    archive_dir_path = os.path.join(archive_base_dir, archive_dir_name)

    # If that exact archive directory already exists, delete it to overwrite
    if os.path.exists(archive_dir_path):
        print(f"The directory '{archive_dir_path}' already exists. Deleting it to overwrite with a new version.")
        shutil.rmtree(archive_dir_path)  # Remove the existing directory

    # Directories and files to skip
    skip_dirs = {"venv", "data", "__pycache__"}

    # Check if we have any .py files in the project directory
    found_any_python = process_directory(project_dir, archive_dir_path, skip_dirs, no_file_description, openai_client)

    if found_any_python:
        print(
            f"Created '{archive_dir_name}' in:\n  {archive_base_dir}\n"
            "containing .md files for every .py file."
        )
        if not no_readme:
            generate_readme(archive_dir_path, openai_client)  # Pass the client to generate_readme
            print(f"README has been created in '{archive_dir_path}'.")
    else:
        print("No Python files found; no archive directory created.")


if __name__ == "__main__":
    main() 