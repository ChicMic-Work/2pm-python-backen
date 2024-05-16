import re
from unidecode import unidecode

def unaccent(s):
    """
    Simulate the unaccent function.
    Replace accented characters with their non-accented equivalents.
    """
    # Define your own mapping or use a library for more comprehensive conversion
    accent_map = {
        'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a', 'æ': 'ae', 'À': 'A', 'Á': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A', 'Å': 'A', 'Æ': 'AE',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e', 'È': 'E', 'É': 'E', 'Ê': 'E', 'Ë': 'E',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i', 'Ì': 'I', 'Í': 'I', 'Î': 'I', 'Ï': 'I',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o', 'õ': 'o', 'ø': 'o', 'œ': 'oe', 'Ò': 'O', 'Ó': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O', 'Ø': 'O', 'Œ': 'OE',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u', 'ü': 'u', 'Ù': 'U', 'Ú': 'U', 'Û': 'U', 'Ü': 'U',
        'ñ': 'n', 'Ñ': 'N',
        'ç': 'c', 'Ç': 'C',
        'ð': 'd', 'Ð': 'D',
        '¿': '' , '¡': '' , 'ß': 'ss'
    }
    return ''.join(accent_map.get(char, char) for char in s)

def normalize_nickname(nickname):
    
    normalized_nickname = unidecode(nickname)
    
    # Remove accents
    normalized_nickname = unaccent(normalized_nickname)
    
    pattern = re.compile(r'[^a-zA-Z\s]')
    
    if pattern.search(normalized_nickname):
        raise
    
    # Replace non-whitespace characters with a single space
    normalized_nickname = re.sub(r'[^a-zA-Z\s]', ' ', normalized_nickname)
    
    # Replace sequences of whitespace characters with a single space
    normalized_nickname = re.sub(r'\s+', ' ', normalized_nickname)
    
    # Trim leading and trailing whitespace
    normalized_nickname = normalized_nickname.strip()
    
    # Convert to uppercase
    normalized_nickname = normalized_nickname.upper()
    
    return normalized_nickname

"""
nickname = "kožušček José  @%$ García 12421 \n icwbb kožušček 21321 $*#^@* ä, ë, ï, ö, ü, ÿ, Ä, Ë, Ï, Ö, Ü, Ÿ, œ, Œ, æ, Æ, ø, Ø, ¿, ¡, ß, å, Å"


vad = unidecode(nickname)
normalized_nickname = normalize_nickname(vad)
print(normalized_nickname)

vad = unidecode('kožušček 21321 $*#^@* ä, ë, ï, ö, ü, ÿ, Ä, Ë, Ï, Ö, Ü, Ÿ, œ, Œ, æ, Æ, ø, Ø, ¿, ¡, ß, å, Å')
"""