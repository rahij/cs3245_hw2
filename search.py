#to parse postings list: http://stackoverflow.com/a/1926757/1805980
#!/usr/bin/python
import sys
import getopt

def search_query():
  print "test"

def usage():
  print "usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

documents_dir = dict_file = postings_file = None
try:
  opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
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
if documents_dir == None or dict_file == None or postings_file == None:
  usage()
  sys.exit(2)
