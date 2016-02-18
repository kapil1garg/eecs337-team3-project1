import sys
import json
import re
import string
import copy
import time
import multiprocessing as mp
import nltk


def load_data(year):
    file_string = 'gg' + str(year) + '.json'
    tweets = {}
    with open(file_string, 'r') as f:
        tweets = json.load(f)
    return tweets

def lower_case_tweet(tweet):
    lower_tweet = tweet
    lower_tweet['text'] = lower_tweet['text'].lower()
    return lower_tweet

def remove_stop_words_tweet(stop_words, tweet):
    stop_words_removed_tweet = tweet
    tweet_words = tweet['text'].split()
    stop_words_removed_tweet['text'] = ' '.join([w for w in tweet_words if w not in stop_words])
    return stop_words_removed_tweet

def lower_case_all(tweets):
    tweets = copy.deepcopy(tweets)
    return [lower_case_tweet(tweet) for tweet in tweets]

def remove_stop_words_all(tweets):
    tweets = copy.deepcopy(tweets)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    return [remove_stop_words_tweet(stop_words, tweet) for tweet in tweets]

def lower_case_mp(tweets):
    tweets = copy.deepcopy(tweets)
    pool = mp.Pool(processes=8)
    return pool.map(lower_case_tweet, tweets)

def remove_stop_words_mp(tweets):
    tweets = copy.deepcopy(tweets)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    pool = mp.Pool(processes=2)
    return [pool.apply(remove_stop_words_tweet, args=(stop_words, tweet)) for tweet in tweets]

OFFICIAL_AWARDS = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    return awards

def get_nominees(year):
    '''Nominees is a list of dictionaries with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    return nominees

def get_winners(year):
    '''Winners is a list of dictionaries with the hard coded award
    names as keys, and each entry a list containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    return winners

def get_presenters(year):
    '''Presenters is a list of dictionaries with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print "Pre-ceremony processing complete."
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    tweets = load_data(2013)
    print 'Testing serial code'
    start_time = time.time()
    print tweets[2]
    print lower_case_all(tweets)[2]
    print remove_stop_words_all(tweets)[2]
    end_time = time.time()
    print 'Execution time for serial was ' + str(end_time - start_time) + '\n'

    # print 'Testing parallel code'
    # start_time = time.time()
    # print tweets[2]
    # print lower_case_mp(tweets)[2]
    # print remove_stop_words_mp(tweets)[2]
    # end_time = time.time()
    # print 'Execution time for parallel was ' + str(end_time - start_time) + '\n'
    # return

if __name__ == '__main__':
    mp.freeze_support()
    main()
