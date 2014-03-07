#!/usr/bin/python
import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import sys
import getopt
import math
import os.path
import shutil

TOKEN_FILES_DIR='dict_dir/'
NUM_FILES_TO_INDEX = 100

TOKENS_INVALID = ['.', '..']

def create_dict_dir():
  if not os.path.exists(TOKEN_FILES_DIR):
    os.makedirs(TOKEN_FILES_DIR)

def stem_and_normalize_tokens(token_list):
  stemmer = nltk.stem.porter.PorterStemmer()
  normalized_list = []
  for i in xrange(len(token_list)):
    token = stemmer.stem(token_list[i])
    if "/" in token:
      for t in token.split('/'):
        normalized_list.append(t)
    else:
      normalized_list.append(token)
  return [x for x in normalized_list if x]

def get_tokens_from_line(line):
  token_list = map(lambda x: x.lower(),filter(lambda word: word not in ',-.&()\"\'', [word for sent in sent_tokenize(line) for word in word_tokenize(sent)]))
  token_list = stem_and_normalize_tokens(token_list)
  return token_list

def write_doc_id_to_file(token, doc_id):
  token_file_path=TOKEN_FILES_DIR + token
  if not os.path.isfile(token_file_path):
    dict_token_writer = open(token_file_path, "w")
    dict_token_writer.write(doc_id)
  else:
    dict_token_reader = open(token_file_path, "r")
    list_of_doc_ids = dict_token_reader.readline().split()
    if doc_id not in list_of_doc_ids:
      dict_token_writer = open(token_file_path, "a")
      dict_token_writer.write(" " + doc_id)


def get_list_of_files_to_index():
  file_list = os.listdir(documents_dir)
  file_list.sort(key=int)
  # return file_list[0:NUM_FILES_TO_INDEX]
  return file_list

def get_list_of_token_files():
  file_list = os.listdir(TOKEN_FILES_DIR)
  return file_list

def insert_skip_pointers(l):
  l = l.split()
  if len(l) > 10:
    idx = 0
    skip_distance = int(math.floor(math.sqrt(len(l))))
    while idx < len(l):
      if idx + skip_distance >= len(l):
        l[idx] += ",-1"
      else:
        l[idx] += "," + l[idx + skip_distance]
      idx += skip_distance
  return ' '.join(l)

def append_all_files_to_dict():
  dict_file_writer = open(dict_file, "w")
  postings_file_writer = open(postings_file, "w")
  postings_file_writer.write(" ".join(get_list_of_files_to_index()) + "\n")
  token_file_list = get_list_of_token_files()
  for file_name in token_file_list:
    in_file = TOKEN_FILES_DIR + file_name
    with open(in_file) as f:
      file_pointer = postings_file_writer.tell()
      doc_ids = insert_skip_pointers(f.readline())
      postings_file_writer.write(doc_ids + "\n")
      dict_file_writer.write(file_name + " " + str(file_pointer) + "\n")

  shutil.rmtree(TOKEN_FILES_DIR)

def index_docs(documents_dir, dict_file, postings_file):
  create_dict_dir()
  indexer = {}
  file_list = get_list_of_files_to_index()
  for file_name in file_list:
    in_file = documents_dir + file_name
    with open(in_file) as f:
      for l in f.readlines():
        token_list = get_tokens_from_line(l)
        for token in token_list:
          if not token in TOKENS_INVALID:
            write_doc_id_to_file(token, file_name)

  append_all_files_to_dict()

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