# modified by john
from __future__ import division
import json
import re
import pprint
import nltk
from lxml import html
import requests


stopwords = nltk.corpus.stopwords.words('english')
commonUselessWords = ['award', 'http', 'rt', 'goldenglobes', 'goldenglobe', 'best', 'wins', 'win', 'of', 'lol']
uselessWords = [['demille', 'cecil', 'b'], ['drama', 'motion', 'picture', 'actress', 'actor'], [], [], ['paul']]

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

    # set up the nominees, which turned out to be a dictionary
    nominees = {}

    # open all the tweets
    
    with open("../gg%d.json" % (year)) as file_data:
      data = json.load(file_data)

    text = [[nltk.word_tokenize(w["text"].lower()),w["text"].lower()] for w in data]
    
 
    # search for nominees
    # first award ---------------------------------------------------------------------------------------
    # first for the most special award - cecil b demille award, there is only one nominees for this award
    tweetsBuffer = []
    for w in text:
      if "cecil" in w[0] and 'demille' in w[0]: 
        tmp = [x for x in w[0] if  x.isalpha()]
        tweetsBuffer.append(tmp)
    # after get the tweets, get freqdist
    # first we need to filter the stopwords
    wordsBuffer = []
    for w in tweetsBuffer:
      for x in w:
        if x not in stopwords and x not in uselessWords[0] and x not in commonUselessWords:
          wordsBuffer.append(x);

    # get the frequent list
    cecilList = nltk.FreqDist(wordsBuffer)

    # get the result
    nominees[OFFICIAL_AWARDS[0]] = " ".join([cecilList.most_common(2)[1][0], cecilList.most_common(2)[0][0]]) 
    print nominees[OFFICIAL_AWARDS[0]]
    # end of first awards ----------------------------------------------------------------------------
    
    # second award -----------------------------------------------------------------------------------
    # firstly get the drama related tweets
    
    # get one year movie list
    usefulMovies = []
    americanMovies = []
    worldMovies = []

    # ------------------------ this part is for getting american movies ---------------------------
    americanMovies = getAmericanMovies(year) # only used in foreign film

    # ------------------------ this part is for getting world movies ------------------------------
    worldMovies = [getWorldMovies(year), getWorldMovies(year-1)]
    # get related movie list
    
    # ------------------------- foreign movie award -----------------------------------------------
    for i in range(2):
      for x in worldMovies[i]:
        foreign = 1
        for y in americanMovies:
          if x[0][0] in y[0]:
            foreign = 0
            break 
        if foreign:
          usefulMovies.append(x)

    foreignMovies = []
    for x in usefulMovies:
      for y in text:
        if x[0][0] in y[1]:
          foreignMovies.append(x)
          break

    frequency = {}
    for x in foreignMovies:
      count = 0
      for y in text:
        if x[0][0] in y[1] and 'foreign' in y[1]:
          count+=1
      frequency[x[0][0]] = count

    foreignList = sorted(frequency.items(), key = lambda x:x[1], reverse = True)
    nominees[OFFICIAL_AWARDS[8]] = [ x[0] for x in foreignList[:5]]
    print 'foreign', foreignList[:5]
    # ----------------------------------- end of foreign movie --------------------------------------

    # --- start of drama movie ----------------------------------------------------------------------
    tweetsBuffer = []
    usefulMovies = []
    for x in text:
      if 'drama' in x[0] and 'television' not in x[1]:
        tweetsBuffer.append(x)

    for i in range(2):
      for x in worldMovies[i]:
        if 'drama' in x[1]:
          for y in tweetsBuffer:
            if x[0][0] in y[1]:
              usefulMovies.append(x)
              break
    
    frequency = {}
    for x in usefulMovies:
      total = 0;
      base = 0;
      for y in nltk.word_tokenize(x[0][0]):
        if y.isalpha() and y not in stopwords and y not in commonUselessWords and y not in uselessWords[1]:
          base+=1
          for z in tweetsBuffer:
            if y in z[0]:
              total+=1
      if base != 0:
        frequency[x[0][0]] = total/base

    dramaList = sorted(frequency.items(), key = lambda x:x[1], reverse=True)
    nominees[OFFICIAL_AWARDS[1]] = [x[0] for x in dramaList[:5]]
    print 'drama', dramaList[:5]
    # --------------------------------- end of drama movie ----------------------------------------

    
    # --------------------------  comedy or musical related movie ---------------------------------
    tweetsBuffer = []
    usefulMovies = []

    for x in text:
      if 'musical' in x[0] or 'comedy' in x[0]:
        if 'television' not in x[1]:
          tweetsBuffer.append(x)

    for i in range(2):
      for x in worldMovies[i]:
        if 'musical' in x[1] or 'comedy' in x[1]:
          for y in tweetsBuffer:
            if x[0][0] in y[1]:
              usefulMovies.append(x)
              break

    frequency = {}
    for x in usefulMovies:
      base = 0
      total = 0
      for y in nltk.word_tokenize(x[0][0]):
        if y not in stopwords and y.isalpha() and y not in commonUselessWords and y not in uselessWords[4]:
          base+=1
          for z in tweetsBuffer:
            if y in z[0]:
              total+=1
      if base != 0:
        frequency[x[0][0]] = total/base
    
    comedyList = sorted(frequency.items(), key=lambda x:x[1], reverse=True)
    nominees[OFFICIAL_AWARDS[4]] = [x[0] for x in comedyList[:5]]
    print 'comedy', comedyList[:5]
    # -------------------------- end of comedy and musical movie -----------------------------------

    '''
    # animated movie
    tweetsBuffer = []
    nominees[OFFICIAL_AWARDS[1]] = []
    for w in text:
      if 'animated' in w[0] or 'cartoon' in w[0] and 'television' not in w[1]:
        tweetsBuffer.append(w[0])

    wordsBuffer = []
    frequency = {}
    for x in usefulMovies:
      if 'fantasy' not in x[1] and 'family' not in x[1] and 'adventure' not in x[1]:
        continue
      total = 0
      base = 0
      for z in nltk.word_tokenize(x[0][0]):
        if z.isalpha() and z not in stopwords:
          base += 1
          for y in tweetsBuffer:
            if z in y:
              total += 1
      frequency[x[0][0]]=total/base

    cartoonList = sorted(frequency.items(), key = lambda x:x[1], reverse = True)
    print cartoonList[:10]
    '''
    
    # try to get all nominees for drama movie
    

    # testing idea here
    #for w in nominee_data:
    #    if "boardwalk" in w[0]:
    #        print w[1]

    # Your code here
    return nominees

def get_winners(year):
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

    '''
    # firstly import the tweets and do the filtering
    print "Filtering Related Tweets"
    # Open and import the json tweets data
    with open("../gg2013.json") as file_data:
        data = json.load(file_data)

    text = [[nltk.word_tokenize(w["text"].lower()),w["text"].lower()] for w in data]
    
    # start filtering
    # nomiees related tweets
    nominees_text = [w for w in text if "nominated" in w[0] or "nominee" in w[0] or "nominees" in w[0] or "endorse"]
    with open("filteredTweets%d.json" % (2013), 'w') as file_data:
        json.dump(nominees_text, file_data)

    # winner related tweets -- work on it later

    # television related tweets 
    television_text = [w for w in text if "television" in w[0] or "series" in w[0]]
    with open("televisionTweets%d.json" % (2013), 'w') as file_data:
        json.dump(television_text, file_data)

    # movie related 
    movie_text = [w for w in text if "television" not in w[0]]
    with open("movieTweets%d.json" % (2013), 'w') as file_data:
        json.dump(movie_text, file_data)




    # this part is for winner ----- keywords: best

    print "Finished Filtering"
    # --------------------------------- end of filtering ---------------------------------
    '''
    print "Pre-ceremony processing complete."
    return

# get american movie
def getAmericanMovies(year):
  page = requests.get('https://en.wikipedia.org/wiki/List_of_American_films_of_%d' % (year-1))
  tree = html.fromstring(page.content)
  americanMovies = []

  for x in range(1, len(tree.xpath('//div[@id="mw-content-text"]/table[2]/tr'))):
    tmp = tree.xpath('//div[@id="mw-content-text"]/table[2]/tr[%d]/td[1]/i/a/text()' % (x+1))
    if not tmp:
      tmp = tree.xpath('//div[@id="mw-content-text"]/table[2]/tr[%d]/td[1]/i/text()' % (x+1))
    if not tmp:
      tmp = tree.xpath('//div[@id="mw-content-text"]/table[2]/tr[%d]/td[1]/i/span[2]/span/a/text()' % (x+1))
    if not tmp:
      tmp = tree.xpath('//div[@id="mw-content-text"]/table[2]/tr[%d]/td[1]/i/a/text()' % (x+1))
    if not tmp:
      tmp = tree.xpath('//div[@id="mw-content-text"]/table[2]/tr[%d]/td[1]/i/span[2]/text()' % (x+1))
    title = [w.lower() for w in tmp]
    americanMovies.append(title)

  return americanMovies

# the return value is a 3d list
def getWorldMovies(year):
  worldMovies = []
  page = requests.get('https://en.wikipedia.org/wiki/%d_in_film' % (year-1))
  tree = html.fromstring(page.content)

  for j in range(3, len(tree.xpath('//div[@id="mw-content-text"]/table'))-2):
    for i in range(1,len(tree.xpath('//div[@id="mw-content-text"]/table[%d]/tr' % (j+1)))):
      tmp = tree.xpath('//div[@id="mw-content-text"]/table[%d]/tr[%d]/td[2]/i/a/text()' % (j+1, i+1))
      if not tmp:
        tmp = tree.xpath('//div[@id="mw-content-text"]/table[%d]/tr[%d]/td[1]/i/a/text()' % (j+1, i+1))
      title = [x.lower() for x in tmp]
      if not title:
        continue;

      typeBuffer = []
      existInfo = 0;
      tmp1 = tree.xpath('//div[@id="mw-content-text"]/table[%d]/tr[%d]/td[5]/text()' % (j+1, i+1))
      for x in tmp1:
        if x[0] != '\n':
          typeBuffer.append(x.lower())
      tmp1 = tree.xpath('//div[@id="mw-content-text"]/table[%d]/tr[%d]/td[5]/a/text()' % (j+1, i+1))
      for x in tmp1:
        if x[0] != '\n':
          typeBuffer.append(x.lower())

      if not typeBuffer:
        tmp1 = tree.xpath('//div[@id="mw-content-text"]/table[%d]/tr[%d]/td[4]/text()' % (j+1, i+1))
        for x in tmp1:
          if x[0] != '\n':
            typeBuffer.append(x.lower())
            tmp1 = tree.xpath('//div[@id="mw-content-text"]/table[%d]/tr[%d]/td[4]/a/text()' % (j+1, i+1))
            for x in tmp1:
              if x[0] != '\n':
                typeBuffer.append(x.lower())

      tmp1 = ' '.join(typeBuffer)
      genre = re.findall(r"[\w']+", tmp1)
      worldMovies.append([title, genre])

  return worldMovies

def tests(year):

  with open("../gg%d.json" % (year)) as file_data:
    data = json.load(file_data)

  text = [[nltk.word_tokenize(w["text"].lower()),w["text"].lower()] for w in data]

  # get one year movie list
  usefulMovies = []
  americanMovies = []
  worldMovies = []

  # ------------------------ this part is for getting american movies ---------------------------
  americanMovies = getAmericanMovies(year) # this list is only used to remove the unnecessary result for foreign movie

  # ------------------------ this part is for getting world movies ------------------------------
  worldMovies = [getWorldMovies(year), getWorldMovies(year-1)]


  return


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    get_nominees(2013)
    # tests(2013)

    return

if __name__ == '__main__':
    main()
