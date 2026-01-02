import os
import sys


SKIP_DIRS = {
    '.git', 'node_modules', 'venv', '__pycache__',
    '.venv', 'dist', 'build', '.idea', 'target'
}

SKIP_FILES = {
    'package-lock.json',
    'yarn.lock',
    'pnpm-lock.yaml',
    '.DS_Store'
}

ALLOWED_EXTENSIONS = (
    '.py', '.js', '.ts', '.jsx', '.tsx',
    '.java', '.cpp', '.h', '.cs',
    '.html', '.css',
    '.json', '.yml', '.yaml', '.xml',
    '.md', '.txt',
    '.sh', '.bat',
    '.sql',
    '.env'
)

def generate_tree(root_dir, output_file, prefix="", is_last=True):
    tree = []
    root_name = os.path.basename(root_dir)
    tree.append(f"{prefix}{'└── ' if is_last else '├── '}{root_name}")

    prefix += "    " if is_last else "│   "
    output_abs = os.path.abspath(output_file)

    try:
        items = sorted(os.listdir(root_dir))
        visible_items = []

        for item in items:
            item_path = os.path.join(root_dir, item)

            if os.path.abspath(item_path) == output_abs:
                continue

            if os.path.isdir(item_path):
                if item in SKIP_DIRS:
                    continue
                visible_items.append(item)

            else:
                if item in SKIP_FILES:
                    continue
                if item.lower().endswith(ALLOWED_EXTENSIONS):
                    visible_items.append(item)

        for i, item in enumerate(visible_items):
            item_path = os.path.join(root_dir, item)
            is_last_item = i == len(visible_items) - 1

            if os.path.isdir(item_path):
                tree.extend(
                    generate_tree(item_path, output_file, prefix, is_last_item)
                )
            else:
                tree.append(
                    f"{prefix}{'└── ' if is_last_item else '├── '}{item}"
                )

    except PermissionError:
        tree.append(f"{prefix}└── [Permission denied]")

    return tree


def collect_codebase(root_dir, output_file):
    output_abs = os.path.abspath(output_file)

    with open(output_file, 'w', encoding='utf-8') as out:
        # Directory tree
        out.write("=== Directory Structure ===\n")
        tree = generate_tree(root_dir, output_file)
        out.write("\n".join(tree))
        out.write("\n\n=== File Contents ===\n\n")

        for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

            for filename in filenames:
                if filename in SKIP_FILES:
                    continue

                if not filename.lower().endswith(ALLOWED_EXTENSIONS):
                    continue

                file_path = os.path.join(dirpath, filename)

                if os.path.abspath(file_path) == output_abs:
                    continue

                rel_path = os.path.relpath(file_path, root_dir)
                out.write(f"--- File: {rel_path} ---\n\n")

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        out.write(f.read())
                        out.write("\n\n")
                except UnicodeDecodeError:
                    out.write("[[Binary or non-text file skipped]]\n\n")
                except Exception as e:
                    out.write(f"[[Error reading file: {e}]]\n\n")

    print(f"✅ Codebase exported to {output_file}")


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    output = sys.argv[2] if len(sys.argv) > 2 else "codebase_smart.txt"
    collect_codebase(root, output)
