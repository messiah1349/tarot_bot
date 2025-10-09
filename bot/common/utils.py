import re

def escape_markdown_v2(input_text: str) -> str:
    header_pattern = r'[#]+\s+(.+?)\s*\n'
    header_replacement = r'*_\1_*\n\n'
    input_text = re.sub(header_pattern, header_replacement, input_text)
    processed_text = input_text.replace('#', '')
    processed_text = processed_text.replace('**', '*')
    processed_text = processed_text.replace('\\n', '\n')
    for symb in '[]()~>!.+-=|{}':
        processed_text = processed_text.replace(symb, f'\\{symb}')

    # Use a negative lookbehind `(?<!\\)` to find a dot `.` that is not
    # preceded by a backslash `\\`. Then, replace that dot with `\.`.
    # processed_text = re.sub(r'(?<!\\)\.', r'\.', processed_text) #re.sub(r'(?<!\\)\.', r'\.', processed_text)

    return processed_text
