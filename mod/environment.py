import os
import string

class Environment:
    tutorial=True
    sassy=False
    wordlists = []
    blocklist = []
    addlist = []
    capsFreq = 0.5
    subsFreq = 0.5
    escape = '\\'
    symbolSet = string.punctuation
    wordlist_file = os.path.join("resources", "wordlists", "common-english-clean.txt")
    blocklist_file = os.path.join("resources", "blocklist.txt")
    addlist_file = os.path.join("resources", "addlist.txt")
