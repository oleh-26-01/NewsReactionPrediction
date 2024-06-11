import random
import string
import re
from math import log10

import humanize
from keras.utils import pad_sequences
from fuzzywuzzy import fuzz


def object_size(obj): return humanize.naturalsize(obj.__sizeof__())


def clean_text(text):
    cleaned_text = re.sub(f"[^\w'’‘-]+", " ", text.lower())
    return cleaned_text


def replace_numbers(text, depth=10):
    words = text.split(" ")
    for i in range(len(words)):
        if words[i].isdigit():
            num = int(words[i])
            if num <= 0:
                words[i] = f"n0n"
            else:
                power = int(log10(num))
                if power < depth:
                    words[i] = f"n{power}n"
                else:
                    words[i] = "nxn"
    return " ".join(words)


def split_data(articles, answers, train_split=0.9):
    data = list(zip(articles, answers))
    random.shuffle(data)
    train_data = data[:int(len(data) * train_split)]
    validation_data = data[int(len(data) * train_split):]

    train_articles = [row[0] for row in train_data]
    train_answers = [row[1] for row in train_data]
    validation_articles = [row[0] for row in validation_data]
    validation_answers = [row[1] for row in validation_data]
    return (train_articles, train_answers), (validation_articles, validation_answers)


def seq_pad_and_trunc(articles, tokenizer, padding, truncating, max_length):
    sequences = tokenizer.texts_to_sequences(articles)
    padded = pad_sequences(sequences, padding=padding, truncating=truncating, maxlen=max_length)
    return padded


def generate_test_string(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    test_string = ''.join(random.choice(characters) for _ in range(length))
    return test_string


def split_by_words_and_rest(text, simple: bool = False) -> [list, list]:
    form = "\w+" if simple else "[\w’'‘`]+"
    print(f"using form: {form}")
    matches = re.findall(rf'\b({form})(\W*)', text.lower())
    words, rest = zip(*matches)

    return words, rest


def levenshtein_distance(word1, word2):
    m, n = len(word1), len(word2)

    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],  # видалення
                                   dp[i][j - 1],  # вставка
                                   dp[i - 1][j - 1])  # заміна

    return dp[m][n]


def word_similarity(word1, word2):
    distance = levenshtein_distance(word1, word2)
    max_len = max(len(word1), len(word2))
    similarity = 1 - distance / max_len
    return similarity


def word_similarity_fuzzy(word1, word2):
    similarity = fuzz.ratio(word1, word2) / 100
    return similarity


def unique(array) -> dict:
    unique_dict = {}
    for item in array:
        if item in unique_dict:
            unique_dict[item] += 1
        else:
            unique_dict[item] = 1
    # sort by value
    unique_dict = {k: v for k, v in sorted(unique_dict.items(), key=lambda item: item[1], reverse=True)}
    return unique_dict


if __name__ == "__main__":

    # Приклад використання:
    word1 = "україна"
    word2 = "українка"
    similarity = word_similarity(word1, word2)
    print(f"Схожість між '{word1}' і '{word2}': {similarity}")