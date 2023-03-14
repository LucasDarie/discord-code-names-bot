import io
import unidecode

def write_list_file(wrapper:io.TextIOWrapper, max_word:int, max_length_word:int, guild_id:str):
    """write words in a file

    Args:
        wrapper (io.TextIOWrapper): text wrapper buffer
        max_word (int): Number max of word allowed to add
        max_length_word (int): max length of a word, if the length is greater the word will not be added
        guild_id (str): the guild id of the word list
    """
    l = wrapper.readlines()
    with open(f"words/servers/{guild_id}_word_list.txt", "w") as f:
        
        i = 0
        words_added:list[str] = []
        while i < len(l) and len(words_added) < max_word:
            word = unidecode.unidecode(l[i].strip()).capitalize()
            i += 1
            if (all(x.isalpha() or x == "-" or x.isnumeric() for x in word[:-1]) 
                    and len(word) <= max_length_word 
                    and word not in words_added
                    and word != ""):
                words_added.append(word)
                f.write(word+"\n")
        # exit : i >= len(l) or len(words_added) >= max_word

def read_list_file(path:str) -> list[str]:
    """read a file to create a list of word

    Args:
        path (str): the path of the file

    Returns:
        list[str]: the list of word
    """
    with open(path, "r") as f:
        return [unidecode.unidecode(word.strip()).upper() for word in f.readlines() if word != "\n"]


