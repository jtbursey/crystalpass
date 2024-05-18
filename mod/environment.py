import os
import string

class Environment:
    tutorial=True
    wordlists = []
    blocklist = []
    addlist = []
    capsFreq = 0.2
    escape = '\\'
    symbolSet = string.punctuation
    wordlist_file = os.path.join("resources", "common-english-clean.txt")
    blocklist_file = os.path.join("resources", "blocklist.txt")
    addlist_file = os.path.join("resources", "addlist.txt")
