#to parse postings list: http://stackoverflow.com/a/1926757/1805980
#!/usr/bin/python
import sys
import getopt
import os
import re
import Queue

REGEX_STRING_ENCLOSED_BY_PARANTHESES = "(?<=\().*?(?=\))"
DELIMITER_OR = " OR "
DELIMITER_AND = " AND "
PREFIX_NOT = "NOT "
PREFIX_PARANTHESIS = "PARANTHESIS_"
REGEX_PREFIX_PARANTHESIS = "(?<=PARANTHESIS_).*"

list_query_parantheses_results = []

def usage():
  print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

def doesStringContainOnlyDigits(inputString):
  return all(char.isdigit() for char in inputString)

def parse_dictionary_file_entry(entry):
  file_entry_list_by_whitespace = entry.split()
  assert len(file_entry_list_by_whitespace) == 2
  assert doesStringContainOnlyDigits(file_entry_list_by_whitespace[1])
  return file_entry_list_by_whitespace

def store_entry_in_dictionary(entry):
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
    doc_ids[i] = int(doc_ids[i])
  postings_file_reader.close()
  print doc_ids
  return doc_ids

def write_to_output_file(line):
  prepend_char = "\n"
  if not os.path.isfile(output_file):
    output_writer = open(output_file, "w")
    prepend_char = ""
  else:
    output_writer = open(output_file, "a")
  output_writer.write(prepend_char + line)

def get_doc_ids_for_token(token):
  doc_ids = []
  if query in dictionary:
    postings_file_pointer_for_query_term = int(dictionary[query])
    doc_ids = get_doc_ids_from_postings_file_at_pointer(postings_file_pointer_for_query_term)
  return doc_ids

def execute_and_operation(operands):
  assert len(operands) > 1
  list_results = perform_query(operands[0].strip())
  for i in range(1, len(operands)):
    list_results = list(set(list_results) & set(perform_query(operands[i].strip())))
  list_results.sort()
  print list_results
  return list_results

def execute_or_operation(operands):
  list_results = []
  for operand in operands:
    list_results = list_results + perform_query(operand.strip())
  list_results = sorted(list(set(list_results)))
  print list_results
  return list_results

def execute_not_operation(parent_list, to_be_excluded_list):
  return [x for x in a if x not in b]

# def split_query_into_tokens(query):
#   query_tokens_list = re.split(' ', query)
#   for token in query_tokens_list:
#     if token.startswith('('):

#   print query_tokens_list

# def make_operation_queue_from_tokens_list(query_tokens_list):
#   if are_brackets_present_in_query_tokens

def are_there_brackets_in_expression(expr):
  matches = re.findall(REGEX_STRING_ENCLOSED_BY_PARANTHESES, expr)
  if len(matches) > 0:
    return True

# def get_binary_operation_queue(query):
#   if are_there_brackets_in_expression(query):
    
  # query_tokens_list = split_query_into_tokens(query)
  # operation_queue = make_operation_queue_from_tokens_list(query_tokens_list)

def get_substrings_enclosed_in_brackets(str):
  return re.findall(REGEX_STRING_ENCLOSED_BY_PARANTHESES, str)

def get_index_of_bracketed_query(query):
  matches = re.findall(REGEX_PREFIX_PARANTHESIS, query)
  assert len(matches) == 1
  assert doesStringContainOnlyDigits(matches[0])
  return int(matches[0])

def perform_query(query):
  print query
  if are_there_brackets_in_expression(query):
    list_of_expressions_in_bracket = get_substrings_enclosed_in_brackets(query)
    for i in range(0, len(list_of_expressions_in_bracket)):
      expression = list_of_expressions_in_bracket[i]
      query = query.replace('(' + expression + ')', 'PARANTHESIS_' + str(i))
      list_query_parantheses_results.append(perform_query(expression.strip()))
    perform_query(query)
  elif DELIMITER_OR in query:
    list_sub_expressions_separated_by_OR = query.split(DELIMITER_OR)
    return execute_or_operation(list_sub_expressions_separated_by_OR)
  elif DELIMITER_AND in query:
    list_sub_expressions_separated_by_AND = query.split(DELIMITER_AND)
    return execute_and_operation(list_sub_expressions_separated_by_AND)
  elif PREFIX_PARANTHESIS in query:
    index_query_in_bracket_list = get_index_of_bracketed_query(query)
    return list_query_parantheses_results[index_query_in_bracket_list]
  else:
    if query in dictionary:
      postings_file_pointer_for_query_term = int(dictionary[query])
      return get_doc_ids_from_postings_file_at_pointer(postings_file_pointer_for_query_term)
    else:
      raise Exception('Query ' + query + ' is not present in dictionary')

  # get_binary_operation_queue(query)

def perform_queries():
  query_file_reader = open(query_file, 'r')
  postings_file_reader = open(postings_file, 'r')
  for query in query_file_reader.readlines():
    list_query_parantheses_results = []
    query = query.strip()
    print perform_query(query)

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
dictionary = store_dictionary_in_memory_and_return_it(dict_file)
perform_queries()