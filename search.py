#to parse postings list: http://stackoverflow.com/a/1926757/1805980
#!/usr/bin/python
import sys
import getopt

def usage():
  print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

def doesStringContainOnlyDigits(inputString):
    return all(char.isdigit() for char in inputString)

def parse_dictionary_file_entry(entry):
  file_entry_list_by_whitespace = entry.split()
  assert len(file_entry_list_by_whitespace) == 2
  assert doesStringContainOnlyDigits(file_entry_list_by_whitespace[1])
  return file_entry_list_by_whitespace

def store_entry_in_dictionary(entry, dictionary):
  term_pointer_list = parse_dictionary_file_entry(entry)
  term = term_pointer_list[0]
  file_pointer = term_pointer_list[1]
  dictionary[term] = file_pointer

def store_dictionary_in_memory_and_return_it(dict_file_path):
  dict_file = open(dict_file_path, 'r')
  dictionary = {}
  for dict_entry in dict_file:
    store_entry_in_dictionary(dict_entry, dictionary)
  print dictionary
  return dictionary

def get_doc_ids_from_postings_file_at_pointer(postings_file, file_pointer):
  postings_file_read_position = postings_file.seek(file_pointer)
  return postings_file.readline()

def perform_query(query, dictionary, postings_file):
  if query in dictionary:
    postings_file_pointer_for_query_term = int(dictionary[query])
    print postings_file_pointer_for_query_term
    return get_doc_ids_from_postings_file_at_pointer(postings_file, postings_file_pointer_for_query_term)
  else:
    raise('Query term ' + query + ' not present in dictionary')

def perform_queries(query_file_path, dictionary, postings_file_path):
  query_file = open(query_file_path, 'r')
  postings_file = open(postings_file_path, 'r')
  for query in query_file:
    print perform_query(query, dictionary, postings_file)

if __name__ == "__main__":
  dict_file = postings_file = query_file = output_file = None
  try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o')
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
  dictionary = store_dictionary_in_memory_and_return_it(dict_file)
  perform_queries(query_file, dictionary, postings_file)

# def get_documents_for_query(query_string):
