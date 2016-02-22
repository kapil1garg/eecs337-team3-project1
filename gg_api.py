import json
import re
import numpy
import sys
import nltk
from nltk.corpus import names, stopwords
from nltk.tokenize import *
import os.path
import collections
import pickle
import operator
import difflib
import copy


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

NOMINEES_2013 = {'cecil b. demille award': ['Jodie Foster'],
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

# Dictionary used to match title of a movie
# { AWARD_NAME : [[WORDS MUST BE IN THE TWEET], [WORDS CANT BE IN THE TWEET], [>= 1 WORD MUST BE IN TWEET]] }
AWARDS_LISTS = {'cecil b. demille award': [['cecil', 'demille', 'award'], [], []],
                'best motion picture - drama': [['best', 'motion picture', 'drama'], ['actor', 'actress', 'television'], []], # no actor or actress
                'best performance by an actress in a motion picture - drama' : [['best', 'actress', 'drama'], ['television'], []],
                'best performance by an actor in a motion picture - drama' : [['best', 'actor', 'drama'], ['television'], []],
                'best motion picture - comedy or musical' : [['best', 'motion picture', 'comedy', 'musical'], ['actor', 'actress', 'television'], []], # no actor or actress
                'best performance by an actress in a motion picture - comedy or musical' : [['best', 'actress', 'comedy', 'musical'], [], []],
                'best performance by an actor in a motion picture - comedy or musical' : [['best', 'actor', 'comedy', 'musical'], [], []],
                'best animated feature film' : [['best', 'animated'], [], []],
                'best foreign language film' : [['best', 'foreign'], [], []],
                'best performance by an actress in a supporting role in a motion picture' : [['best', 'actress', 'supporting'], ['television'], []],
                'best performance by an actor in a supporting role in a motion picture' : [['best', 'actor', 'supporting'], ['television'], []],
                'best director - motion picture' : [['best', 'director'], [], []],
                'best screenplay - motion picture' : [['best', 'screenplay'], [], []],
                'best original score - motion picture' : [['best', 'score'], [], []],
                'best original song - motion picture' : [['best', 'song'], [], []],
                'best television series - drama' : [['best', 'television', 'drama'], ['actor', 'actress'], []], # no actor or actress
                'best performance by an actress in a television series - drama' : [['best', 'actress', 'television', 'drama'], [], []],
                'best performance by an actor in a television series - drama' : [['best', 'actor', 'television', 'drama'], [], []],
                'best television series - comedy or musical' : [['best', 'television', 'comedy', 'musical'], ['actor', 'actress'], []], # no actor or actress
                'best performance by an actress in a television series - comedy or musical' : [['best', 'actress', 'television', 'comedy', 'musical'], [], []],
                'best performance by an actor in a television series - comedy or musical' : [['best', 'actor', 'television', 'comedy', 'musical'], [], []],
                'best mini-series or motion picture made for television' : [['best', 'mini series', 'motion picture', 'television'], ['actor', 'actress'], ['mini', 'series', 'motion picture']], # mini series OR motion picture
                'best performance by an actress in a mini-series or motion picture made for television' : [['best', 'actress', 'television'], [], ['mini series', 'motion picture']], # mini series OR motion picture
                'best performance by an actor in a mini-series or motion picture made for television' : [['best', 'actor', 'television'], [], ['mini series', 'motion picture']],
                'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television' : [['best', 'actress', 'supporting', 'television'], [], [' mini ', ' series ', 'motion picture']], # series OR mini series OR motion picture
                'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television' : [['best', 'actor', 'supporting', 'television'], [], [' mini ', ' series ', 'motion picture']]} # series OR mini series OR motion picture


stop_words = nltk.corpus.stopwords.words('english')
stop_words.extend(['http', 'golden', 'globe', 'globes', 'goldenglobe', 'goldenglobes'])
stop_words.extend(['-', 'male', 'female', '#goldenglobes', '#gg'])
stop_words = set(stop_words)
#stop_words = ['.', ',', '!', '?', '(', '-', ' on ', ' the ', ' male ', ' female ', ' in ', ' a ', ' is ', ' for ', ' at ', 'golden ', 'globes ', 'goldenglobes', 'gg', ' by ', ' an ', ' category ', ' and ', ' show ']
                
MALE_NAMES = nltk.corpus.names.words('male.txt')
FEMALE_NAMES = nltk.corpus.names.words('female.txt')


def load_data(year):
    file_string = 'gg' + str(year) + '.json'
    tweets = {}
    with open(file_string, 'r') as f:
        tweets = json.load(f)
    return tweets

def lower_case_tweet(tweet):
    lower_tweet = tweet
    lower_tweet = lower_tweet.lower()
    return lower_tweet

def presenters_remove_stop_words_tweet(stop_words, tweet):

    stop_words_removed_tweet = tweet['text'].split()
    stop_words_removed_tweet = ' '.join([str(w) for w in stop_words_removed_tweet if all(ord(c) < 128 for c in w) and str(w).lower() not in stop_words])
    return stop_words_removed_tweet

def lower_case_all(tweets):
    tweets = copy.deepcopy(tweets)
    re_retweet = re.compile('rt', re.IGNORECASE)
    return [lower_case_tweet(tweet) for tweet in tweets if not re.match(re_retweet, tweet)]

NAMES = set(lower_case_all(MALE_NAMES + FEMALE_NAMES))

def presenters_remove_stop_words_all(tweets):
    tweets = copy.deepcopy(tweets)
    presenter_stop_words = nltk.corpus.stopwords.words('english')
    presenter_stop_words.extend(['http', 'golden', 'globe', 'globes', 'goldenglobe', 'goldenglobes', '-', 'male', 'female', '#goldenglobes', '#gg'])
    presenter_stop_words = set(presenter_stop_words)
    return [presenters_remove_stop_words_tweet(presenter_stop_words, tweet) for tweet in tweets]


class Award(object):

    def __init__(self, a_name, a_nominees=[], a_winners=[], a_presenters=[], a_sentiments=[]):

        self.name = a_name
        self.nominees = a_nominees
        self.winners = a_winners
        self.presenters = a_presenters
        self.sentiments = a_sentiments

    def get_nominees(self, year):

        if not self.nominees:

            self.nominees = [' '.join(word_tokenize(nominee.lower())) for nominee in NOMINEES_2013[self.name]]


        return self.nominees

    def get_winners(self, year):

        if not self.winners:

            self.winners = []

        return self.winners

    def get_presenters(self, year):

        re_Presenters = re.compile('present|\sgave|\sgiving|\sgive|\sannounc|\sread|\sintroduc', re.IGNORECASE)
        re_Names = re.compile('([A-Z][a-z]+?\s[A-Z.]{,2}\s{,1}?[A-Z]?[-a-z]*?)[\s]')

        names_lower = NAMES
            
        presentersCount = {}
        if not self.presenters:

            cased_clean_tweets_file_path = "./cased_clean_tweets%s.json" % year
            if not (os.path.isfile(cased_clean_tweets_file_path)):
                raise Exception('Tweets for %s have not been preprocessed' % year)

            with open(cased_clean_tweets_file_path) as cased_clean_file:
                tweets = json.load(cased_clean_file)

            for tweet in tweets:
                
                clean_tweet = clean(tweet)
                clean_tweet = re.sub('(\'s)',' ', clean_tweet)
                if re.search(re_Presenters, clean_tweet):
   
                    lower_clean_tweet = lower_case_tweet(clean_tweet) 
                    award_name = self.name
                    award_words = AWARDS_LISTS[award_name][0]
                    award_not_words = AWARDS_LISTS[award_name][1]
                    award_either_words = AWARDS_LISTS[award_name][2]

                        
                    if all([word in lower_clean_tweet for word in award_words])\
                       and not( any([not_word in lower_clean_tweet for not_word in award_not_words]))\
                       and ((len(award_either_words) == 0) or any([either_word in lower_clean_tweet for either_word in award_either_words])):

                        tweet_names = re.findall(re_Names, clean_tweet)
                        for name in tweet_names:

                            name = name.lower()
                            name_token = word_tokenize(name)
                            dictName = name
                            if len(name_token) > 1:
                                first_name = name_token[0]
                                last_name = name_token[-1]
                                
                                if first_name in names_lower and last_name not in ' '.join(self.nominees):
                                    
                                    if first_name not in award_name and last_name not in award_name:
                                        
                                        if dictName not in presentersCount.keys():
                                            
                                            presentersCount[dictName] = 1
                                            
                                        else:
                                            
                                            presentersCount[dictName] += 1



            presenters_full = sorted(presentersCount.items(), key=operator.itemgetter(1), reverse=True)

            if len(presenters_full) > 1:
                
                if float(presenters_full[1][1]) / presenters_full[0][1] < 0.5:

                    self.presenters = [str(presenters_full[0][0])]
                else:
                    
                    self.presenters = [str(presenters_full[0][0]), str(presenters_full[1][0])]
            elif len(presenters_full) == 1:

                self.presenters = [str(presenters_full[0][0])]
                
        return self.presenters

    def get_sentiments(self, year):

        if not self.sentiments:

            self.sentiments = []

        return self.sentiments
        
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
    

    #if not (os.path.isfile("./clean_tweets%s.json" % year)):
    #    raise Exception('Tweets for %s have not been preprocessed' % year)

    #with open("./clean_tweets%s.json" % year) as clean_file:
    #    tweets = json.load(clean_file)
        
    raw_tweets = load_data(year)
    n_tweets = len(raw_tweets)
    tweet_iterator = xrange(n_tweets)
    processed_tweets = []

    # make all tweets lower case and remove any retweets
    for i in tweet_iterator:
        current_word_list = re.findall(r"['a-zA-Z]+\b", raw_tweets[i]['text'].lower())
        if 'rt' not in current_word_list:
            processed_tweets.append(' '.join(current_word_list))
            
    tweets = processed_tweets

    
    awards = []
    for u_tweet in tweets:
        
        if 'best' in u_tweet:

            tweet = u_tweet

            drama_match = re.search(re_Best_Drama, tweet)
            musical_match = re.search(re_Best_Musical, tweet)
            comedy_match = re.search(re_Best_Comedy, tweet)

            if drama_match or musical_match or comedy_match:
                
                if drama_match:

                    for match_str in drama_match.groups():

                        award = str(match_str.lower())

                        if ' film ' in award:

                            award = ' motion picture '.join([a.strip() for a in award.split(' film ')])

                        awards.append(format_award(' - drama'.join([a.strip() for a in award.split('drama')])))
                            
                if musical_match and not comedy_match:

                    for match_str in musical_match.groups():

                        award = str(match_str.lower())

                        if ' film ' in award:

                            award = ' motion picture '.join([a.strip() for a in award.split(' film ')])

                        if 'musical' in award and 'comedy' not in award:

                            award = ' - comedy or musical '.join([a.strip() for a in award.split('musical')])

                        elif 'musical or comedy' in award:

                            award = ' - comedy or musical '.join([a.strip() for a in award.split('musical or comedy')])

                        awards.append(format_award(award.strip()))
                
                if comedy_match:

                    for match_str in comedy_match.groups():

                        award = str(match_str.lower())

                        if ' film ' in award:

                            award = ' motion picture '.join([a.strip() for a in award.split(' film ')])
                        
                        if 'comedy' in award and 'musical' not in award:

                            award = ' - comedy or musical '.join([a.strip() for a in award.split('comedy')])

                        elif 'musical or comedy' in award:

                            award = ' - comedy or musical '.join([a.strip() for a in award.split('musical or comedy')])

                        awards.append(format_award(award))

            else:

                mp_match = re.search(re_Best_MotionPicture, tweet)
                tv_match = re.search(re_Best_Television, tweet)
                film_match = re.search(re_Best_Film, tweet)

                if mp_match:

                    for match_str in mp_match.groups():

                        awards.append(format_award_2(str(match_str.lower())))

                elif tv_match:

                    for match_str in tv_match.groups():

                        awards.append(format_award_2(str(match_str.lower())))

                elif film_match:

                    for match_str in film_match.groups():

                        awards.append(format_award_2(str(match_str.lower())))

    awards_fd = nltk.FreqDist(awards)
    #total = 0
    #for award in awards_fd:
    #    total += award[1]
    #print 'percentage: %s' % (float(awards_fd[29][1])/total)
       
    return [award[0] for award in awards_fd.most_common(30) if award[0] is not None]

def format_award(award):
    
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
    
    if award_final in ['best - drama', 'best - comedy or musical', 'best - motion picture']:

        award_final = None
        
    return award_final
    
def format_award_2(award):
    
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
            
    if award_final in ['best film', 'best - motion picture', 'best television']:

        award_final = None
    return award_final
    

def get_nominees(year):
    '''Nominees is a list of dictionaries with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here

    path = './awards_%s_pickle.txt' % year
    nominees = []
    try:
        with open(path) as awards_file:

            awards = pickle.load(awards_file)

    except NameError:

        print 'Cannot get nominees. Preprocessing is not complete. "%s" is not a file' % path

    for award in awards:

        nominees.append({award.name : award.nominees})

            
    return nominees

def get_winner(year):
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

    path = './awards_%s_pickle.txt' % year
    presenters = []
    try:
        with open(path) as awards_file:

            
            awards = pickle.load(awards_file)

    except IOError:

        print 'Cannot get presenters. Preprocessing is not complete. "%s" is not a file' % path

    for award in awards:

        presenters.append({award.name : award.presenters})

    
    return presenters

def clean(tweet, change_film=True):

    clean_tweet = tweet
            
    if '#' in clean_tweet:

        clean_tweet = ''.join([a for a in clean_tweet.split('#')])
        
    if 'movie' in clean_tweet:

        clean_tweet = 'motion picture'.join([a for a in re.split("movie", clean_tweet, flags=re.IGNORECASE)])

    if change_film and 'film' in clean_tweet:

        clean_tweet = 'motion picture'.join([a for a in re.split("film", clean_tweet, flags=re.IGNORECASE)])

    if 'picture' in clean_tweet and 'motion' not in clean_tweet:

        clean_tweet = 'motion picture'.join([a for a in re.split("picture", clean_tweet, flags=re.IGNORECASE)])

    if ' tv ' in clean_tweet:

        clean_tweet = ' television '.join([a.strip() for a in re.split(" tv ", clean_tweet, flags=re.IGNORECASE)])

    if 'comedy' in clean_tweet and 'musical' not in clean_tweet:

        clean_tweet = 'comedy or musical'.join([a for a in re.split("comedy", clean_tweet, flags=re.IGNORECASE)])

    elif 'musical' in clean_tweet and 'comedy' not in clean_tweet:

        clean_tweet = 'comedy or musical'.join([a for a in re.split("musical", clean_tweet, flags=re.IGNORECASE)])

    elif 'musical or comedy' in clean_tweet:

        clean_tweet = 'comedy or musical'.join([a for a in re.split("musical or comedy", clean_tweet, flags=re.IGNORECASE)])

    return clean_tweet

        

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here

    print 'STARTING PRE CEREMONY\n\n'
    
    years = [2013]
        
    for year in years:
        
        print 'Reading tweets from %s...' % year
        
        cased_clean_tweets_path = path = './cased_clean_tweets%s.json' % year
        raw_tweets = load_data(year)
        cased_tweets = presenters_remove_stop_words_all(raw_tweets)
        
        with open(cased_clean_tweets_path, 'w') as cased_tweets_file:
            
            json.dump(cased_tweets, cased_tweets_file)

        # Initialize all of the Awards objects using the OFFICIAL_AWARDS list
        awards_objects_path = './awards_%s_pickle.txt' % year
        if not (os.path.isfile(awards_objects_path)) or True:

            print 'Initializing GG Awards for %s' % year
            with open(awards_objects_path, 'wb') as awards_file:
                
                awards_list = []
                for award_name in OFFICIAL_AWARDS:
    
                    award = Award(award_name)
                    nominees = award.get_nominees(year)
                    winners = award.get_winners(year)
                    presenters = award.get_presenters(year)
                    sentiments = award.get_sentiments(year)
                    award = Award(award_name, nominees, winners, presenters, sentiments)
                    awards_list.append(award)

                pickle.dump(awards_list, awards_file)
    
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

    awards = get_awards(2013)
    print awards

    presenters = get_presenters(2013)
    print presenters
    
    return
    

if __name__ == '__main__':
    main()
