import re

def escape_markdown_v2(text: str) -> str:
    """
    Escapes characters for Telegram's MarkdownV2 parser.
    """
    escape_chars = r'_[]()~`>#+-=|{}.!' 
    
    # This regex uses a negative lookbehind (?<!\\) to ensure we don't escape
    # a character that's already escaped.
    # The `\\\\` is needed because backslashes are special in both Python strings and regex.
    regex = f'(?<!\\\\)([{re.escape(escape_chars)}])'
    
    return re.sub(regex, r'\\\1', text)
