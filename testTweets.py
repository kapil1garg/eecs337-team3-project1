# modified by john
from __future__ import division
import json
import re
import pprint
import nltk
from lxml import html
import requests

stopwords = nltk.corpus.stopwords.words('english')
pronouns = ['he', 'she', 'it', 'they', 'this', 'that', 'these', 'those', 'there']
sighwords = ['blah']
verbs = ['do', 'does', 'will']
prepositions = ['somehow', 'somewhat', 'anyone', 'everyone']
commonUselessSingleWords = ['real', 'ever', 'americans', 'goldenglobes', 'acting', 'reality', 'mr', 'football', 'u']
commonTwoWordsPhrase = ['my wife', 'my husband', 'the last', 'the other', 'the show', 'any other'
												'the goldenglobes', 'the nominees', 'the oscars', 'any other']
famousSingers = ['adele','taylor swift']
movieList = []
femaleNameList = []
maleNameList = []
additionalmaleNameList = ['christoph', 'hugh']

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

class InfoPiece():

	keys = ['text', 'timestamp_ms', 'tokens']

	def __init__(self, piece):
		self.text = piece['text'].lower()
		self.timestamp_ms = piece['timestamp_ms']
		self.tokens = [x.lower() for x in nltk.word_tokenize(self.text) if x.isalpha() or x == '&']

	def contains(self, keywords, source):

		keywords = [keyword.lower() for keyword in keywords]
		if source == 'tokens':
			for token in self.tokens:
				if token in keywords:
					return True
		if source == 'raw':
			for keyword in keywords:
				if keyword in self.text.lower():
					return True
		return False

	def __str__(self):
		return self.text.encode('utf-8')

	def __repr__(self):
		return self.text.encode('utf-8')

	def getTokens(self):
		return self.tokens

	def getTime(self):
		return self.timestamp_ms

	def find(self, pattern):
		re.UNICODE
		matches = re.findall(pattern, self.text)
		return matches

class InfoBundle():

	def __init__(self):
		self.data = []

	def get(self, index):
		return self.data[index]
		
	def insert(self, piece):
		self.data.append(piece)

	def search(self, keywords, source = 'tokens'):
		result = []
		for x in self.data:
			if x.contains(keywords, source):
				result.append(x)
		return result

	def removeOverlapping(self, candidatelist):
		newlist = []
		for x in candidatelist:
			overLap = False
			for y in candidatelist:
				if x != y and x in y:
					overLap = True
					break
				if x==''.join(nltk.word_tokenize(y)):
					overLap = True
					break
			if not overLap:
				newlist.append(x)


		return newlist

	def getCandidates(self, patterns):
		candidates = []
		for pattern in patterns:
			for tweet in self.data:
				matches = tweet.find(pattern)
				for match in matches:
					match = trim(match)
					if checkValidation(match):
						#print match
						candidates.append(match)
		candidates = list(set(candidates))
		candidates = self.removeLessFrequentCandidates(candidates)
		candidates = self.removeSinger(candidates)
		print candidates
		return candidates

	def getDramaMovieCandidates(self, patterns, humanNameList):
		candidates = self.getCandidates(patterns)
		candidates = self.checkExistance(candidates)

		# this function need to be modified later
		candidates = self.removeOverlapping(candidates)

		# most possible drama TV winner --- this is only used for nominees, to get real winder, just get the first one form nominess
		dramaTvNominess = self.getOrderedCandidates(['drama'], ['movie'], candidates)
		dramaTvNominess = self.getOrderedCandidates(['tv', 'series', 'television'], [], dramaTvNominess)
		print dramaTvNominess[:10]
		for candidate in dramaTvNominess:
			tokens = nltk.word_tokenize(candidate)
			if len(tokens)==3 and tokens[0] in humanNameList and tokens[1] not in ['and', '&']:
				continue
			if len(tokens)!=2 or tokens[0] not in humanNameList:
				dramaTvWinner = candidate
				break
		# get the winner
		winnerCandidates = self.getOrderedCandidates(['drama'], ['television', 'tv', 'series'], candidates)

		nominees = []
		for candidate in winnerCandidates:
			if candidate == dramaTvWinner:
				continue
			tokens = nltk.word_tokenize(candidate)
			if len(tokens)==3 and tokens[0] in humanNameList and tokens[1] not in ['and', '&']:
				continue
			if len(tokens)!=2 or tokens[0] not in humanNameList:
				nominees.append(candidate)
			if len(nominees)==5:
				break

		winner = nominees[0]
		print 'dramaNominees:', nominees
		return nominees

	def getComedyMovieCandidates(self, patterns, humanNameList):
		nominees = []
		candidates = self.getCandidates(patterns)
		candidates = self.checkExistance(candidates)
		
		candidates = self.removeOverlapping(candidates)
		comedyCandidates = self.getOrderedCandidates(['comedy', 'musical'], ['television', 'tv', 'series', 'drama'], candidates)
		print comedyCandidates
		comedyTvNominees = self.getOrderedCandidates(['comedy', 'musical'], ['movie'], candidates)
		comedyTvNominees = self.getOrderedCandidates(['television', 'tv', 'series'], ['drama'], comedyTvNominees)
		print comedyTvNominees

		for candidate in comedyTvNominees:
			tokens = nltk.word_tokenize(candidate)
			if len(tokens)==3 and tokens[0] in humanNameList and tokens[1] not in ['and', '&']:
				continue
			if len(tokens)!=2 or tokens[0] not in humanNameList:
				comedyTvWinner = candidate
				break

		for candidate in comedyCandidates:
			if candidate == comedyTvWinner:
				continue
			tokens = nltk.word_tokenize(candidate)
			if len(tokens)==3 and tokens[0] in humanNameList and tokens[1] not in ['and', '&']:
				continue
			if len(tokens)!=2 or tokens[0] not in humanNameList:
				nominees.append(candidate)
			if len(nominees)==5:
				break

		winner = nominees[0]
		print 'comedyNominee:', nominees
		return nominees

	def getCartoonMovieCandidates(self, patterns, humanNameList):
		nominees = []
		candidates = self.getCandidates(patterns)
		candidates = self.checkExistance(candidates)
		candidates = self.removeOverlapping(candidates)
		if 'brave' in candidates:
			print 66666666666666666
		cartoonCandidates = self.getOrderedCandidates(['cartoon', 'child', 'animated', 'kid'], ['television', 'tv', 'series', 'drama', 'musical'], candidates)
		

		for candidate in cartoonCandidates:
			tokens = nltk.word_tokenize(candidate)
			if len(tokens)==3 and tokens[0] in humanNameList and tokens[1] not in ['and', '&']:
				continue
			if len(tokens)!=2 or tokens[0] not in humanNameList:
				nominees.append(candidate)
			if len(nominees)==5:
				break

		winner = nominees[0]
		print 'cartoonNominee:', nominees
		return nominees

	def getForeignMovieCandidates(self, patterns, humanNameList):
		nominees = []
		candidates = self.getCandidates(patterns)
		candidates = self.checkExistance(candidates)
		candidates = self.removeOverlapping(candidates)
		foreignCandidates = self.getOrderedCandidates(['foreign', 'language', 'exotic'], ['television', 'tv', 'series', 'drama', 'musical'], candidates)
		print foreignCandidates

		for candidate in foreignCandidates:
			tokens = nltk.word_tokenize(candidate)
			if len(tokens)==3 and tokens[0] in humanNameList and tokens[1] not in ['and', '&']:
				continue
			if len(tokens)!=2 or tokens[0] not in humanNameList:
				nominees.append(candidate)
			if len(nominees)==5:
				break

			winner = nominees[0]
			print 'foreignNominee:', nominees
			return nominees


	def getDramaActressCandidates(self, patterns, femaleNameList):
		nominees = []
		candidates = self.getCandidates(patterns)
		candidates = self.checkExistance(candidates)
		candidates = self.removeOverlapping(candidates)
		dramaActressNominees = self.getOrderedCandidates(['drama'], ['television', 'tv', 'series'], candidates)
		dramaActressNominees = self.getOrderedCandidates(['she', 'actress'], ['actor', 'director', 'supporting'], dramaActressNominees)

		for candidate in dramaActressNominees:
			tokens =nltk.word_tokenize(candidate)
			if len(tokens)<2 or len(tokens)>3:
				continue
			if tokens[0] not in femaleNameList or tokens[1] in ['and', '&']:
				continue
			nominees.append(candidate)
			if len(candidate) == 5:
				break

		winner = nominees[0]
		print 'dramaActressNominees:', nominees
		return nominees

	def getDramaActorCandidates(self, patterns, maleNameList):
		nominees = []
		candidates = self.getCandidates(patterns)
		candidates = self.checkExistance(candidates)
		candidates = self.removeOverlapping(candidates)
		dramaActorNominees = self.getOrderedCandidates(['drama'], ['television', 'tv', 'series'], candidates)
		dramaActorNominees = self.getOrderedCandidates(['he', 'actor'], ['actress', 'director', 'supporting'], dramaActorNominees)

		for candidate in dramaActorNominees:
			tokens =nltk.word_tokenize(candidate)
			if len(tokens)<2 or len(tokens)>3:
				continue
			if tokens[0] not in maleNameList or tokens[1] in ['and', '&']:
				continue
			nominees.append(candidate)
			if len(candidate) == 5:
				break

		winner = nominees[0]
		print 'dramaActorNominees:', nominees
		return nominees

	def getComedyActressCandidates(self, patterns, femaleNameList):
		nominees = []
		candidates = self.getCandidates(patterns)
		candidates = self.checkExistance(candidates)
		candidates = self.removeOverlapping(candidates)
		comedyActressNominees = self.getOrderedCandidates(['comedy', 'musical'], ['television', 'tv', 'series'], candidates)
		comedyActressNominees = self.getOrderedCandidates(['she', 'actress'], ['actor', 'director', 'supporting'], comedyActressNominees)

		for candidate in comedyActressNominees:
			tokens =nltk.word_tokenize(candidate)
			if len(tokens)<2 or len(tokens)>3:
				continue
			if tokens[0] not in femaleNameList or tokens[1] in ['and', '&']:
				continue
			nominees.append(candidate)
			if len(candidate) == 5:
				break

		winner = nominees[0]
		print 'comedyActressNominees:', nominees
		return nominees

	def getComedyActorCandidates(self, patterns, maleNameList):
		nominees = []
		candidates = self.getCandidates(patterns)
		candidates = self.checkExistance(candidates)
		candidates = self.removeOverlapping(candidates)

		comedyActorNominees = self.getOrderedCandidates(['comedy', 'musical'], ['television', 'tv', 'series'], candidates)
		comedyActorNominees = self.getOrderedCandidates(['he', 'actor'], ['actress', 'director', 'supporting'], comedyActorNominees)

		for candidate in comedyActorNominees:
			tokens =nltk.word_tokenize(candidate)
			if len(tokens)<2 or len(tokens)>3:
				continue
			if tokens[0] not in maleNameList or tokens[1] in ['and', '&']:
				continue
			nominees.append(candidate)
			if len(candidate) == 5:
				break

		winner = nominees[0]
		print 'comedyActorNominees:', nominees
		return nominees

	def getMovieSupportingActress(self, patterns, femaleNameList):


		return

	def getMovieSupportingActor(self, patterns, maleNameList):
		nominees = []
		candidates = self.getCandidates(patterns)
		candidates = self.checkExistance(candidates)
		candidates = self.removeOverlapping(candidates)

		supportingMovieActorNominees = self.getOrderedCandidates(['supporting'], ['mini', 'television', 'tv', 'series'], candidates)
		supportingMovieActorNominees = self.getOrderedCandidates(['he', 'actor'], ['actress', 'director'], supportingMovieActorNominees)

		for candidate in comedyActorNominees:
			tokens =nltk.word_tokenize(candidate)
			if len(tokens)<2 or len(tokens)>3:
				continue
			if tokens[0] not in maleNameList or tokens[1] in ['and', '&']:
				continue
			nominees.append(candidate)
			if len(candidate) == 5:
				break

		winner = nominees[0]
		print 'supportingMovieActorNominees:', nominees
		return nominees

	def getTargetTweets(self, keywords, nowords):
		tweets = []
		for tweet in self.data:
			if tweet.contains(keywords, 'raw'):
				if not tweet.contains(nowords, 'raw'):
					tweets.append(tweet)
		return tweets

	def checkExistance(self, candidates):
		passList = []
		for candidate in candidates:
			for x in self.data:
				if x.contains([candidate], 'raw'):
					passList.append(candidate)
					break

		return passList


	def getTimeAverage(self, winner):
		mslist = []
		for x in self.data:
			if x.contains([winner], 'raw'):
				mslist.append(x.getTime())
		# produce a range
		mslist = sorted(mslist)
		length = len(mslist)
		lowerbound = int(0.3*length)
		upperbound = length - lowerbound
		total = 0;
		base = upperbound-lowerbound+1
		for i in range(lowerbound-1, upperbound):
			total+=mslist[i]/base

		print length, lowerbound, upperbound, total
		average = int(total)
		return average


	# first keywoard is and / 2d list is for or
	def getOrderedCandidates(self, keywords, nowords, candidates):
		if 'brave' in candidates:
			print 6666666666666666
		frequency = [[candidate, 0] for candidate in candidates]
		# firstly get the useful tweets
		tweets = self.getTargetTweets(keywords, nowords)
		for tweet in tweets:
			for candidate in frequency:
				if tweet.contains([candidate[0]], 'raw'):
					candidate[1]+=1
		result = sorted(frequency, key = lambda x:x[1], reverse = True)
		result = [x[0] for x in result]
		return result 

	def removeLessFrequentCandidates(self, candidates):
		frequency = [[candidate, 0] for candidate in candidates]
		for tweet in self.data:
			for candidate in frequency:
				if tweet.contains([candidate[0]], 'raw'):
					candidate[1]+=1
		finalCandidates = [x[0] for x in frequency if x[1]>25]
		return finalCandidates

	def removeSinger(self, candidates):
		candidates = [candidate for candidate in candidates if candidate not in famousSingers]
		return candidates

	def __str__(self):
		return self.data

	def __repr__(self):
		return self.data

def checkValidation(phrase):
	tokens = nltk.word_tokenize(phrase)
	# check whether it is too long
	if not tokens:
		return False

	# goldenglobes
	if 'goldenglobe' in ''.join(tokens):
		return False

	if len(tokens)>=7:
		return False

	# check if it is stopwords
	if len(tokens)==1:
		if tokens[0] in stopwords or tokens[0] in prepositions or tokens[0] in commonUselessSingleWords or tokens[0] in pronouns:
			return False
	elif len(tokens)==2 and ' '.join([tokens[0], tokens[1]]) in commonTwoWordsPhrase:
			return False
	elif len(tokens)>1:
		if tokens[0] in pronouns:
			return False


	return True

def trim(phrase):
	tokens = nltk.word_tokenize(phrase)
	if '@' in tokens or '#'in tokens:
		return ''

	tokens = [token.lower() for token in tokens if token.isalpha() and token.lower() not in sighwords]
	
	if not tokens:
		return ''
	if tokens[-1] in verbs:
		del tokens[-1]

	result = ' '.join(tokens)
	return result

def readCorpus(year):
	with open("gg%d.json" % (year)) as file_data:
		data = json.load(file_data)

	# for every data segment, the keys are as follows:
	# [u'text', u'timestamp_ms', u'user', u'id']
	allData = InfoBundle()
	for x in data:
		piece = InfoPiece(x)
		allData.insert(piece)
	print 'Finished loading data'
	return allData

def writeTweets(data):
	# drama movie
	dramaMovies = ['brave']
	for drama in dramaMovies:
		result = data.search([drama], 'raw')
		print drama+':'
		print result

	# comedy movie
	comedyMovies = [u'Les Mis\xc3rables']

	return


def main():
		'''This function calls your program. Typing "python gg_api.py"
		will run this function. Or, in the interpreter, import gg_api
		and then run gg_api.main(). This is the second thing the TA will
		run when grading. Do NOT change the name of this function or
		what it returns.'''
		
		femaleNameList = getNameDictionary('female') + getNameDictionary('female', '1')
		maleNameList = getNameDictionary('male') + getNameDictionary('male', '1')
		year = 2013
		allData = readCorpus(year)
		
		goodPatterns = [r'hop[(?:es?)(?:ing)](?:\sthat)?\s+(.*?)\sw[io]ns?',
										r'wants?\s+(.*?)\s+to\s+win', r'better\sthan\s(.*?)[.?!]',
										r'movie called (.*)[.!?]', r'[(?:film)(?:movie)] - (.*?) -']
		testPatterns = []
		#allData.getComedyMovieCandidates(goodPatterns, femaleNameList+maleNameList+additionalmaleNameList)
		#allData.getDramaMovieCandidates(goodPatterns, femaleNameList+maleNameList+additionalmaleNameList)
		allData.getCartoonMovieCandidates(goodPatterns, femaleNameList+maleNameList+additionalmaleNameList)
		#allData.getForeignMovieCandidates(goodPatterns, femaleNameList+maleNameList+additionalmaleNameList)
		#allData.getDramaActressCandidates(goodPatterns, femaleNameList)
		#allData.getDramaActorCandidates(goodPatterns, maleNameList)
		#writeTweets(allData)
		return

if __name__ == '__main__':
		main()
