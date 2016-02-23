# eecs337-team3-project1
Team 3's Project 1 code for Northwestern's EECS 337: Natural Language Processin

Team members: Kapil Garg, Noah Wolfenzon, Yifeng Zhang

In the file gg_api.py, we implement several functions to get the information related to golden globes which include: hosts, award names, nominees, winners, presenters and setiments. Brief Descripition are given in the follows about there functions:
get_hosts: 
// kapil

get_awards:
// noah 

get_nominees:
Firstly we will use some regular expression patterns to get some nominee candadites. After some filtering and text processing, impossible candidates are removed. Later, a dictionary of human name list or movie titles are used to check whether the nominees are of the right type. Finally, by counting the frequency of these words in award related tweets, candidates are sorted and the most five frequent candidates are regarded as nominees.

get_winner:
Get winner is only one step further. After geting the nominees, the most frequent one is within five candidates is the winner of that award.

get_presenters:
// noah fill this part

get_sentiments:
// kapil

Besides, when seeking for the nominees, we constructed a male namelist, female list and movie list of last five years by scraping the webpages. The name lists are from http://names.mongabay.com/ and the movie lists are gained from wikipedia page.

// other citations if exists

Finally, in the main look. we builds are simple text user interface by infinite loops.








