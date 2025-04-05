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

def process_folder(src, dest, placeholders, env_suffix):
    for root, dirs, files in os.walk(src):
        for file in files:
            # Replace placeholders in content and file name
            new_file_name = replace_placeholders_in_path(file, placeholders).replace('.yaml', f'-{env_suffix}.yaml')
            dest_file = os.path.join(dest, new_file_name)

            if os.path.exists(dest_file):
                print(f"⚠️ Skipping existing file: {dest_file}")
                continue

            src_file = os.path.join(root, file)
            shutil.copy2(src_file, dest_file)
            replace_placeholders_in_file(dest_file, placeholders)
            print(f"✅ Created file: {dest_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate redb files from skeleton")
    parser.add_argument('--name', required=True)
    parser.add_argument('--env', required=True)
    parser.add_argument('--team', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--project', required=True)

    args = parser.parse_args()

    # Validate inputs
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

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created folder: {output_dir}")
    else:
        print(f"📁 Folder already exists: {output_dir} — will append new files if needed")

    process_folder(template_dir, output_dir, placeholders, args.env)

if __name__ == "__main__":
    main()
