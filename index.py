import xml.etree.ElementTree as ET
from openai import OpenAI
import os
from dotenv import load_dotenv


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
    print(open_ai_key)
    client = OpenAI(
    api_key=(open_ai_key or '').strip(),
    )
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": f"""You are a helpful assistant that translates English text to {target_language}.
             We are translating game about middle ages. Words in [] do not translate. For example [Hairstyles] should be [Hairstyles]
             Next  words should  translated:
             sir - пан,
             Hair o' the Dog potion - зелле "Сабачча поўсць",
             charisma - Абаянне,
             vitality - жывучасць,
             skill Speech - красамоўства,
             like one - як  адзін з іх,
             potion - зелле,
             potions - зеллі,
             a Cuman - полавец, полаўцы 
             road - дарога, шлях,
             you - ты,
             Henry - Індрык,
             Reeky - Смярдзюк,
             The nobility (aristocracy) - шляхта,
             nobleman - шляхціч,
             Hanush - Януш,
             Johanka - Ёханка,
             Wenceslas - Вацлаў,
             Bohemia - Багемія,
             Sigismund - Жыгімонт,
             charcoal-burner - вугляпал,
             <br/>&nbsp;<br/> - <br/>&nbsp;<br/>  
             Kuttenberg - Кутна-Гора,
             Uzhitz - Ужыца,
             Samopše - Самапеш,
             Sasau - Сазаў,
             the Holy Lance - дзіда,
             Merhojed - Мрхаеды,
             safe-conduct documenе - ахоўная  грамата,
             the Bailiff - ваявода,
             Racek Kobyla - Рацык Кабыла,
             Sir Hans Capon - Пан Ян  Птачак,
             Leipa - Ліпа,
             Conspicuousness - Прыкметнасць,
             Visibility - Бачнасць,
             Fast talk - Красамоўства,

            
              """},
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

