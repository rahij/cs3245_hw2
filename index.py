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

def create_dict_dir():
  if not os.path.exists(TOKEN_FILES_DIR):
    os.makedirs(TOKEN_FILES_DIR)

def get_tokens_from_line(line):
  stemmer = nltk.stem.porter.PorterStemmer()
  token_list = map(lambda x: x.lower(),filter(lambda word: word not in ',-.&\"\'', [word for sent in sent_tokenize(line) for word in word_tokenize(sent)]))
  for token in token_list:
    if "/" in token:
      token_list.remove(token)
      token_list.append(token.split('/')[0])
      token_list.append(token.split('/')[1])
    token = stemmer.stem(token)
  return token_list

def write_doc_id_to_file(token, doc_id):
  token_file_path=TOKEN_FILES_DIR + token
  print token_file_path + "\n"
  prepend_char = ""
  if not os.path.isfile(token_file_path):
    dict_token_writer = open(token_file_path, "w")
  else:
    dict_token_writer = open(token_file_path, "a")
    prepend_char = " "

  dict_token_writer.write(prepend_char + doc_id)


def get_list_of_files_to_index():
  file_list = os.listdir(documents_dir)[0:NUM_FILES_TO_INDEX]
  return file_list

def get_list_of_token_files():
  file_list = os.listdir(TOKEN_FILES_DIR)
  return file_list

def sort_line(l):
  return l

def append_all_files_to_dict():
  dict_file_writer = open(dict_file, "w")
  postings_file_writer = open(postings_file, "w")
  token_file_list = get_list_of_token_files()
  for file_name in token_file_list:
    in_file = TOKEN_FILES_DIR + file_name
    with open(in_file) as f:
      file_pointer = postings_file_writer.tell()
      doc_ids = sort_line(f.readline())
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
          write_doc_id_to_file(token, file_name)

  append_all_files_to_dict()
          # if token not in indexer:
          #   indexer[token] = []
          # if int(file_name) not in indexer[token]:
          #   indexer[token].append(int(file_name))
  # for token, doc_list in indexer.iteritems():
  #   current_position = postings_file_writer.tell()
  #   dict_file_writer.write(token + " " + str(current_position) + "\n")
  #   postings_file_writer.write(str(doc_list) + "\n")

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