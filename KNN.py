"""
COMP 614
Homework 5: Bag of Words
"""

import math
import numpy
import re
import string

import comp614_module5


def get_title_and_text(filename):
    """
    Given a the name of an XML file, extracts and returns the strings contained 
    between the <title></title> and <text></text> tags.
    """
    with open(filename, 'r', encoding='utf-8') as xml:
        lines = xml.readlines()
        title = ""
        in_text = False
        text = ""
        start_text = re.compile('<text.*?>')

        for line in lines:

            if line.find("<title>") != -1:
                start = line.find("<title>")+7
                end = line.rfind("</title>")
                title = line[start:end]

            elif start_text.search(line) is not None and line.find("</text>") != -1:
                match = start_text.search(line)
                start = match.end()
                end = line.rfind("</text>")
                text += line[start:end]

            elif start_text.search(line) is not None:
                match = start_text.search(line)
                start = match.end()
                text += line[start:]
                in_text = True

            elif line.find("</text>") != -1:
                end = line.rfind("</text>")
                text += line[:end]
                in_text = False

            elif in_text:
                text += line

    text = re.sub(r'\n', ' ', text)

    return title, text


def get_words(text):
    """
    Given the full text of an XML file, filters out the non-body text (text that
    is contained within {{}}, [[]], [], <>, etc.) and punctuation and returns a 
    list of the remaining words, each of which should be converted to lowercase.
    """

    word_list = []
    punctuation_to_remove = "[" + string.punctuation + "](?![st]\\s)"

    expressions = ['{{.*?}}', '\\{\\|.*?\\|}', '\\[\\[.*?]]', '\\[.*?]',
                   '<.*?>', '&lt;.*?&gt;', 'File:', punctuation_to_remove]

    for expression in expressions:
        case = re.compile(expression, re.DOTALL)
        if case.search(text) is not None:
            text = case.sub(" ", text)

    words = text.split()

    for word in words:
        new_word = word.lower()
        word_list.append(new_word)

    return word_list


def count_words(words):
    """
    Given a list of words, returns the total number of words as well as a 
    dictionary mapping each unique word to its frequency of occurrence.
    """
    frequency = {}
    total = 0

    for word in words:

        total += 1

        if word not in frequency:
            frequency[word] = 1
        else:
            frequency[word] += 1

    return total, frequency


def count_all_words(filenames):
    """
    Given a list of filenames, returns three things. First, a list of the titles,
    where the i-th title corresponds to the i-th input filename. Second, a
    dictionary mapping each filename to an inner dictionary mapping each unique
    word in that file to its relative frequency of occurrence. Last, a dictionary 
    mapping each unique word --- including all words found across all files --- 
    to its total frequency of occurrence across all of the input files.
    """

    all_titles = []
    title_to_counter = {}
    total_count = {}

    for file in filenames:

        title, text = get_title_and_text(file)
        word_list = get_words(text)
        total, frequency = count_words(word_list)

        all_titles.append(title)
        if title not in title_to_counter:
            title_to_counter[title] = {}

        for key, value in frequency.items():

            if key not in total_count:
                total_count[key] = value
            else:
                total_count[key] += value

            title_to_counter[title][key] = value/total

    return all_titles, title_to_counter, total_count


def encode_word_counts(all_titles, title_to_counter, total_counts, num_words):
    """
    Given two dictionaries in the format output by count_all_words and an integer
    num_words representing the number of top words to encode, finds the top 
    num_words words in total_counts and builds a matrix where the element in 
    position (i, j) is the relative frequency of occurrence of the j-th most 
    common overall word in the i-th article (i.e., the article corresponding to 
    the i-th title in titles).
    """

    sorted_words = sorted(total_counts.items(), key=lambda tup: (-1 * tup[1], tup[0]))

    if len(sorted_words) < num_words:
        num_words = len(sorted_words)

    wanted_words = sorted_words[:num_words]
    list_lists = []


    for title in all_titles:

        temp_list = []

        for word in wanted_words:

            if word[0] in title_to_counter[title]:
                temp_list.append(title_to_counter[title][word[0]])
            else:
                temp_list.append(0)

        list_lists.append(temp_list)

    return numpy.array(list_lists)


def nearest_neighbors(matrix, all_titles, title, num_nbrs):
    """
    Given a matrix, a list of all titles whose data is encoded in the matrix, such
    that the i-th title corresponds to the i-th row, a single title whose data is
    encoded in the matrix, and the desired number of neighbors to be found, finds 
    and returns the closest neighbors to the article with the given title.
    """

    if num_nbrs > matrix.shape[0]:
        num_nbrs = matrix.shape[0]

    distances_list = []
    title_index = all_titles.index(title)
    neighbor_list = []

    for xindex in range(matrix.shape[0]):
        temp_list = []

        if xindex == title_index:
            distances_list.append(float('inf'))
            continue

        for yindex in range(matrix.shape[1]):
            temp_list.append((matrix[title_index][yindex] - matrix[xindex][yindex]) ** 2)

        distances_list.append(sum(temp_list) ** 0.5)

    sorted_distances = sorted(distances_list)

    for element in sorted_distances:
        if element == float('inf'):
            continue
        index = distances_list.index(element)
        neighbor_list.append(all_titles[index])

    return neighbor_list[:num_nbrs]

def run():
    """
    Encodes the wikipedia dataset into a matrix, prompts the user to choose an
    article, and then runs the knn algorithm to find the 5 nearest neighbors
    of the chosen article.
    """
    # Encode the wikipedia dataset in a matrix
    filenames = comp614_module5.ALL_FILES
    all_titles, title_to_counter, total_counts = count_all_words(filenames)
    mat = encode_word_counts(all_titles, title_to_counter, total_counts, 20000)

    # Print all articles
    print("Enter the integer corresponding to the article whose nearest" +
          " neighbors you would like to find. Your options are:")
    for idx in range(len(all_titles)):
        print("\t" + str(idx) + ". " + all_titles[idx])

    # Prompt the user to choose an article
    while True:
        choice = input("Enter your choice here: ")
        try:
            choice = int(choice)
            break
        except ValueError:
            print("Error: you must enter an integer between 0 and " +
                  str(len(all_titles) - 1) + ", inclusive.")

    # Compute and print the results
    nbrs = nearest_neighbors(mat, all_titles, all_titles[choice], 5)
    print("\nThe 5 nearest neighbors of " + all_titles[choice] + " are:")
    for nbr in nbrs:
        print("\t" + nbr)


# Leave the following line commented when you submit your code to OwlTest/CanvasTest,
# but uncomment it to perform the analysis for the discussion questions.
run()