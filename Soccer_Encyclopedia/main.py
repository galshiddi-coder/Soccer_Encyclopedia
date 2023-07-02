# Names: Ghaida Alshiddi & Bushra Rahman
# Class: CS 4395.001
# Assignment: Web Crawler
# Due date: 3/11/23

import pathlib
from bs4 import BeautifulSoup
# import urllib
# from urllib import request
import requests
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import pickle


# This function takes a URL as its parameter
# and returns a list of 15 relevant URLs.
def web_crawler(starter_url):
    r = requests.get(starter_url)
    data = r.text
    soup = BeautifulSoup(data, features='html.parser')
    url_list = [starter_url]
    counter = 0
    # Crawl for urls and append to url_list
    for link in soup.find_all('a'):
        link_str = str(link.get('href'))
        # print(link_str)
        if counter > 13:
            break
        if link_str.startswith('http') and 'google' not in link_str:
            url_list.append(link_str)
            counter += 1
            # print(counter)

    return url_list
# End of web_crawler()


# This function takes a list of URLs as its parameter,
# scrapes text off each webpage, and outputs each webpage's text to its own output file.
def text_scraper(url_list):
    counter = 1
    for url in url_list:
        with open(pathlib.Path.cwd().joinpath('ScrapedText_%d.txt' % counter), 'w', encoding='utf-8') as f:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            text = soup.get_text()
            f.write(text)
        counter += 1
# End of text_scraper()


# This function reads in an input file of scraped text,
# cleans it up, and writes the new text to a new output file.
def text_cleaner(input_filename):
    with open(pathlib.Path.cwd().joinpath(input_filename), 'r', encoding='utf-8') as f:
        # Replace tabs/newlines/carriage returns in the file lines w/ spaces
        text = re.sub(r'[\t\n\r]', ' ', ''.join(f.readlines()))

    # Tokenize sentences
    sentences = sent_tokenize(text)

    # Create output file
    num = int(re.sub('[^0-9]', '', input_filename))
    with open(pathlib.Path.cwd().joinpath('CleanedText_%d.txt' % num), 'w', encoding='utf-8') as f:
        # Write cleaned text to output file
        for sentence in sentences:
            f.write(sentence)
            f.write('\n')
# End of text_cleaner()


# This function reads in an input file of cleaned text
# and extracts the 3 most important terms using the importance measure of term frequency (tf).
def important_terms(input_filename):
    with open(pathlib.Path.cwd().joinpath(input_filename), 'r', encoding='utf-8') as f:
        # Read in raw text as a string
        raw_text = ''.join(f.readlines())

    # Get list of tokens: lowercase everything & remove stopwords and punctuation
    tokens = [tok.lower() for tok in word_tokenize(raw_text)]
    tokens_list = [tok2 for tok2 in tokens if tok2.isalpha() and tok2 not in stopwords.words('english')]

    # Dictionary for tf, where each {key:value} = {term:tf}
    tf_dict = {}
    # Get counts of terms
    for tok in tokens_list:
        # Accumulate token count if token is already a key in tf_dict
        if tok in tf_dict:
            tf_dict[tok] += 1
        # Initialize token count to 1 if token is not already a key in tf_dict
        else:
            tf_dict[tok] = 1
    # Calculate tf for each term: count(term)/total # of tokens in document
    for tok in tf_dict.keys():
        tf_dict[tok] = tf_dict[tok] / len(tokens_list)

    # Lambda expression used to sort tf_dict by tf (i.e. by value, not key).
    # Return type is not a dict but a list due to sorted(). Each list element is a {key:value} tuple.
    sorted_tf_list = sorted(tf_dict.items(), key=lambda x: x[1], reverse=True)

    # Use list slicing to return the top 3 terms and their tf values
    return sorted_tf_list[0:3]
# End of important_terms()


# This function takes a term and filename as input
# and returns a list of sentences containing the term.
def knowledge_base(term, input_filename):
    with open(pathlib.Path.cwd().joinpath(input_filename), 'r', encoding='utf-8') as f:
        # Read in raw text as a string
        text = ''.join(f.readlines())
    # Tokenize sentences
    sentences = sent_tokenize(text)
    # Create list of sentences containing the term
    sentences_with_term = [sentence for sentence in sentences if term in sentence]
    return sentences_with_term
# End of knowledge_base()


# main()
if __name__ == '__main__':
    start = 'https://www.encyclopedia.com/sports/sports-fitness-recreation-and-leisure-magazines/fifa-world-cup-soccer'

    # Call web_crawler() to create URLs list
    urls = web_crawler(start)

    # Print URLs list
    index = 1
    for url in urls:
        print(index, url)
        index += 1

    # Call text_scraper() to scrape text off each URL page into files
    text_scraper(urls)

    print('\nThe top 45 terms are:')

    # Call text_cleaner() and important_terms() on each file
    for i in range(len(urls)):
        filename = 'ScrapedText_%d.txt' % (i+1)
        text_cleaner(filename)
        filename = 'CleanedText_%d.txt' % (i+1)
        # Call important_term() on 15 files, for 15*3=45 total important terms
        print(important_terms(filename))

    # Manually pick top 10 terms
    top10_terms_list = ['world', 'cup', 'soccer', 'rugby', 'basketball', 'game', 'players', 'cricket', 'football', 'sports']
    print('\nThe top 10 terms chosen are:')
    counter = 0
    for term in top10_terms_list:
        print((counter + 1), term)
        counter += 1

    # The knowledge base is a dict where {key:value} = {term:list of sentences containing term}
    knowledge_base_dict = {}
    for term in top10_terms_list:
        # Initialize terms as the dict keys
        knowledge_base_dict[term] = []

    for i in range(len(top10_terms_list)):
        # Initialize list of sentences for term
        sentences_list = []
        for j in range(len(urls)):
            filename = 'CleanedText_%d.txt' % (j + 1)
            list_to_add = knowledge_base(top10_terms_list[i], filename)
            sentences_list.extend(list_to_add)
        # Store finalized list of sentences as the dict values
        knowledge_base_dict[top10_terms_list[i]] = sentences_list

    # Pickle knowledge_base_dict
    file = open('knowledge_base.pickle', 'wb')
    pickle.dump(knowledge_base_dict, file)
    file.close()

    # Read the pickle back in
    knowledge_base_in = pickle.load(open('knowledge_base.pickle', 'rb'))

    # Print knowledge base
    print('\n\nKnowledge Base: ')
    print(knowledge_base_in)

# End of main()
