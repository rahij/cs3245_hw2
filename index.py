#!/usr/bin/python
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import sys
import getopt
import math
import os.path

def index_docs(documents_dir, dict_file, postings_file):
  stemmer = nltk.stem.porter.PorterStemmer()
  dict_file_writer = open(dict_file, "w")
  postings_file_writer = open(postings_file, "w")
  doc_id = 0;
  indexer = {}
  file_list = os.listdir(documents_dir)
  sorted(file_list, key = lambda x: int(x))
  for file_name in file_list:
    if doc_id > 300:
      break
    in_file = documents_dir+file_name
    with open(in_file) as f:
      for l in f.readlines():
        token_list = map(lambda x: x.lower(),filter(lambda word: word not in ',-', [word for sent in sent_tokenize(l) for word in word_tokenize(sent)]))
        for token in token_list:
          token = stemmer.stem(token)
          if token not in indexer:
            indexer[token] = []
          if int(file_name) not in indexer[token]:
            indexer[token].append(int(file_name))
    doc_id = doc_id + 1
  for token, doc_list in indexer.iteritems():
    current_position = postings_file_writer.tell()
    dict_file_writer.write(token + " " + str(current_position) + "\n")
    postings_file_writer.write(str(doc_list) + "\n")

def usage():
  print "usage: " + sys.argv[0] + " -i training-doc-directory -d out-file-for-dictionary -p output-file-for-postings-list"

documents_dir = dict_file = postings_file = None
try:
  opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError, err:
  usage()
  sys.exit(2)
for o, a in opts:
  if o == '-i':
    documents_dir = a
  elif o == '-d':
    dict_file = a
  elif o == '-p':
    postings_file = a
  else:
    assert False, "unhandled option"
if documents_dir == None or dict_file == None or postings_file == None:
  usage()
  sys.exit(2)

index_docs(documents_dir, dict_file, postings_file)