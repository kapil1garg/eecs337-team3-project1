# eecs337-team3-project1
Team 3's Project 1 code for Northwestern's EECS 337: Natural Language Processin

Team members: Kapil Garg, Noah Wolfenzon, Yifeng Zhang

In the file gg_api.py, we implement several functions to get the information related to golden globes which include: hosts, award names, nominees, winners, presenters and setiments. Brief descripition are given in the follows about there functions:
get_hosts: 
// kapil

get_awards:
The get awards functions uses regular expressions to account for the general structure of an award in the film industry. After
normalizing the tweets by lower casing them, it filters out the retweets. It then filters out tweets without the word best in order to
avoid over use of expensive regular expressions. The remaining tweets are matched and parsed with the general structure regular
expresion. Next, commonly used colloquial film related terms are switched in favor of standardized and official terms in order to ensure
we can recognize a match between all tweets that are focused on the same award. After extracting these and adding them to the dictionary of all awards, the most common awards are returned.

get_nominees:
Firstly we will use some regular expression patterns to get some nominee candadites. After some filtering and text processing, impossible candidates are removed. Later, a dictionary of human name list or movie titles are used to check whether the nominees are of the right type. Finally, by counting the frequency of these words in award related tweets, candidates are sorted and the most five frequent candidates are regarded as nominees.

get_winner:
Get winner is only one step further. After geting the nominees, the most frequent one is within five candidates is the winner of that award.

get_presenters:
The get presenter function uses a list of tweets that have only characters and free from stopwords. Case is preserved. The function then
utilizes verbs commonly used to describe somebody presenting an award (i.e. present, announce, introduce) to filter out tweets that are
most likely not refering to the presentation of the award. Next, the function uses a regular expression match to parse out words that are
name cased. To avoid false positives in the form of capitalized words that may also be a name, the function only uses matches that are
2-3 name cased words long. The first word is checked to ensure it is in a names corpus and the second word is checked against our results
from the get nominees function, as tweets that have the name of presenters often have the name of nominees and we do not want these false
positive. The "name" is then added to a presenter count dictionary for each word. The function returns a dictionary of all official
awards as keys and lists of 1-2 presenters as values. It the count of the second most common presenter name is less than half the count
of the first name, it is removed.

get_sentiments:
// kapil

Besides, when seeking for the nominees, we constructed a male namelist, female list and movie list of last five years by scraping the webpages. The name lists are from http://names.mongabay.com/ and the movie lists are gained from wikipedia page.

// other citations if exists
Python Libraries Imported:

from __future__ import division, 
import os.path, 
import collections, 
import operator, 
import pprint, 
import sys, 
import json, 
import re, 
import string, 
import copy, 
import math, 
import requests, 
import nltk, 
from nltk.corpus import names, stopwords, 
from nltk.tokenize import *, 
from lxml import html

Finally, in the main function, we build a simple text user interface by infinite loops.








