import os

def find_empty_files(root_dir):
    empty_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            # Get the relative path
            relative_path = os.path.relpath(file_path, root_dir)
            
            # Check if the file is empty
            if os.path.getsize(file_path) == 0:
                empty_files.append(relative_path)

    return empty_files

def main():
    # Get the current directory
    current_dir = os.getcwd()

    print(f"Searching for empty files in: {current_dir}")
    print("-----------------------------------")

    empty_files = find_empty_files(current_dir)

    if empty_files:
        print("Empty files found:")
        for file in empty_files:
            print(f"- {file}")
        print(f"\nTotal empty files: {len(empty_files)}")
    else:
        print("No empty files found.")

if __name__ == "__main__":
    main()
