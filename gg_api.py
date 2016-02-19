import json
import re
import numpy
import sys
import nltk
import os.path
import collections
import pickle


OFFICIAL_AWARDS = ['cecil b. demille award',
                   'best motion picture - drama',
                   'best performance by an actress in a motion picture - drama',
                   'best performance by an actor in a motion picture - drama',
                   'best motion picture - comedy or musical',
                   'best performance by an actress in a motion picture - comedy or musical',
                   'best performance by an actor in a motion picture - comedy or musical',
                   'best animated feature film',
                   'best foreign language film',
                   'best performance by an actress in a supporting role in a motion picture',
                   'best performance by an actor in a supporting role in a motion picture',
                   'best director - motion picture',
                   'best screenplay - motion picture',
                   'best original score - motion picture',
                   'best original song - motion picture',
                   'best television series - drama',
                   'best performance by an actress in a television series - drama',
                   'best performance by an actor in a television series - drama',
                   'best television series - comedy or musical',
                   'best performance by an actress in a television series - comedy or musical',
                   'best performance by an actor in a television series - comedy or musical',
                   'best mini-series or motion picture made for television',
                   'best performance by an actress in a mini-series or motion picture made for television',
                   'best performance by an actor in a mini-series or motion picture made for television',
                   'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television',
                   'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']

# NOAH using this to test out my get presenters function. Assuming we can get all of the correct nominees
NOMINEES_2013 = {'cecil b. demille award': [],
                   'best motion picture - drama': ['Argo', 'Django Unchained', 'Life of Pi', 'Lincoln', 'Zero Dark Thirty'] ,
                   'best performance by an actress in a motion picture - drama' : ['Jessica Chastain', 'Marion Cotillard', 'Helen Mirren', 'Naomi Watts', 'Rachel Weisz'],
                   'best performance by an actor in a motion picture - drama' : ['Daniel Day-Lewis', 'Richard Gere', 'John Hawkes', 'Joaquin Phoenix', 'Denzel Washington'],
                   'best motion picture - comedy or musical' : ['Les Miserables', 'The Best Exotic Marigold Hotel', 'Moonrise Kingdom', 'Salmon Fishing in the Yemen', 'Silver Linings Playbook'],
                   'best performance by an actress in a motion picture - comedy or musical' : ['Jennifer Lawrence', 'Emily Blunt', 'Judi Dench', 'Maggie Smith', 'Meryl Streep'],
                   'best performance by an actor in a motion picture - comedy or musical' : ['Hugh Jackman', 'Jack Black', 'Bradley Cooper', 'Ewan McGregor', 'Bill Murray'],
                   'best animated feature film' : ['Brave', 'Frankenweenie', 'Hotel Transylvania', 'Rise of the Guardians', 'Wreck-It Ralph'],
                   'best foreign language film' : ['Amour', 'A Royal Affair', 'The Intouchables', 'Kon-Tiki', 'Rust and Bone'],
                   'best performance by an actress in a supporting role in a motion picture' : ['Anne Hathaway', 'Amy Adams', 'Sally Field', 'Helen Hunt', 'Nicole Kidman'],
                   'best performance by an actor in a supporting role in a motion picture' : ['Christopher Waltz', 'Alan Arkin', 'Leonardo DiCaprio', 'Phillip Seymour Hoffman', 'Tommy Lee Jones'],
                   'best director - motion picture' : ['Ben Affleck', 'Kathryn Bigelow', 'Ang Lee', 'Steven Spielberg', 'Quentin Tarantino'],
                   'best screenplay - motion picture' : ['Quentin Tarantino', 'Tony Kushner', 'David O Russel', 'Mark Boal'],
                   'best original score - motion picture' : ['Mychael Danna', 'Dario Marianelli', 'Alexandre Desplat', 'John Williams', 'Tom Tykwer', 'Johnny Klimek', 'Reinhold Heil'],
                   'best original song - motion picture' : ['Skyfall', 'For You', 'Not Running Anymore', 'Safe & Sound', 'Suddenly'],
                   'best television series - drama' : ['Homeland', 'Breaking Bad', 'Boardwalk Empire', 'Downton Abbey', 'The Newsroom'],
                   'best performance by an actress in a television series - drama' : ['Claire Danes', 'Connie Britton', 'Glenn Close', 'Michelle Dockery', 'Julianna Margulies'],
                   'best performance by an actor in a television series - drama' : ['Damian Lewis', 'Steve Buscemi', 'Bryan Cranston', 'Jeff Daniels', 'Jon Hamm'],
                   'best television series - comedy or musical' : ['Girls', 'The Big Bang Theory', 'Episodes', 'Modern Family', 'Smash'],
                   'best performance by an actress in a television series - comedy or musical' : ['Lena Dunham', 'Zooey Deschanel', 'Tina Fey', 'Julia Lois Dreyfus', 'Amy Poehler'],
                   'best performance by an actor in a television series - comedy or musical' : ['Don Cheadle', 'Alec Baldwin', 'Lois C.K.', 'Matt LeBlanc', 'Jim Parsons'],
                   'best mini-series or motion picture made for television' : ['Game Change', 'The Girl', 'The Hour', 'Hatfields & McCoys', 'Political Animals'],
                   'best performance by an actress in a mini-series or motion picture made for television' : ['Julianne Moore', 'Nicole Kidman', 'Jessica Lange', 'Sienna Miller', 'Sigourney Weaver'],
                   'best performance by an actor in a mini-series or motion picture made for television' : ['Kevin Costner', 'Benedict Cumberbatch', 'Woody Harrelson', 'Toby Jones', 'Clive Owen'],
                   'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television' : ['Maggie Smith', 'Hayden Panettiere', 'Archie Panjabi', 'Sarah Paulson', 'Sofia Vergara'],
                   'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television' : ['Ed Harris', 'Max Greenfield', 'Danny Houston', 'Mandy Patinkin', 'Eric Stonestreet']}

AWARDS_LISTS = [['cecil', 'demille', 'award'],
                ['best', 'motion picture', 'drama'], # no actor or actress
                ['best', 'actress', 'drama'],
                ['best', 'actor', 'drama'],
                ['best', 'motion picture', 'comedy', 'musical'], # no actor or actress
                ['best', 'actress', 'comedy', 'musical'],
                ['best', 'actor', 'comedy', 'musical'],
                ['best', 'animated'],
                ['best', 'foreign'],
                ['best', 'actress', 'supporting'],
                ['best', 'actor', 'supporting'],
                ['best', 'director'],
                ['best', 'screenplay'],
                ['best', 'score'],
                ['best', 'song'],
                ['best', 'television', 'drama'], # no actor or actress
                ['best', 'actress', 'television', 'drama'],
                ['best', 'actor', 'television', 'drama'],
                ['best', 'television', 'comedy', 'musical'], # no actor or actress
                ['best', 'actress', 'television', 'comedy', 'musical'],
                ['best', 'actor', 'television', 'comedy', 'musical'],
                ['best', 'mini series', 'motion picture', 'television'], # mini series OR motion picture
                ['best', 'actress', 'mini series', 'motion picture', 'television'], # mini series OR motion picture
                ['best', 'actor', 'mini series', 'motion picture', 'television'],
                ['best', 'actress', 'supporting', 'series', 'mini series', 'motion picture', 'television'], # series OR mini series OR motion picture
                ['best', 'actor', 'supporting', 'series', 'mini series', 'motion picture', 'television']] # series OR mini series OR motion picture

stop_words = ['.', ',', '!', '?', '(', '-', ' on ', ' the ', ' male ', ' female ', ' in ', ' a ', ' is ', ' for ', ' at ', ' golden ', ' globes ', ' by ', ' an ', ' category ', ' and ', ' show ']
                

class Award(object):

    def __init__(self, a_name, a_nominees=[], a_winner=[], a_presenters=[], a_sentiments=[]):

        self.name = a_name
        self.nominees = a_nominees
        self.winners = a_winner
        self.presenters = a_presenters

    def get_nominees(self, year):

        if self.nominees:

            return self.nominees

        else:

            self.nominees = NOMINEES_2013[self.name]

            return self.nominees
       
        
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
    

    if not (os.path.isfile("./clean_tweets%s.json" % year)):
        raise Exception('Tweets for %s have not been preprocessed')

    with open("./clean_tweets%s.json" % year) as clean_file:
        tweets = json.load(clean_file)

    # switch words
    # film, movie, picture -> motion picture (not for things that end with film)
    # tv -> television
    # television -> television series (not for things that end with television)
    
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

def get_nominees(year):
    '''Nominees is a list of dictionaries with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here

    path = './awards_%s_pickle.txt' % year
    nominees = {}
    try:
        with open(path) as awards_file:

            awards = pickle.load(awards_file)

    except NameError:

        print 'Cannot get nominees. Preprocessing is not complete. "%s" is not a file' % path

    for award in awards:

        nominees[award.name] = award.nominees

            
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

    if not (os.path.isfile("./clean_tweets%s.json" % year)):
        raise Exception('Tweets for %s have not been preprocessed')

    with open("./clean_tweets%s.json" % year) as clean_file:
        tweets = json.load(clean_file)

    re.findall("([A-Z][-'a-zA-Z]+\s[A-Z][-'a-zA-Z]+)", tweet)

    for tweetIndex in range(20):

        clean_tweet = clean(tweets[tweetIndex])

        print clean_tweet
        
    presenters = []

    
    return presenters

def clean(tweet, change_film=True):

    clean_tweet = tweet

    if 'movie' in clean_tweet:

        'motion picture'.join([a for a in clean_tweet.split('movie')])

    if change_film and 'film' in clean_tweet:

        'motion picture'.join([a for a in clean_tweet.split('film')])

    if 'picture' in clean_tweet and 'motion' not in clean_tweet:

        'motion picture'.join([a for a in clean_tweet.split('picture')])

    if ' tv ' in clean_tweet:

        ' television '.join([a.strip() for a in clean_tweet.split(' tv ')])

    if 'comedy' in clean_tweet and 'musical' not in clean_tweet:

        'comedy or musical'.join([a for a in clean_tweet.split('comedy')])

    elif 'musical' in clean_tweet and 'comedy' not in clean_tweet:

        'comedy or musical'.join([a for a in clean_tweet.split('musical')])

    elif 'musical or comedy' in clean_tweet:

        'comedy or musical'.join([a for a in clean_tweet.split('musical or comedy')])

    for stop_word in stop_words:

        if stop_word in clean_tweet:

            clean_tweet = ' '.join([a.strip() for a in clean_tweet.split(stop_word)])

    return clean_tweet

        

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here

    # Clean the tweets of the given file path
    #file_path = './gg2013.json'
    
    #tweets = get_tweets(file_path)
    #my_clean_tweets = clean_tweets(tweets)

    # NOAH Need to write the clean tweets into a file here so that every other function can access them
    
    # Initialize all of the Awards objects using the OFFICIAL_AWARDS list
    awards_path_2013 = './awards_2013_pickle.txt'
    year = 2013
    if not (os.path.isfile(awards_path_2013)):

        with open(awards_path_2013, 'wb') as awards_file:
            
            awards_2013 = []
            for award_name in OFFICIAL_AWARDS:

                award = Award(award_name)
                awards_2013.append(award)

            pickle.dump(awards_2013, awards_file)

    try:

        with open(awards_path_2013, 'rb') as awards_file:

            awards_2013 = pickle.load(awards_file)
            nominees = []
            winners = []
            presenters = []
            sentiments = []
            for n,award in enumerate(awards_2013):

                nominees = award.get_nominees(year)
                #winners = award.get_winners(year)
                #presenters = award.get_presenters(year)
                #sentiments = award.get_sentiments(year)

                awards_2013[n] = Award(award.name, nominees, winners, presenters, sentiments)

        with open(awards_path_2013, 'wb') as awards_file:
            
            pickle.dump(awards_2013, awards_file)
            
    except NameError:

        print '%s is not a file. Could not complete preprocessing' % awards_path_2013
    
    print "Pre-ceremony processing complete."
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here

    # PRE_CEREMONY MUST BE RUN BEFORE ALL OTHER API FUNCTIONS
    pre_ceremony()

    nominees = get_nominees(2013)
    print nominees
    
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
