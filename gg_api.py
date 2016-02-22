from __future__ import division
import json
import re
import pprint
import nltk
from lxml import html
import requests


stopwords = nltk.corpus.stopwords.words('english')
unistopwords = ['real', 'ever', 'americans', 'goldenglobes', 'acting', 'reality', 'mr', 'football', 'u', 'somehow', 'somewhat', 'anyone', 'everyone', 'musical', 'comedy', 'drama']
bistopwords = ['my wife', 'my husband', 'the last', 'the other', 'the show', 'the goldenglobes', 'the nominees', 'the oscars', 'any other', 'motion picture']
pronouns = ['he', 'she', 'it', 'they', 'this', 'that', 'these', 'those', 'there']
verbs = ['do', 'does', 'will', 'has', 'may', 'might']
singers = ['adele','taylor swift']


OFFICIAL_AWARDS = ['cecil b. demille award',         # this is a special case, deal with it later
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

def read_data(year):
    file_string = 'gg' + str(year) + '.json'
    with open(file_string, 'r') as f:
        tweets = json.load(f)
    rawstring = [tweet['text'] for tweet in tweets]
    return rawstring

def remove_hashtags(tweet):
    tokens = tweet.split()
    new_tokens = []
    for token in tokens:
        if '#' in token or '@' in tokens:
            continue
        new_tokens.append(token.lower())
    
    result = ' '.join(new_tokens)
    return result

def trim_data(raw_data):
    tweets = []
    for tweet in raw_data:
        tweets.append(remove_hashtags(tweet))
    return tweets

def getMovieTitles(year):
    worldMovies = []
    page = requests.get('https://en.wikipedia.org/wiki/%d_in_film' % (year-1))
    tree = html.fromstring(page.content)

    for j in range(3, len(tree.xpath('//div[@id="mw-content-text"]/table'))-2):
        for i in range(1,len(tree.xpath('//div[@id="mw-content-text"]/table[%d]/tr' % (j+1)))):
            tmp = tree.xpath('//div[@id="mw-content-text"]/table[%d]/tr[%d]/td[2]/i/a/text()' % (j+1, i+1))
            if not tmp:
                tmp = tree.xpath('//div[@id="mw-content-text"]/table[%d]/tr[%d]/td[1]/i/a/text()' % (j+1, i+1))
            title = [x.lower() for x in tmp]
            worldMovies=worldMovies+title
            if not title:
                continue;
    return worldMovies

def getNameDictionary(gender, subtitle=''):
    nameList = []

    page = requests.get('http://names.mongabay.com/%s_names%s.htm' % (gender, subtitle))
    tree = html.fromstring(page.content)

    namelen = len(tree.xpath('//table[@id="myTable"]/tr'))

    for i in range(1, namelen):
        name = tree.xpath('//table[@id="myTable"]/tr[%d]/td[1]/text()' % (i+1))
        for x in name:
            if name:
                nameList.append(x.lower())
    return nameList

def candidateCheck(candidate):
    if not candidate:
        return ''
    if 'goldenglobe' in candidate:
        return ''
    if 'motion picture' in candidate:
        return ''
    candidate = re.sub(r'\bblah\b', '', candidate)
    tokens = nltk.word_tokenize(candidate)
    tokens_length = len(tokens)
    if tokens[-1] in verbs:
        del tokens[-1]
    for token in tokens:
        if token in ['comedy', 'musical', 'drama', 'supporting']:
            return ''
    if tokens_length>=7:
        return ''
    elif tokens_length==1 and tokens[0] in (stopwords+unistopwords+pronouns):
        return ''
    elif tokens_length==2 and ' '.join(tokens) in bistopwords:
        return ''
    elif tokens_length >1 and tokens[0] in pronouns:
        return ''
    return ' '.join(tokens)

def candidatePreprocess(candidates, tweets):
    frequency = []
    for candidate in candidates:
        if candidate not in singers:
            frequency.append([candidate, 0])

    for tweet in tweets:
        for candidate in frequency:
            if candidate[0] in tweet:
                candidate[1]+=1

    passedCandidates = [x[0] for x in frequency if x[1]>19]
    return passedCandidates

def getRawCandidates(general_patterns, tweets):
    candidates = []
    for pattern in general_patterns:
        for tweet in tweets:
            matches = re.findall(pattern, tweet)
            for match in matches:
                match = candidateCheck(match)
                if match:
                    candidates.append(match)
    candidates = list(set(candidates))
    candidates = candidatePreprocess(candidates, tweets)
    return candidates

def getCandidates(raw_candidates, tweets):
    # check existance
    candidates = []
    for candidate in raw_candidates:
        for tweet in tweets:
            if candidate in tweet:
                candidates.append(candidate)
                break
    # remove over lapping
    passlist = []
    for x in candidates:
        overLap = False
        for y in candidates:
            if x != y and x in y:
                overLap = True
                break
        if not overLap:
            passlist.append(x)
    return passlist

def getHumanCandidates(candidates, namelist):
    passlist = []
    for candidate in candidates:
        tokens = nltk.word_tokenize(candidate)
        length = len(tokens)
        if length<2 or length>3:
            continue
        if tokens[0] not in namelist:
            continue
        if tokens[1] in ['and', '&']:
            continue
        passlist.append(candidate)
    return passlist

def getNonHumanCandidates(candidates, namelist):
    passlist = []
    for candidate in candidates:
        tokens = nltk.word_tokenize(candidate)
        length = len(tokens)
        if length == 2 and tokens[0] in namelist:
            continue
        if length == 3 and tokens[0] in namelist and tokens[1] not in ['and', '&']:
            continue
        passlist.append(candidate)
    return passlist

def getMovieCandidates(candidates, lastFiveYearMovie):
    passlist = []
    for candidate in candidates:
        if candidate in lastFiveYearMovie:
            passlist.append(candidate)
    return passlist

# keywords is of the relationship or, while no words is and
def getTargetTweets(tweets, keywords, nowords):
    targets = []
    for tweet in tweets:
        status = False
        for keyword in keywords:
            if keyword in tweet:
                status = True
                break
        if not status:
            continue
        for noword in nowords:
            if noword in tweet:
                status = False
                break
        if status:
            targets.append(tweet)
    return targets

def getOrderedCandidates(keywords, nowords, candidates, tweets):
    frequency = [[candidate, 0] for candidate in candidates]
    tweets = getTargetTweets(tweets, keywords, nowords)
    for tweet in tweets:
        for candidate in frequency:
            if candidate[0] in tweet:
                candidate[1]+=1
    result = sorted(frequency, key=lambda x:x[1], reverse=True)
    result = [x[0] for x in result]
    return result

def get_demille(general_patterns, tweets, female_name, male_name):
    # first got all the candidate
    raw_candidates = getRawCandidates(general_patterns, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['demille', 'cecil'], [], candidates, tweets)
    candidates = getHumanCandidates(candidates, female_name+male_name)
    return candidates[0]

def get_drama_movie(general_patterns, tweets, lastFiveYearMovie):
    raw_candidates = getRawCandidates(general_patterns, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['drama'], ['television', 'tv', 'series', 'foreign'], candidates, tweets)
    candidates = getMovieCandidates(candidates, lastFiveYearMovie)
    #print candidates
    return candidates[:5]

def get_drama_movie_actress(special_pattern, tweets, female_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['drama'], ['television', 'tv', 'series', 'supporting'], candidates, tweets)
    candidates = getHumanCandidates(candidates, female_name)
    print candidates
    return candidates[:5]

def get_drama_movie_actor(special_pattern, tweets, male_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['drama'], ['television', 'tv', 'series', 'supporting'], candidates, tweets)
    candidates = getHumanCandidates(candidates, male_name)
    print candidates
    return candidates[:5]

def get_comedy_movie(special_pattern, tweets, lastFiveYearMovie):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['comedy', 'musical'], ['television', 'tv', 'series', 'drama', 'foreign'], candidates, tweets)
    candidates = getMovieCandidates(candidates, lastFiveYearMovie)
    print candidates
    return candidates[:5]

def get_comedy_movie_actress(special_pattern, tweets, female_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['comedy', 'musical'], ['television', 'tv', 'series', 'drama', 'foreign'], candidates, tweets)
    candidates = getHumanCandidates(candidates, female_name)
    print candidates
    return candidates[:5]

def get_comedy_movie_actor(special_pattern, tweets, male_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['comedy', 'musical'], ['television', 'tv', 'series', 'drama', 'foreign'], candidates, tweets)
    candidates = getHumanCandidates(candidates, male_name)
    print candidates
    return candidates[:5]

def get_animated_feature_movie(special_pattern, tweets, lastFiveYearMovie):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['animated feature', 'cartoon', 'animated film'], ['television', 'tv', 'series', 'drama', 'musical'], candidates, tweets)
    candidates = getMovieCandidates(candidates, lastFiveYearMovie)
    return candidates[:5]

def get_foreign_language_movie(special_pattern, tweets, lastFiveYearMovie):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['foreign', 'language', 'exotic'], ['television', 'tv', 'series', 'drama', 'musical'], candidates, tweets)
    candidates = getMovieCandidates(candidates, lastFiveYearMovie)
    return candidates[:5]

def get_movie_supporting_actress(special_pattern, tweets, female_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['supporting'], ['television', 'tv', 'series', 'mini'], candidates, tweets)
    candidates = getHumanCandidates(candidates, female_name)
    return candidates[:5]

def get_movie_supporting_actor(special_pattern, tweets, male_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['supporting'], ['television', 'tv', 'series', 'mini'], candidates, tweets)
    candidates = getHumanCandidates(candidates, male_name)
    return candidates[:5]

def get_director(special_pattern, tweets, nameList):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['director'], ['television', 'tv', 'series', 'mini'], candidates, tweets)
    candidates = getHumanCandidates(candidates, nameList)
    return candidates[:5]

def get_screenplay(special_pattern, tweets, namelist):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['screenplay'], ['television', 'tv', 'series', 'mini'], candidates, tweets)
    candidates = getHumanCandidates(candidates, namelist)
    return candidates[:5]

def get_original_score(special_pattern, tweets, namelist):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['original score'], ['television', 'tv', 'series', 'mini'], candidates, tweets)
    candidates = getNonHumanCandidates(candidates, namelist)
    return candidates[:5]

def get_original_song(special_pattern, tweets, namelist):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['original song'], ['television', 'tv', 'series'], candidates, tweets)
    candidates = getNonHumanCandidates(candidates, namelist)
    return candidates[:5]

def get_drama_series(special_pattern, tweets, nameList):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates(['drama'], [], candidates, tweets)
    candidates = getNonHumanCandidates(candidates, nameList)
    return candidates[:5]

def get_drama_series_actress(special_pattern, tweets, female_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates(['drama'], [], candidates, tweets)
    candidates = getHumanCandidates(candidates, female_name)
    return candidates[:5]

def get_drama_series_actor(special_pattern, tweets, male_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates(['drama'], [], candidates, tweets)
    candidates = getHumanCandidates(candidates, male_name)
    return candidates[:5]

def get_comedy_series(special_pattern, tweets, namelist):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates(['musical', 'comedy'], ['drama'], candidates, tweets)
    candidates = getNonHumanCandidates(candidates, namelist)
    return candidates[:5]

def get_comedy_series_actress(special_pattern, tweets, female_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates(['musical', 'comedy'], ['drama', 'supporting'], candidates, tweets)
    candidates = getHumanCandidates(candidates, female_name)
    return candidates[:5]

def get_comedy_movie_actor(special_pattern, tweets, male_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates(['musical', 'comedy'], ['drama', 'supporting'], candidates, tweets)
    candidates = getHumanCandidates(candidates, male_name)
    return candidates[:5]

def get_mini_series(special_pattern, tweets, namelist):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series', 'mini'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates([], ['drama', 'comedy', 'musical'], candidates, tweets)
    candidates = getNonHumanCandidates(candidates, namelist)
    return candidates[:5]

def get_mini_series_actress(special_pattern, tweets, female_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates([], ['drama', 'comedy', 'musical'], candidates, tweets)
    candidates = getHumanCandidates(candidates, female_name)
    return candidates[:5]

def get_mini_series_actor(special_pattern, tweets, male_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates([], ['drama', 'comedy', 'musical'], candidates, tweets)
    candidates = getHumanCandidates(candidates, male_name)
    return candidates[:5]

def get_nonmovie_supporting_actress(special_pattern, tweets, female_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates(['supporting'], [], candidates, tweets)
    candidates = getHumanCandidates(candidates, female_name)
    return candidates[:5]

def get_nonmovie_supporting_actor(special_pattern, tweets, male_name):
    raw_candidates = getRawCandidates(special_pattern, tweets)
    candidates = getRawCandidates(raw_candidates, tweets)
    candidates = getOrderedCandidates(['television', 'tv', 'series'], ['movie', 'film', 'motion picture'], candidates, tweets)
    candidates = getOrderedCandidates(['supporting'], [], candidates, tweets)
    candidates = getHumanCandidates(candidates, male_name)
    return candidates[:5]

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

    nominees = {}

    # open all the tweets
    raw_data = read_data(year)
    tweets = trim_data(raw_data)
    # two webpags for male and female name 
    female_name = getNameDictionary('female') + getNameDictionary('female', '1')
    male_name = getNameDictionary('male') + getNameDictionary('male', '3') + getNameDictionary('male', '6') + ['christoph', 'hugh']
    lastFiveYearMovie = getMovieTitles(year)+getMovieTitles(year-1)+getMovieTitles(year-2)+getMovieTitles(year-3)+getMovieTitles(year-4)
    lastFiveYearMovie = set(lastFiveYearMovie)

    general_patterns = [r'hop[(?:es?)(?:ing)](?:\sthat)?\s+(.*?)\sw[io]ns?',
                        r'wants?\s+(.*?)\s+to\s+win', r'better\sthan\s(.*?)[.?!,]',
                        r'movie called (.*)[.!?,]', r'[(?:film)(?:movie)] - (.*?) -', 
                        r'want to see (.*?)[.!,?]', r'and (.*?) were better than']

    
    # award index 0 -- only one winner and candidate
    special_pattern = [r'[,!?.] \w+ \w+ and (\w+ \w+)[.?!]']
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[0]] = get_demille(special_pattern, tweets, female_name, male_name)
    print nominees[OFFICIAL_AWARDS[0]]
    
    # award index 1 
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[1]] = get_drama_movie(special_pattern, tweets, lastFiveYearMovie)
    print nominees[OFFICIAL_AWARDS[1]]
    
    # award index 2
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[2]] = get_drama_movie_actress(special_pattern, tweets, female_name)
    print nominees[OFFICIAL_AWARDS[2]]

    # award index 3
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[3]] = get_drama_movie_actor(special_pattern, tweets, male_name)
    print nominees[OFFICIAL_AWARDS[3]]

    # award index 4
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[4]] = get_comedy_movie(special_pattern, tweets, lastFiveYearMovie)
    print nominees[OFFICIAL_AWARDS[4]]

    # award index 5
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[5]] = get_comedy_movie_actress(special_pattern, tweets, female_name)
    print nominees[OFFICIAL_AWARDS[5]]

    # award index 6
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[6]] = get_comedy_movie_actor(special_pattern, tweets, male_name)
    print nominees[OFFICIAL_AWARDS[6]]

    # award index 7
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[7]] = get_animated_feature_movie(special_pattern, tweets, lastFiveYearMovie)
    print nominees[OFFICIAL_AWARDS[7]]
    

    # award index 8
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[8]] = get_foreign_language_movie(special_pattern, tweets, lastFiveYearMovie)
    print nominees[OFFICIAL_AWARDS[8]]
    
    # award index 9
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[9]] = get_movie_supporting_actress(special_pattern, tweets, female_name)
    print nominees[OFFICIAL_AWARDS[9]]

    # award index 10
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[10]] = get_movie_supporting_actor(special_pattern, tweets, male_name)
    print nominees[OFFICIAL_AWARDS[10]]

    # award index 11
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[11]] = get_director(special_pattern, tweets, male_name+female_name)
    print nominees[OFFICIAL_AWARDS[11]]
    

    # award index 12
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[12]] = get_screenplay(special_pattern, tweets, male_name+female_name)
    print nominees[OFFICIAL_AWARDS[12]]

    # award index 13
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[13]] = get_original_score(special_pattern, tweets, male_name+female_name)
    print nominees[OFFICIAL_AWARDS[13]]

    # award index 14
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[14]] = get_original_song(special_pattern, tweets, male_name+female_name)
    print nominees[OFFICIAL_AWARDS[14]]

    # award index 15
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[15]] = get_drama_series(special_pattern, tweets, male_name+female_name)
    print nominees[OFFICIAL_AWARDS[15]]

    # award index 16
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[16]] = get_drama_series_actress(special_pattern, tweets, female_name)
    print nominees[OFFICIAL_AWARDS[16]]

    # award index 17
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[17]] = get_drama_series_actor(special_pattern, tweets, male_name)
    print nominees[OFFICIAL_AWARDS[17]]

    # award index 18
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[18]] = get_comedy_series(special_pattern, tweets, male_name+female_name)
    print nominees[OFFICIAL_AWARDS[18]]

    # award index 19
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[19]] = get_comedy_series_actress(special_pattern, tweets, female_name)
    print nominees[OFFICIAL_AWARDS[19]]

    # award index 20
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[20]] = get_comedy_movie_actor(special_pattern, tweets, male_name)
    print nominees[OFFICIAL_AWARDS[20]]


    # award index 21
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[21]] = get_mini_series(special_pattern, tweets, male_name+female_name)
    print nominees[OFFICIAL_AWARDS[21]]

    # award index 22
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[22]] = get_mini_series_actress(special_pattern, tweets, female_name)
    print nominees[OFFICIAL_AWARDS[22]]

    # award index 23
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[23]] = get_mini_series_actor(special_pattern, tweets, male_name)
    print nominees[OFFICIAL_AWARDS[23]]

    
    # award index 24
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[24]] = get_nonmovie_supporting_actress(special_pattern, tweets, female_name)
    print nominees[OFFICIAL_AWARDS[24]]

    # award index 25
    special_pattern = []
    special_pattern = special_pattern+general_patterns
    nominees[OFFICIAL_AWARDS[25]] = get_nonmovie_supporting_actor(special_pattern, tweets, male_name)
    print nominees[OFFICIAL_AWARDS[25]]
    
    return nominees

def get_winner(year):
    '''Winners is a list of dictionaries with the hard coded award
    names as keys, and each entry a list containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    winners = {}
    nominees = get_nominees(year)
    for x in OFFICIAL_AWARDS:
        winners[x] = nominees[x][0]
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
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    return

if __name__ == '__main__':
    main()
