# -*- coding: utf-8 -*-
import unicodedata
import re
import nltk

tokenizer = nltk.tokenize.TweetTokenizer()

def read_json(fname):
    with open(fname, encoding="utf-8") as f:
        json_posts = json.load(f)

    print("Read in %d posts from %s" % (len(json_posts), fname))
    return json_posts

# conversion based on https://stackoverflow.com/questions/10294032/python-replace-typographical-quotes-dashes-etc-with-their-ascii-counterparts
def _get_unicode_character_name(char):
    try:
        return unicodedata.name(char)
    except ValueError:
        return None

def _get_all_unicode_non_ascii_characters():
    # Generate all Unicode characters with their names
    all_unicode_characters = []
    for n in range(128, 0x10ffff):  # Unicode planes 0-16
        char = chr(n)
        name = _get_unicode_character_name(char)
        if name:
            all_unicode_characters.append((char, name))
    return all_unicode_characters

def _build_unicode_to_ascii_normalisation_dict():
    unicode_to_ascii_normalisazion_dict = {}
    all_unicode_characters = _get_all_unicode_non_ascii_characters()
    # quote = double or quotation mark or angle quotation mark,
    # single quotation marks are sometimes also used in place of asterics, so replace them by apostrophe/single quote
    quote_chars = [char for char, name in all_unicode_characters if
                   'QUOTATION MARK' in name and (not 'SINGLE' in name or 'ANGLE' in name)]
    ascii_quote_char = u'"'

    # apostrophe = apostrophe characters or single quotation mark (if not standard ascii quotation mark)
    apostrophe_chars = [char for char, name in all_unicode_characters if
                        'APOSTROPHE' in name or ('QUOTATION MARK' in name and 'SINGLE' in name)]
    ascii_apostrophe_char = u"'"

    hyphen_chars = [char for char, name in all_unicode_characters if 'HYPHEN' in name]
    ascii_hyphen_char = u"-"
    dash_chars = [char for char, name in all_unicode_characters if 'DASH' in name and 'DASHED' not in name]
    ascii_dash_char = ascii_hyphen_char
    space_chars = [char for char, name in all_unicode_characters if 'SPACE' in name]
    ascii_space_char = u" "
    for quote_char in quote_chars:
        unicode_to_ascii_normalisazion_dict[ord(quote_char)] = ord(ascii_quote_char)
    for apostrophe_char in apostrophe_chars:
        unicode_to_ascii_normalisazion_dict[ord(apostrophe_char)] = ord(ascii_apostrophe_char)
    for hyphen_char in hyphen_chars:
        unicode_to_ascii_normalisazion_dict[ord(hyphen_char)] = ord(ascii_hyphen_char)
    for dash_char in dash_chars:
        unicode_to_ascii_normalisazion_dict[ord(dash_char)] = ord(ascii_dash_char)
    for space_char in space_chars:
        unicode_to_ascii_normalisazion_dict[ord(space_char)] = ord(ascii_space_char)

    return unicode_to_ascii_normalisazion_dict


UNICODE_TO_ASCII_NORMALISATION_DICT = _build_unicode_to_ascii_normalisation_dict()


def normalise_unicode_to_ascii(text):
    text = str(text)
    # print("Original text\n%s" %text)
    text = text.translate(UNICODE_TO_ASCII_NORMALISATION_DICT)
    # print("ASCII text\n%s" %text)

    return text

def remove_reddit_quotes(text, remove_in_line_quotes=False):
    """
    removes all lines starting with &gt; (displayed as | in reddit) that are quotes of another user
    :param text:
    :param remove_in_line_quotes: if True, additionally removes all quotes in double quotes (And then he said "I love you")
    :return:
    """
    user_lines = []
    quoted_text = re.compile(r"\".+\"")
    for line in text.split("\n"):
        if line and not line.startswith('&gt;'):
            if remove_in_line_quotes:
                line = quoted_text.sub("", line)
            user_lines.append(line)
    return "\n".join(user_lines)

def tokenize(text):
    return " ".join(tokenizer.tokenize(text))
