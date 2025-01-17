import os
import sys
import shutil
from utils import process_directory, generate_readme
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# Load environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

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

    # The script name itself, so we can skip it
    script_name = os.path.basename(sys.argv[0]) 
    
    # Get the project directory from command line arguments
    if len(sys.argv) < 2:
        print("Please provide the path to the project directory.")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    if not os.path.isdir(project_dir):
        print(f"The path '{project_dir}' is not a valid directory.")
        sys.exit(1)
    
    # Determine the archive directory
    if len(sys.argv) >= 3:
        archive_base_dir = sys.argv[2]
    else:
        archive_base_dir = "/Users/yanbarta/Library/Mobile Documents/iCloud~md~obsidian/Documents/The Foundation/Archive"
    
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
    skip_files = {script_name}

    # Check if we have any .py files in the project directory
    found_any_python = process_directory(project_dir, archive_dir_path, skip_dirs, skip_files)

    if found_any_python:
        print(
            f"Created '{archive_dir_name}' in:\n  {archive_base_dir}\n"
            "containing .md files for every .py file."
        )
        generate_readme(archive_dir_path, openai_client)  # Pass the client to generate_readme
        print(f"README.md has been created in '{archive_dir_path}'.")
    else:
        print("No Python files found; no archive directory created.")


if __name__ == "__main__":
    main() 