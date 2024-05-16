from enum import IntEnum
from typing import List, Tuple

from mod.range import Range
import mod.common as common
import mod.entropy as entropy
import mod.options as options

import mod.dialogue as dialogue

class Exp_Retval(IntEnum):
    EMPTY = 1
    OK = 0
    ERR = -1
    FAIL = -2
    INVALSYMBOL = -3
    INVALEXPR = -4
    INVALARG = -5

class Exp_Type(IntEnum):
    NONE = 0
    WORD = 1
    DIGIT = 2
    LETTER = 3
    SYMBOL = 4
    CHARACTER = 5
    RANDOM = 6
    NAMED = 7
    EXACT = 8

class Exp_Quad(IntEnum):
    FALSE = 0
    TRUE = 1
    BEGIN = 2
    END = 3

class Exp_None:
    def __init__(self) -> None:
        pass

class Exp_Word:
    def __init__(self, l : Range, c : Exp_Quad, s : bool) -> None:
        self.length = l
        self.caps = c
        self.subs = s

class Exp_Digit:
    def __init__(self, l : int, s : List[int], r : Range) -> None:
        self.length = l
        self.set = s
        self.range = r

class Exp_Letter:
    def __init__(self, l : int, s : str, r : Range, c : bool) -> None:
        self.length = l
        self.set = s
        self.range = r
        self.caps = c

class Exp_Symbol:
    def __init__(self, l : int, s : str) -> None:
        self.length = l
        self.set = s

class Exp_Character:
    def __init__(self) -> None:
        pass

class Exp_Random:
    def __init__(self, l) -> None:
        # A list of other expressions
        self.list = l
        pass

class Exp_Named:
    def __init__(self, r, rev : bool, reg : bool) -> None:
        self.reference = r
        self.reverse = rev
        self.regen = reg

class Exp_Exact:
    def __init__(self, s : str) -> None:
        self.exact = s

class Expression:
    def __init__(self) -> None:
        self.type = Exp_Type.NONE
        self.exp = Exp_None()
        self.name = None
    
    def entropy(self):
        pass
    # TODO: json style output for saving patterns

expression_names = ["word", "digit", "number", "letter", "symbol", "character", "random", "named"]
escaped_chars = "\\"

def longest_exp_substring(pattern : str) -> str:
    global expression_names
    best = ""
    for i in range(1, len(pattern)+1):
        for w in expression_names:
            if w.startswith(pattern[1:i]) and i > len(best):
                best = pattern[0:i]
    return best

def find_exp_parity(pattern : str, l = '[', r = ']') -> Tuple[Exp_Retval, str]:
    if len(pattern) == 0 or pattern[0] != l:
        return (Exp_Retval.OK, "")
    
    pos1 = 1
    par = 1
    while par != 0:
        pos2 = common.find_first_of(pattern[pos1:], "[]")
        if pos2 == None:
            return (Exp_Retval.INVALARG, pattern)
        pos1 += pos2
        if pattern[pos1] == ']' and pattern[pos1-1] != '\\':
            par -= 1
        elif pattern[pos1] == '[' and pattern[pos1-1] != '\\':
            par += 1
        pos1 += 1

    return (Exp_Retval.OK, pattern[0:pos1])

def get_next_exp_string(pattern : str) -> Tuple[Exp_Retval, str, str]:
    global expression_names, escaped_chars
    
    if len(pattern) == 0:
        return (Exp_Retval.EMPTY, "", "")

    if pattern.startswith("\\"):
        # dealing with possible expression
        if len(pattern) == 1:
            return (Exp_Retval.INVALSYMBOL, pattern, "")

        exp = longest_exp_substring(pattern)
        if len(exp) == 1:
            if len(pattern) > 0 and pattern[1] in escaped_chars:
                return (Exp_Retval.OK, pattern[1], pattern[2:])
            return (Exp_Retval.INVALEXPR, pattern, "")
        rem = find_exp_parity(pattern[len(exp):])
        if rem[0] < 0:
            return rem
        rem = rem[1]
        return (Exp_Retval.OK, pattern[0:len(exp)+len(rem)], pattern[len(exp)+len(rem):])

    pos1 = common.find_first_of(pattern, "\\")
    if pos1 == None:
        return (Exp_Retval.OK, pattern[0:], "")
    return (Exp_Retval.OK, pattern[0:pos1], pattern[pos1:])

def parse(pattern : str) -> Tuple[Exp_Retval, List[Expression]]:
    while pattern != "":
        ret, expr, pattern = get_next_exp_string(pattern)
        # parse the expression string into a struct
        break
    return (Exp_Retval.FAIL, [Expression()])

def validate(pattern : str) -> Exp_Retval:
    ret, _ = parse(pattern)
    return ret

def generate(pattern : str) -> Tuple[Exp_Retval, str]:
    # parse the pattern -> get array of expressions
    # generate a string from the list of expressions
    s = ""
    while pattern != "":
        ret, expr, pattern = get_next_exp_string(pattern)
        if ret >= 0:
            s += " " + expr
        else:
            return (ret, expr)

    return (ret, s)
    #get_next_exp_string(pattern)[0:2]