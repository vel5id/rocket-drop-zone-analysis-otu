import zipfile
import re
import sys
import os

def extract_text_from_docx(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as zf:
            xml_content = zf.read('word/document.xml').decode('utf-8')
            # Remove XML tags
            text = re.sub('<[^>]+>', '', xml_content)
            # Clean up whitespace
            text = re.sub('\s+', ' ', text).strip()
            return text
    except Exception as e:
        return f"Error reading docx: {e}"

if __name__ == "__main__":
    file_path = r"c:\Users\vladi\Downloads\aero-space\Алгоритмический рассчет области падения ракеты Платон + Рассчет безопасных экологических зон\Aerospace_V_10_engl.docx"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
    else:
        text = extract_text_from_docx(file_path)
        output_path = "paper_content.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Text extracted to {output_path}")
