Email: a0091539@nus.edu.sg-a0075136@nus.edu.sg

1. Indexing:

After each token is normalized by stemming and case folding, we create a temporary directory to store the current doc_ids found for a token. Each file inside this directory is named after a token. After all the tokens are indexed in this manner, we then append the contents of all these files into the dictionary and postings files. This directory is then deleted.

The reason for this is to avoid storing the postings lists of all tokens in memory in order to keep updating the list.

2. Searching:

The query term is parsed in order of precedence of operations and is recursively evaluated. It stores the postings lists of the current doc_ids that it operates on and carries out the operations. The result is then written to the output file.

Resources:
Stackoverflow
docs.python.org