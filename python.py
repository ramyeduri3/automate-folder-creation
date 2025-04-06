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

def is_common_file(relative_path, placeholders):
    common_files = {
        "chart.yaml",
        "templates/role.yaml",
        "templates/rolebinding.yaml",
        "templates/ingress.yaml",
        f"redb-{placeholders['appshortname']}-np.yaml"
    }
    return relative_path in common_files

def process_folder(src, dest, placeholders, dry_run=False):
    files_to_generate = []
    existing_files = []
    skipped_common = []

    for root, dirs, files in os.walk(src):
        relative_path = os.path.relpath(root, src)
        target_dir = os.path.join(dest, replace_placeholders_in_path(relative_path, placeholders))
        os.makedirs(target_dir, exist_ok=True)

        for file in files:
            replaced_file_name = replace_placeholders_in_path(file, placeholders)
            relative_file_path = os.path.normpath(os.path.join(relative_path, replaced_file_name))
            dest_file = os.path.join(target_dir, replaced_file_name)
            src_file = os.path.join(root, file)

            if os.path.exists(dest_file):
                if is_common_file(relative_file_path, placeholders):
                    skipped_common.append(dest_file)
                    continue
                else:
                    existing_files.append(dest_file)
            else:
                files_to_generate.append((src_file, dest_file))

    if dry_run:
        print("🔍 DRY RUN PREVIEW")
        for _, dest_file in files_to_generate:
            print(f"📝 Would create: {dest_file}")
        for skipped in skipped_common:
            print(f"ℹ️ Would skip existing common file: {skipped}")
        if existing_files:
            print("❌ The following env-specific files already exist and would block the run:")
            for f in existing_files:
                print(f"   - {f}")
        return

    if existing_files:
        print("❌ The following env-specific files already exist and will not be overwritten:")
        for f in existing_files:
            print(f"   - {f}")
        sys.exit(1)

    for src_file, dest_file in files_to_generate:
        shutil.copy2(src_file, dest_file)
        replace_placeholders_in_file(dest_file, placeholders)
        print(f"✅ Created file: {dest_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate redb files from skeleton")
    parser.add_argument('--appshortname', required=True)
    parser.add_argument('--namespace', required=True)
    parser.add_argument('--memorysize', required=True)
    parser.add_argument('--recname', required=True)
    parser.add_argument('--replication', required=True)
    parser.add_argument('--shardcount', required=True)
    parser.add_argument('--tlsmode', required=True)
    parser.add_argument('--env', required=True)
    parser.add_argument('--databasesecretname', required=True)
    parser.add_argument('--dry-run', action='store_true', help='Preview only, do not write files')

    args = parser.parse_args()

    for arg_name in vars(args):
        value = getattr(args, arg_name)
        if arg_name != "dry_run" and not is_valid_name(value):
            print(f"❌ Invalid value for '{arg_name}': '{value}'. Only letters, numbers, hyphens, and underscores are allowed.")
            sys.exit(1)

    placeholders = {
        'appshortname': args.appshortname,
        'namespace': args.namespace,
        'memorysize': args.memorysize,
        'recname': args.recname,
        'replication': args.replication,
        'shardcount': args.shardcount,
        'tlsmode': args.tlsmode,
        'env': args.env,
        'databasesecretname': args.databasesecretname
    }

    template_dir = 'skeleton_redb'
    output_dir = os.path.join('eastus', 'redb', f'{args.appshortname}-redb')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created folder: {output_dir}")
    else:
        print(f"📁 Folder exists: {output_dir} — will check for duplicate files")

    process_folder(template_dir, output_dir, placeholders, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
