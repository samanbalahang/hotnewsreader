import os
import shutil

def empty_news_folder(folder_path):
    """
    Deletes all files and subfolders inside the specified path.
    If the folder doesn't exist, it creates it.
    """
    # 1. Check if folder exists; if not, create it and exit
    if not os.path.exists(folder_path):
        print(f"📁 Folder '{folder_path}' did not exist. Creating it now...")
        os.makedirs(folder_path)
        return

    print(f"🧹 Cleaning up the '{folder_path}' folder...")
    
    # 2. Iterate and delete contents
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Delete file or symlink
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Delete entire subdirectory
        except Exception as e:
            print(f'❌ Failed to delete {file_path}. Reason: {e}')
    
    print("✅ Folder is now empty and ready for fresh news.")

def ensure_data_dirs(directories):
    """
    Helper to ensure all required directories exist at startup.
    Expects a list of paths like ['data', 'data/raw_news']
    """
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created missing directory: {directory}")

if __name__ == "__main__":
    # Test block
    empty_news_folder('data/raw_news')