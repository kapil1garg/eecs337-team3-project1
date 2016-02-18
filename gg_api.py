import json
import re
import numpy
import sys
import nltk
import os.path
import collections


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

    re_Best_Drama = re.compile('(best\s[a-zA-z\s\(-]*?drama)', re.IGNORECASE)
    re_Best_Musical = re.compile('(best\s[a-zA-z\s\(-]*?musical)', re.IGNORECASE)
    re_Best_Comedy = re.compile('(best\s[a-zA-z\s\(-]*?comedy)', re.IGNORECASE)

    re_Best_MotionPicture = re.compile('(best\s[a-zA-Z\s\(-]*?motion picture)', re.IGNORECASE)
    re_Best_Television = re.compile('(best\s[a-zA-Z\s\(-]*?television)', re.IGNORECASE)
    re_Best_Film = re.compile('(best\s[a-zA-Z\s\(-]*?film)', re.IGNORECASE)

    # No need for break words because our regexs will not capture these
    #break_words = [' http', ' #', '.', ',', '!', '?','\\', ':', ';', '"', "'"]

    # stop words to be removed from all tweets
    stop_words = ['.', ',', '!', '(', '-', ' on ', ' the ', ' male ', ' female ', ' in ', ' a ', ' is ', ' for ', ' at ', ' golden ', ' globes ', ' by ', ' an ', ' category ', ' and ', ' show ']

    

    

    if not (os.path.isfile("./clean_tweets%s.json" % year)):
        raise Exception('Tweets for %s have not been preprocessed')

    with open("./clean_tweets%s.json" % year) as clean_file:
        tweets = json.load(clean_file)

    # switch words
    # film, movie, picture -> motion picture (not for things that end with film)
    # tv -> television
    # television -> television series (not for things that end with television)
    

#    awards = {}
    awards = []
    awards_2 = []
    awards_final = []
    for u_tweet in tweets:
        
        if 'best' in u_tweet:

            tweet = u_tweet
            for stop_word in stop_words:

                if stop_word in tweet:

                    tweet = ' '.join([a.strip() for a in tweet.split(stop_word)])

            drama_match = re.search(re_Best_Drama, tweet)
            musical_match = re.search(re_Best_Musical, tweet)
            comedy_match = re.search(re_Best_Comedy, tweet)

            if drama_match or musical_match or comedy_match:
                
                if drama_match:

                    for match_str in drama_match.groups():

                        l_dramaMatch = str(match_str.lower())

                        if ' film ' in l_dramaMatch:

                            l_dramaMatch = ' motion picture '.join([a.strip() for a in l_dramaMatch.split(' film ')])

                        awards.append(' - drama'.join([a.strip() for a in l_dramaMatch.split('drama')]))
                            
                if musical_match and not comedy_match:

                    for match_str in musical_match.groups():

                        l_musMatch = str(match_str.lower())

                        if ' film ' in l_musMatch:

                            l_musMatch = ' motion picture '.join([a.strip() for a in l_musMatch.split(' film ')])

                        if 'musical' in l_musMatch and 'comedy' not in l_musMatch:

                            l_musMatch = ' - comedy or musical '.join([a.strip() for a in l_musMatch.split('musical')])

                        elif 'musical or comedy' in l_musMatch:

                            l_musMatch = ' - comedy or musical '.join([a.strip() for a in l_musMatch.split('musical or comedy')])

                        l_musMatch = l_musMatch.strip()
                        awards.append(l_musMatch)
                
                if comedy_match:

                    for match_str in comedy_match.groups():

                        l_comMatch = str(match_str.lower())

                        if ' film ' in l_comMatch:

                            l_comMatch = ' motion picture '.join([a.strip() for a in l_comMatch.split(' film ')])
                        
                        if 'comedy' in l_comMatch and 'musical' not in l_comMatch:

                            l_comMatch = ' - comedy or musical '.join([a.strip() for a in l_comMatch.split('comedy')])

                        elif 'musical or comedy' in l_comMatch:

                            l_comMatch = ' - comedy or musical '.join([a.strip() for a in l_comMatch.split('musical or comedy')])

                        awards.append(l_comMatch)

            else:

                mp_match = re.search(re_Best_MotionPicture, tweet)
                tv_match = re.search(re_Best_Television, tweet)
                film_match = re.search(re_Best_Film, tweet)

                if mp_match:

                    for match_str in mp_match.groups():

                        l_mpMatch = str(match_str.lower())

                        awards_2.append(l_mpMatch)

                if tv_match:

                    for match_str in tv_match.groups():

                        l_tvMatch = str(match_str.lower())

                        awards_2.append(l_tvMatch)

                if film_match:

                    for match_str in film_match.groups():

                        l_filmMatch = str(match_str.lower())

                        awards_2.append(l_filmMatch)
                

 #   remWords = ['(', 'in a', ' in ']
 #   awards_final = []
    for award in awards:

        award_final = award

        if 'movie' in award_final:

            award_final = ' motion picture '.join([a.strip() for a in award_final.split('movie')])

        if 'picture' in award_final and 'motion' not in award_final:

            award_final = ' motion picture '.join([a.strip() for a in award_final.split('picture')])

        if ' tv' in award_final:

            award_final = ' television '.join([a.strip() for a in award_final.split('tv')])

        if 'television' in award_final and 'series' not in award_final:

            award_final = ' television series '.join([a.strip() for a in award_final.split('television')])

        award_final = award_final.strip()
        if award_final not in ['best - drama', 'best - comedy or musical']:

            awards_final.append(award_final)

    for award in awards_2:

        award_final = award

        if 'movie' in award_final:

            award_final = ' motion picture '.join([a.strip() for a in award_final.split('movie')])
                
        if 'picture' in award_final and 'motion' not in award_final:

            award_final = ' motion picture '.join([a.strip() for a in award_final.split('picture')])

        if ' tv' in award_final:

            award_final = ' television '.join([a.strip() for a in award_final.split('tv')])

        award_final = award_final.strip()

        if len(award_final) > 14 and award_final[-14:] == 'motion picture':

            award_final = award_final[:-14] + '- ' + award_final[-14:]
            
        if award_final not in ['best film', 'best - motion picture', 'best television']:

            awards_final.append(award_final)

            

    awards_fd = nltk.FreqDist(awards_final)
       
    return [award_fd for award_fd in awards_fd.most_common(30)]

def clean_awards(awards):
    '''Takes an unfiltered dictionary of awards that we grabbed from the tweets.
    Returns a dictionary with cleaned awards list'''

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
    
    file_path = './gg2013.json'
    
    tweets = get_tweets(file_path)
    my_clean_tweets = clean_tweets(tweets)
    
    #print len(my_clean_tweets)
    
    print "Pre-ceremony processing complete."
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    
    #pre_ceremony()

    award_tweets = get_awards(2013)

    print "len(award_tweets): %s" % len(award_tweets)
    print award_tweets
    return

def get_tweets(path):
    
    with open(path) as json_file:
        raw_tweets = json.load(json_file)
    
    tweets = [tweet["text"] for tweet in raw_tweets]
    
    return tweets

def clean_tweets(tweets):

    path = './clean_tweets2013.json'
    
    if not (os.path.isfile(path)):
        
        re_retweet = re.compile('rt', re.IGNORECASE)
        
        clean_tweets = []
        for tweet in tweets:
            
            if not (re.match(re_retweet, tweet)):
                    
                clean_tweets.append(tweet)
        
        with open(path, 'w') as outfile:
            
            json.dump(clean_tweets, outfile)

    else:
            
        with open(path, 'r') as datafile:
            clean_tweets = json.load(datafile)
    
    return clean_tweets
    

if __name__ == '__main__':
    main()
