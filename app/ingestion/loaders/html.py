from bs4 import BeautifulSoup
import logfire
from sympy import re

### remember to analyse the edges cases in the html files like empty files, files with only scripts or styles, and files with special characters. to understand how best practises are 


def parse_html(file_path: str) -> str:
    """
        Clean scripts, styles, and other non-text elements from an HTML file and return the cleaned text.
    Args:
        file_path (str): The path to the HTML file to parse.
    """
    with logfire.span("parse_html",filename=file_path):
        try:
            with open(file_path, 'r', encoding='utf-8',errors='ignore') as file:
                content = file.read()
            
        

             # Remove script and style elements
            soup = BeautifulSoup(content, 'html.parser')
            for script_or_style in soup(['script', 'style',"meta","noscript"]):
                script_or_style.decompose()

            #extract text
            text = soup.get_text(separator='\n')

            #clean up the text by removing extra whitespace and newlines
            lines=(line.strip() 
                   for line in text.splitlines()
                   )
            chunks=(phrase.strip() 
                    for line in lines 
                    for phrase in line.split("  ")
                    )
            
            #remove blank lines and join the cleaned lines into a single string
            #example 
            text_clean = "\n".join(
                re.sub(r"\s+", " ", line).strip()
                for line in text.splitlines()
                if line.strip()
                )
            
            return text_clean
        except Exception as e:
            logfire.error(f"Error parsing HTML file: {e}")
            return ""

    