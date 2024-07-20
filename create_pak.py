import os
import zipfile

def create_pak_archive(root_folder, archive_name):
    # Ensure the archive_name ends with .pak
    if not archive_name.endswith('.pak'):
        archive_name += '.pak'
    
    # Create a zip file with compression
    with zipfile.ZipFile(archive_name, 'w', compression=zipfile.ZIP_DEFLATED ) as pak_archive:
        for root, dirs, files in os.walk(root_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Write the file to the archive, preserving the directory structure
                pak_archive.write(file_path, os.path.relpath(file_path, start=root_folder))
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                # Ensure the directory itself is included (even if empty)
                pak_archive.write(dir_path, os.path.relpath(dir_path, start=root_folder))

if __name__ == "__main__":
    # Root folder to include in the .pak file
    root_folder = './GameData'
    
    # Name of the resulting .pak archive
    archive_name = 'GameData.pak'
    
    create_pak_archive(root_folder, archive_name)
    print(f'Created {archive_name} with contents of the {root_folder} folder')
