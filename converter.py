import xml.etree.ElementTree as ET
import json
import os
from datetime import datetime

def xml_to_json(xml_file, json_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    data = []
    application_id = "appIDec34bf94bf92bf5d"
    updated_at = datetime.now().isoformat() + "Z"

    for row in root.findall('Row'):
        cells = row.findall('Cell')
        if len(cells) >= 3:
            key = cells[0].text
            english_text = cells[1].text
            belarusian_text = cells[2].text

            data.append({
                "key": key,
                "language": "en",
                "namespace": "default",
                "value": english_text,
                "applicationId": application_id,
                "id": f"valueID{key}",
                "updated_at": updated_at,
                "appkicationId": application_id,
                "langCode": "en"
            })

            data.append({
                "key": key,
                "language": "ru",
                "namespace": "default",
                "value": belarusian_text,
                "applicationId": application_id,
                "id": f"valueID{key}",
                "updated_at": updated_at,
                "appkicationId": application_id,
                "langCode": "ru"
            })

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Data successfully written to {json_file}")

def convert_all_xml_in_folder(folder_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            xml_file_path = os.path.join(folder_path, filename)
            json_file_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.json")
            xml_to_json(xml_file_path, json_file_path)

if __name__ == "__main__":
    folder_path = './examples/russian'
    output_folder = './json/russian'
    convert_all_xml_in_folder(folder_path, output_folder)