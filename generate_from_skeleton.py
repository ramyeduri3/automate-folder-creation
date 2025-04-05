import argparse
import os
import shutil
import sys
import re

def is_valid_name(name):
    return re.match(r'^[a-zA-Z0-9-_]+$', name)

def replace_placeholders_in_file(file_path, placeholders):
    with open(file_path, 'r') as file:
        content = file.read()

    for key, value in placeholders.items():
        content = content.replace(f'{{{key}}}', value)

    with open(file_path, 'w') as file:
        file.write(content)

def replace_placeholders_in_path(path, placeholders):
    for key, value in placeholders.items():
        path = path.replace(f'{{{key}}}', value)
    return path

def process_folder(src, dest, placeholders):
    for root, dirs, files in os.walk(src):
        relative_path = os.path.relpath(root, src)
        dest_dir = os.path.join(dest, replace_placeholders_in_path(relative_path, placeholders))
        os.makedirs(dest_dir, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            new_file_name = replace_placeholders_in_path(file, placeholders)
            dest_file = os.path.join(dest_dir, new_file_name)
            shutil.copy2(src_file, dest_file)
            replace_placeholders_in_file(dest_file, placeholders)

def main():
    parser = argparse.ArgumentParser(description="Generate redb files from skeleton")
    parser.add_argument('--name', required=True)
    parser.add_argument('--env', required=True)
    parser.add_argument('--team', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--project', required=True)

    args = parser.parse_args()

    # Input validation
    for arg_name in vars(args):
        value = getattr(args, arg_name)
        if not is_valid_name(value):
            print(f"❌ Invalid value for '{arg_name}': '{value}'. Only letters, numbers, hyphens, and underscores are allowed.")
            sys.exit(1)

    placeholders = {
        'placeholder': args.name,
        'env': args.env,
        'team': args.team,
        'region': args.region,
        'project': args.project
    }

    template_dir = 'skeleton-redb'
    output_dir = os.path.join('redb', f'{args.name}-redb')

    if os.path.exists(output_dir):
        print(f"❌ Output directory '{output_dir}' already exists. Aborting to prevent overwrite.")
        sys.exit(1)

    process_folder(template_dir, output_dir, placeholders)
    print(f"✅ Successfully generated files in: {output_dir}")

if __name__ == "__main__":
    main()
