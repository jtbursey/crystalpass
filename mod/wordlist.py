from typing import List

def longest_length(words : List[str]) -> int:
    longest = 0
    for w in words:
        w = w.rstrip()
        if len(w) > longest:
            longest = len(w)
    return longest

def split_words(words : List[str]) -> List[List[str]]:
    wordlists = []
    for _ in range(longest_length(words)):
        wordlists.append([])
    for w in words:
        w = w.rstrip()
        wordlists[len(w)-1].append(w)
    return wordlists
