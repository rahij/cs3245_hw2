#to parse postings list: http://stackoverflow.com/a/1926757/1805980
#!/usr/bin/python
import sys
import getopt

def search_query():
  print "test"

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

