#!/usr/bin/python
import sys
import getopt
import os
import re
import Queue
import string
import nltk

REGEX_STRING_ENCLOSED_BY_PARANTHESES = "(?<=\().*?(?=\))"
DELIMITER_OR = " OR "
DELIMITER_AND = " AND "
PREFIX_NOT = "NOT "
REGEX_PREFIX_NOT = "(?<=NOT ).*"
PREFIX_PARANTHESIS = "PARANTHESIS_"
REGEX_PREFIX_PARANTHESIS = "(?<=PARANTHESIS_).*"
POINTER_DOCUMENTS_ALL = 0
MAX_CACHE_SIZE=100000

def get_list_of_all_doc_ids():
  return get_doc_ids_from_postings_file_at_pointer(POINTER_DOCUMENTS_ALL)

def usage():
  print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

def parse_dictionary_file_entry(entry):
  file_entry_list_by_whitespace = entry.split()
  return file_entry_list_by_whitespace

def store_entry_in_dictionary(entry):
  """
  Stores dictionary in memory
  """
  term_pointer_list = parse_dictionary_file_entry(entry)
  term = term_pointer_list[0]
  file_pointer = term_pointer_list[1]
  dictionary[term] = file_pointer

def store_dictionary_in_memory_and_return_it(dict_file):
  dict_file_reader = open(dict_file, 'r')
  for token in dict_file_reader.readlines():
    store_entry_in_dictionary(token)
  dict_file_reader.close()
  return dictionary

def does_doc_id_contain_skip_pointer(doc_id):
  """
  Checks if a postings list term contains a skip pointer
  """
  return (',' in doc_id)

def get_doc_id_from_doc_id_and_skip_pointer(doc_id):
  doc_id_skip_pointer_list = doc_id.split(',')
  return doc_id_skip_pointer_list[0]

def get_doc_ids_from_postings_file_at_pointer(file_pointer):
  postings_file_reader = open(postings_file, "r")
  postings_file_read_position = postings_file_reader.seek(file_pointer)
  doc_ids = postings_file_reader.readline().strip().split()
  for i in range(0, len(doc_ids)):
    doc_id = doc_ids[i]
    if does_doc_id_contain_skip_pointer(doc_id):
      doc_ids[i] = get_doc_id_from_doc_id_and_skip_pointer(doc_id)
  postings_file_reader.close()
  return doc_ids

def write_to_output_file(line):
  """
  Writes result line to output file
  """
  prepend_char = "\n"
  if not os.path.isfile(output_file):
    output_writer = open(output_file, "w")
    prepend_char = ""
  else:
    output_writer = open(output_file, "a")
  output_writer.write(prepend_char + line)

def get_doc_ids_for_token(token):
  """
  Given a token, returns all doc_ids from the postings list
  """
  doc_ids = []
  if query in dictionary:
    postings_file_pointer_for_query_term = int(dictionary[query])
    doc_ids = get_doc_ids_from_postings_file_at_pointer(postings_file_pointer_for_query_term)
  return doc_ids

def merge_lists(p1, p2):
  answer = []
  idx1 = 0
  idx2 = 0
  while idx1 < len(p1) and idx2 < len(p2) :
    doc_id1 = (p1[idx1])
    doc_id2 = (p2[idx2])
    if doc_id1 == doc_id2:
      answer.append(doc_id1)
      idx1 += 1
      idx2 += 1
    elif int(doc_id1) < int(doc_id2):
      idx1 += 1
    else:
      idx2 += 1
  return answer

def union_lists(p1, p2):
  answer = []
  idx1 = 0
  idx2 = 0

  while idx1 < len(p1) and idx2 < len(p2) :
    doc_id1 = (p1[idx1])
    doc_id2 = (p2[idx2])
    if doc_id1 == doc_id2:
      answer.append(doc_id1)
      answer.append(doc_id2)
      idx1 += 1
      idx2 += 1
    elif doc_id1 < doc_id2:
      answer.append(doc_id1)
      idx1 += 1

    elif doc_id2 < doc_id1:
      answer.append(doc_id2)
      idx2 += 1
  return answer

def execute_and_operation(operands):
  assert len(operands) > 1
  list_results = perform_query(operands[0].strip())
  for i in range(1, len(operands)):
    list_results = merge_lists(list_results, perform_query(operands[i].strip()))
  return list_results

def execute_or_operation(operands):
  list_results = []
  for operand in operands:
    list_results = union_lists(list_results, perform_query(operand.strip()))
  return list_results

def execute_not_operation(operand):
  global all_docs
  list_results = []
  operand_query_results = set(perform_query(operand))
  list_results = [doc for doc in all_docs if doc not in operand_query_results]
  return list_results

def are_there_brackets_in_expression(expr):
  matches = re.findall(REGEX_STRING_ENCLOSED_BY_PARANTHESES, expr)
  if len(matches) > 0:
    return True

def get_substrings_enclosed_in_brackets(str):
  return re.findall(REGEX_STRING_ENCLOSED_BY_PARANTHESES, str)

def get_index_of_bracketed_query(query):
  matches = re.findall(REGEX_PREFIX_PARANTHESIS, query)
  return int(matches[0])

def get_expression_in_front_of_NOT(query):
  matches = re.findall(REGEX_PREFIX_NOT, query)
  assert len(matches) == 1
  return matches[0]

def perform_query(query):
  """
  Recursively evaluates query based on rank of precedence
  """
  global list_query_parantheses_results
  if are_there_brackets_in_expression(query):
    list_of_expressions_in_bracket = get_substrings_enclosed_in_brackets(query)
    for i in range(0, len(list_of_expressions_in_bracket)):
      expression = list_of_expressions_in_bracket[i]
      query = query.replace('(' + expression + ')', 'PARANTHESIS_' + str(i))
      list_query_parantheses_results.append(perform_query(expression.strip()))
    return perform_query(query)
  elif DELIMITER_OR in query:
    list_sub_expressions_separated_by_OR = query.split(DELIMITER_OR)
    return execute_or_operation(list_sub_expressions_separated_by_OR)
  elif DELIMITER_AND in query:
    list_sub_expressions_separated_by_AND = query.split(DELIMITER_AND)
    return execute_and_operation(list_sub_expressions_separated_by_AND)
  elif PREFIX_NOT in query:
    expression_to_be_negated = (get_expression_in_front_of_NOT(query)).strip()
    return execute_not_operation(expression_to_be_negated)
  elif PREFIX_PARANTHESIS in query:
    index_query_in_bracket_list = get_index_of_bracketed_query(query)
    return list_query_parantheses_results[index_query_in_bracket_list]
  elif stemmer.stem(string.lower(query)) in dictionary:
    postings_file_pointer_for_query_term = int(dictionary[stemmer.stem(string.lower(query))])
    if query not in cache:
      global current_cache_size
      if current_cache_size > MAX_CACHE_SIZE:
        del cache[cache.itervalues().next()]
        current_cache_size = current_cache_size - 1
      cache[query] = get_doc_ids_from_postings_file_at_pointer(postings_file_pointer_for_query_term)
      current_cache_size = current_cache_size + 1
    return cache[query]
  else:
    return []

def perform_queries():
  query_file_reader = open(query_file, 'r')
  postings_file_reader = open(postings_file, 'r')
  for query in query_file_reader.readlines():
    global list_query_parantheses_results
    list_query_parantheses_results = []
    query = query.strip()
    res = perform_query(query)
    write_to_output_file(" ".join(res))

dict_file = postings_file = query_file = output_file = None
try:
  opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError, err:
  usage()
  sys.exit(2)
for o, a in opts:
  if o == '-d':
    dict_file = a
  elif o == '-p':
    postings_file = a
  elif o == '-q':
    query_file = a
  elif o == '-o':
    output_file = a
  else:
    assert False, "unhandled option"
if query_file == None or dict_file == None or postings_file == None or output_file == None:
  usage()
  sys.exit(2)

dictionary = {}
cache = {}
current_cache_size = 0
list_query_parantheses_results = []
dictionary = store_dictionary_in_memory_and_return_it(dict_file)
stemmer = nltk.stem.porter.PorterStemmer()
all_docs = get_doc_ids_from_postings_file_at_pointer(POINTER_DOCUMENTS_ALL)
perform_queries()
