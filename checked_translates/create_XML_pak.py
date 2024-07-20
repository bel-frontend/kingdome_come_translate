import os
import zipfile

def create_pak_archive(xml_files, archive_name):
    # Ensure the archive_name ends with .pak
    if not archive_name.endswith('.pak'):
        archive_name += '.pak'
    
    with zipfile.ZipFile(archive_name, 'w') as pak_archive:
        for file in xml_files:
            pak_archive.write(file, os.path.basename(file))

if __name__ == "__main__":
    # find  all xml files in the folder
    xml_files = []
    for root, dirs, files in os.walk('../belarussian'):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    # xml_files = ['example1.xml', 'example2.xml']  # Add your XML file names here

    # List your XML files here
    # xml_files = ['example1.xml', 'example2.xml']  # Add your XML file names here
    
    # Name of the resulting .pak archive
    archive_name = 'Russian_xml.pak'
    
    create_pak_archive(xml_files, archive_name)
    print(f'Created {archive_name} with files: {xml_files}')
