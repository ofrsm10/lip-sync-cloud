import unicodedata
import os
from collections import Counter
import re
import requests

FORBIDDEN_WORDS = ["הרג", "יהרוג", "ירצח", "רצח", "פשע", "סקס", "זנות", "גנב", "פושע", "רוצח", "נרצחה", "נרצח", "נהרגה",
                   "נהרג", "מתה", "מת", "נפטרה", "נפטר"]


def get_rows(start, end):
    url = "https://datasets-server.huggingface.co/rows"
    dataset = "imvladikon/hebrew_speech_coursera"
    config = "imvladikon--hebrew_speech_coursera"
    split = "train"
    limit = end - start + 1

    params = {
        "dataset": dataset,
        "config": config,
        "split": split,
        "offset": start,
        "limit": limit
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        features = response.json()
        rows = features['rows']
        return rows
    else:
        print("Error occurred while fetching rows:", response.status_code)
        return None


def read_lines_and_write_sentences(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if not line.startswith("# "):
            sentence = line.split(': ')[1].strip()
            write_sentence_to_file(sentence, "/Users/ofersimchovitch/PycharmProjects/lipSyncBeta/Sentences")


def create_txt_from_data(directory):
    for start_idx in range(0, 20000, 100):
        end_idx = start_idx + 100
        print(f'The end index is: {end_idx}')
        rows = get_rows(start_idx, end_idx)
        if rows is not None:
            # Process the retrieved rows
            for row in rows:
                sentence = row['row']['sentence']
                write_sentence_to_file(sentence, directory)


def write_sentence_to_file(sentence, directory):
    number_of_words = len(sentence.split())
    filename = f'censored_{number_of_words}.txt'
    filepath = os.path.join(directory, filename)

    with open(filepath, 'a') as file:
        file.write(sentence + '\n')


def check_english(string):
    english_chars = all(
        unicodedata.category(char).startswith('L') and
        unicodedata.name(char).startswith('LATIN')
        for char in string
    )
    return english_chars and len(string) > 1


def check_number(string):
    try:
        number = float(string)
        if number > 20:
            return True
        else:
            return False
    except ValueError:
        return False


def remove_duplicates_in_files(directory):
    # Get a list of all text files in the directory
    file_list = [filename for filename in os.listdir(directory) if filename.endswith('.txt')]

    for filename in file_list:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Remove duplicate lines
        unique_lines = list(set(lines))

        # Write the unique lines back to the file
        with open(file_path, 'w') as file:
            file.writelines(unique_lines)


def filter_lines_in_files(directory, forbidden_words=FORBIDDEN_WORDS):
    # Get a list of all text files in the directory
    file_list = [filename for filename in os.listdir(directory) if filename.endswith('.txt')]

    for filename in file_list:
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                lines = file.readlines()

            # Create a list to store the filtered lines
            filtered_lines = []
            unfiltered_lines = []

            for line in lines:
                for word in line.strip().split(' '):
                    if len(word) >= 9 or check_number(word) or check_english(word) or word.lower() in forbidden_words:
                        filtered_lines.append(line)
                    else:
                        write_sentence_to_file(line, directory)

            # Write the filtered lines to the "filtered.txt" file
            filtered_file_path = os.path.join(directory, "filtered.txt")
            with open(filtered_file_path, 'a') as filtered_file:
                filtered_file.writelines(filtered_lines)


import os
from collections import Counter
import re


def analyze_files(directory):
    # Get a list of all text files in the directory
    file_list = [filename for filename in os.listdir(directory) if filename.endswith('.txt')]

    # Initialize counters
    word_counter = Counter()

    # Process each file and update word counts
    for filename in file_list:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as file:
            text = file.read()

        # Tokenize the text into words
        words = re.findall(r'\b\w+\b', text.lower())

        # Update word counts
        word_counter.update(words)

    # Determine words appearing only once in the entire directory
    words_appearing_once = {word for word, count in word_counter.items() if count == 1}

    # Remove lines containing words appearing only once
    for filename in file_list:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Filter lines and keep only those without words appearing once
        filtered_lines = [line for line in lines if
                          not any(word in words_appearing_once for word in re.findall(r'\b\w+\b', line.lower()))]

        # Write the filtered lines back to the file
        with open(file_path, 'w') as file:
            file.writelines(filtered_lines)

        # Append the unfiltered lines to "filtered.txt"
        filtered_file_path = os.path.join(directory, 'filtered.txt')
        with open(filtered_file_path, 'a') as filtered_file:
            filtered_file.writelines(lines)


def common_word(directory):
    # Get a list of all text files in the directory
    file_list = [filename for filename in os.listdir(directory) if filename.endswith('.txt')]

    # Initialize counters
    unique_words = set()
    word_counter = Counter()

    # Process each file
    for filename in file_list:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as file:
            text = file.read()

        # Tokenize the text into words
        words = re.findall(r'\b\w+\b', text.lower())

        # Update unique word set
        unique_words.update(words)

        # Update word counts
        word_counter.update(words)

    # Print number of unique words
    num_unique_words = len(unique_words)
    print(f"Number of unique words: {num_unique_words}")

    # Print counts of 50 most common words
    most_common_words = word_counter.most_common(50)
    print("Counts of the 50 most common words:")
    for word, count in most_common_words:
        print(f"{word}: {count}")

    # Print counts of 50 least common words
    least_common_words = word_counter.most_common()[-50:]
    print("Counts of the 50 least common words:")
    for word, count in least_common_words:
        print(f"{word}: {count}")


dir = "/Users/ofersimchovitch/PycharmProjects/lipSyncBeta/Sentences"
# create_txt_from_data(directory)
# read_lines_and_write_sentences("/Users/ofersimchovitch/PycharmProjects/lipSyncBeta/Sentences/sentences.txt")
# filter_lines_in_files(directory)
# remove_duplicates_in_files(directory)
# analyze_files(directory)
common_word(dir)
