import xml.etree.ElementTree as ET
from openai import OpenAI
import os
from dotenv import load_dotenv
from goman_live_sdk import PromptSDK


sdk = PromptSDK(application_id="appID87b9abb0d07b", api_key="apkdf59b4097d660c2a8e38c9d2947085fb4a66f1234275eeeb0ac572c18bf00427", base_url="https://api.goman.live")
prompt_id = "676dc3cd8a83600397efe178"


# read tocken from  .env file
load_dotenv()
api_token = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    # api_token = api_token,
   # This is the default and can be omitted
)

# xml_file_path = "text_ui_misc.xml"
xml_file_path = "text_ui_tutorials.xml"
xml_folder = "russian"
xnl_path = os.path.join(xml_folder, xml_file_path)
output_folder = "output"
output_path = os.path.join(output_folder, xml_file_path)


def translate_text(text,open_ai_key , target_language="Belarusian",):
    sdk_prompt = sdk.get_prompt_from_remote(prompt_id)  # Await SDK call
    print('SDK result:',sdk_prompt.value,)
    client = OpenAI(
    api_key=(open_ai_key or '').strip(),
    )
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": sdk_prompt.value},
            {"role": "user", "content": text}           
        ],
        # model="gpt-4o-mini",
        model="gpt-4o",
        # model="gpt-4o-2024-08-06",
    ) 
    return completion.choices[0].message.content


def parse_and_translate_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for row in root.findall('Row'):
        cells = row.findall('Cell')
        if len(cells) >= 3:
            english_text = cells[2].text
            if english_text:
                translated_text = translate_text(english_text)
                cells[2].text = translated_text

    tree.write(output_path, encoding='utf-8', xml_declaration=True)


if __name__ == "__main__":
    parse_and_translate_xml(xnl_path)

