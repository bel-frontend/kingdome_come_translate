import xml.etree.ElementTree as ET
import tiktoken
from openai import OpenAI
import os
from dotenv import load_dotenv
#
#def extract_text_from_xml(xml_file):
#    # Parse the XML file
#    tree = ET.parse(xml_file)
#    root = tree.getroot()
#
#    # Extract all text from the XML
#    text_content = []
#    for elem in root.iter():
#        if elem.text:
#            text_content.append(elem.text.strip())
#    return " ".join(text_content)
#
#def count_tokens(text, model="gpt-4o-mini"):
#    # Initialize the tokenizer for the specified model
#    enc = tiktoken.encoding_for_model(model)
#
#    # Encode the text into tokens
#    tokens = enc.encode(text)
#
#    # Return the number of tokens
#    return len(tokens)
#
#if __name__ == "__main__":
#    xml_file_path = "text_ui_dialog.xml"
#    text = extract_text_from_xml(xml_file_path)
#    token_count = count_tokens(text)
#
#    print(f"Token count for the provided XML file: {token_count}")
#
#
#

# Configure your OpenAI API key
# openai.api_key =

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


def translate_text(text,open_ai_key=api_token , target_language="Belarusian",):
    client = OpenAI(
    api_key=(open_ai_key or '').strip(),
    )
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that translates English text to {target_language}."},
            {"role": "user", "content": text}           
        ],
        # model="gpt-4o-mini",
        model="gpt-4o",
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

