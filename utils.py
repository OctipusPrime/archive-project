import os
import shutil
from prompts import README_PROMPT  # Import the prompt

def collect_repository_structure(src_dir: str) -> str:
    """
    Generates a string representation of the repository structure and includes content of each .py file.
    """
    structure = []

    for root, dirs, files in os.walk(src_dir):
        level = root.replace(src_dir, '').count(os.sep)
        indent = '    ' * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        subindent = '    ' * (level + 1)
        for file in files:
            structure.append(f"{subindent}{file}")
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                structure.append(f"{subindent}```python\n{content}\n{subindent}```")

    return '\n'.join(structure)


def generate_readme(archive_dir_path: str, openai_client):
    """
    Generates a README.md file with an overview of the project and descriptions of individual files.
    """
    repo_structure = collect_repository_structure(archive_dir_path)
    # Construct messages for AzureOpenAI using the imported prompt
    messages = [
        {"role": "system", "content": README_PROMPT},
        {"role": "user", "content": repo_structure}
    ]

    # Get completion from AzureOpenAI
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3
    )

    readme_content = response.choices[0].message.content

    # Determine the project directory name for the README file
    project_dir_name = os.path.basename(os.path.normpath(archive_dir_path))
    readme_filename = f"README_{project_dir_name}.md"

    # Write the README.md file
    readme_path = os.path.join(archive_dir_path, readme_filename)
    with open(readme_path, 'w', encoding='utf-8') as readme_file:
        readme_file.write(readme_content)


def process_directory(src_dir: str, dst_dir: str, skip_dirs: set, skip_files: set) -> bool:
    """
    Recursively checks 'src_dir' for .py files (directly or in its subdirectories).
    Returns True if at least one .py file is found in 'src_dir' or its descendants.

    If a .py file is found:
    - Ensures 'dst_dir' exists (creates recursively with os.makedirs).
    - Exports each .py to a .md file, preserving the file name (minus .py extension).
    - Copies any existing .md files to the destination directory.
    - Recursively processes subdirectories that contain .py files.

    skip_dirs: names of directories to ignore entirely
    skip_files: names of individual files to skip
    """
    # List the contents of the source directory
    try:
        entries = os.listdir(src_dir)
    except PermissionError:
        # If we don't have permission to read a directory, skip it
        return False

    found_python = False

    # First pass: we only check if there are .py files or child dirs that have .py
    for entry in entries:
        if entry in skip_dirs or "env" in entry:
            continue

        # Skip the archiver script or any other files in skip_files
        if entry in skip_files:
            continue

        src_path = os.path.join(src_dir, entry)

        if os.path.isdir(src_path):
            # Recursively check if the subdirectory contains .py files
            if process_directory(src_path, os.path.join(dst_dir, entry), skip_dirs, skip_files):
                found_python = True
        else:
            # If it's a .py file, we have a match
            if entry.endswith('.py'):
                found_python = True

    # If we found any .py files in this directory (or children), create dst_dir & export them
    if found_python:
        os.makedirs(dst_dir, exist_ok=True)  # create the destination directory if needed

        # Second pass: actually copy & transform .py to .md and copy .md files
        for entry in entries:
            if entry in skip_dirs or "env" in entry:
                continue
            if entry in skip_files:
                continue

            src_path = os.path.join(src_dir, entry)
            dst_sub_path = os.path.join(dst_dir, entry)

            if os.path.isdir(src_path):
                # We already know there's something in there, so process again to copy .py files
                process_directory(src_path, dst_sub_path, skip_dirs, skip_files)
            else:
                # Convert .py -> .md
                if entry.endswith('.py'):
                    with open(src_path, 'r', encoding='utf-8') as f:
                        code_content = f.read()

                    md_filename = os.path.splitext(entry)[0] + '.md'
                    md_path = os.path.join(dst_dir, md_filename)

                    with open(md_path, 'w', encoding='utf-8') as md_file:
                        md_file.write("```python\n")
                        md_file.write(code_content)
                        md_file.write("\n```")
                
                # Copy .md files
                elif entry.endswith('.md'):
                    shutil.copy2(src_path, dst_sub_path)

    return found_python 