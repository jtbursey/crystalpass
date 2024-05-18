import string
from enum import IntEnum
from typing import List, Tuple

from mod.range import Range
from mod.range import parse_range
import mod.common as common
import mod.entropy as entropy
from mod.environment import Environment as env

import mod.dialogue as dialogue

class Exp_Retval(IntEnum):
    EMPTY = 1
    OK = 0
    ERR = -1
    FAIL = -2
    INVALSYMBOL = -3
    INVALEXPR = -4
    INVALARG = -5
    AMBIG = -6

class Exp_Type(IntEnum):
    NONE = 0
    WORD = 1
    DIGIT = 2
    LETTER = 3
    SYMBOL = 4
    CHARACTER = 5
    RANDOM = 6
    NAMED = 7
    LITERAL = 8

class Arg_Type(IntEnum):
    AMBIG = -2
    INVALID = -1
    NONE = 0
    RANGE = 1
    INT = 2
    QUAD = 3
    BOOL = 4
    SET = 5
    STRING = 6

class Exp_Quad(IntEnum):
    FALSE = 0
    TRUE = 1
    BEGIN = 2
    END = 3

class Exp_None:
    pass

class Exp_Word:
    def __init__(self, l : Range = None, c : Exp_Quad = Exp_Quad.FALSE, s : bool = False) -> None:
        self.length = l
        self.caps = c
        self.subs = s

class Exp_Digit:
    def __init__(self, l : int, s : List[int] = None, r : Range = Range(0,9)) -> None:
        self.length = l
        self.set = s
        self.range = r

class Exp_Letter:
    def __init__(self, l : int = 1, s : str = None, r : Range = Range('a', 'z'), c : bool = False) -> None:
        self.length = l
        self.set = s
        self.range = r
        self.caps = c

class Exp_Symbol:
    def __init__(self, l : int = 1, s : str = env.symbolSet) -> None:
        self.length = l
        self.set = s

class Exp_Character:
    def __init__(self, l : Range = Range(1), s : str = env.symbolSet + string.ascii_lowercase) -> None:
        self.length = l
        self.set = s

class Exp_Random:
    def __init__(self, l : List[any]) -> None:
        # A list of other expressions
        self.list = l

class Exp_Named:
    def __init__(self, r : str, rev : bool = False, reg : bool = False) -> None:
        self.reference = r
        self.reverse = rev
        self.regen = reg

class Exp_LITERAL:
    def __init__(self, s : str = "") -> None:
        self.literal = s

class Expression:
    def __init__(self) -> None:
        self.type = Exp_Type.NONE
        self.exp = Exp_None()
        self.name = None
    
    def entropy(self):
        pass
    # TODO: json style output for saving patterns

# this seems like a better idea than globals
class Expression_Config:
    expression_names = [(Exp_Type.WORD, "word"), (Exp_Type.DIGIT, "digit"), (Exp_Type.DIGIT, "number"), (Exp_Type.LETTER, "letter"), (Exp_Type.SYMBOL, "symbol"), (Exp_Type.CHARACTER, "character"), (Exp_Type.RANDOM, "random"), (Exp_Type.NAMED, "named")]
    arg_names = ["length", "caps", "subs", "name", "regen", "reverse"]
    quad_map = [(Exp_Quad.TRUE, "true"), (Exp_Quad.FALSE, "false"), (Exp_Quad.BEGIN, "begin"), (Exp_Quad.END, "end")]
    bool_map = [(True, "true"), (False, "false")]
    escaped_chars = env.escape + ""

def longest_val_match(val : str, map) -> any:
    matches = [v for v in map if v[1].startswith(val.lower())]
    if len(matches) > 1:
        return (Exp_Retval.AMBIG, val)
    elif len(matches) == 0:
        return (Exp_Retval.INVALARG, val)
    return (Exp_Retval.OK, matches[0][0])

def longest_arg_match(arg : str) -> Tuple[Exp_Retval, str]:
    matches = [an for an in Expression_Config.arg_names if an.startswith(arg)]
    if len(matches) > 1:
        return (Exp_Retval.AMBIG, arg)
    elif len(matches) == 0:
        return (Exp_Retval.INVALARG, arg)
    return (Exp_Retval.OK, matches[0])

def longest_exp_substring(pattern : str) -> Tuple[Exp_Type, str]:
    best = (Exp_Type.NONE, "")
    for i in range(1, len(pattern)+1):
        for w in Expression_Config.expression_names:
            if w[1].startswith(pattern[1:i]) and i > len(best[1]):
                best = (w[0], pattern[0:i])
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
        if pattern[pos1] == ']' and pattern[pos1-1] != env.escape:
            par -= 1
        elif pattern[pos1] == '[' and pattern[pos1-1] != env.escape:
            par += 1
        pos1 += 1

    return (Exp_Retval.OK, pattern[0:pos1])

def get_next_exp_string(pattern : str) -> Tuple[Exp_Retval, str, str]:    
    if len(pattern) == 0:
        return (Exp_Retval.EMPTY, "", "")

    if pattern.startswith(env.escape):
        # dealing with possible expression
        if len(pattern) == 1:
            return (Exp_Retval.INVALSYMBOL, pattern, "")

        _, exp = longest_exp_substring(pattern)
        if len(exp) == 1:
            if len(pattern) > 0 and pattern[1] in Expression_Config.escaped_chars:
                # here we only return the escaped charater as a literal, later the literal will be identified by this
                return (Exp_Retval.OK, pattern[1], pattern[2:])
            return (Exp_Retval.INVALEXPR, pattern, "")
        
        rem = find_exp_parity(pattern[len(exp):])
        if rem[0] < 0:
            return rem
        rem = rem[1]
        return (Exp_Retval.OK, pattern[0:len(exp)+len(rem)], pattern[len(exp)+len(rem):])

    pos1 = common.find_first_of(pattern, env.escape)
    if pos1 == None:
        return (Exp_Retval.OK, pattern[0:], "")
    return (Exp_Retval.OK, pattern[0:pos1], pattern[pos1:])

def get_set(arg_list : List[str]) -> Tuple[Exp_Retval, List[str]]:
    # Don't flame me for this. I was really tired.
    s = []
    esc = False
    last = False
    first = True
    for a in arg_list:
        s1 = ""
        last = False
        if first and a.startswith('"'):
            first = False
            s1 += '"'
            a = a[1:]
        elif first and not a.startswith('"'):
            return (Exp_Retval.INVALARG, s)
        for i in range(len(a)):
            last = False
            if not esc and a[i] == env.escape:
                esc = True
                continue
            if not esc and a[i] == '"':
                s1 += a[i]
                s.append(s1)
                if i < len(a.rstrip())-1:
                    return (Exp_Retval.INVALARG, s)
                return (Exp_Retval.OK, s)
            if esc and a[i] == '"':
                last = True
            s1 += a[i]
            esc = False
        s.append(s1)
    if last:
        return (Exp_Retval.INVALARG, s)
    return (Exp_Retval.OK, s)

def get_next_arg(arg_list : List[str]) -> Tuple[Arg_Type, str, any, List[str]]:
    if len(arg_list) == 0 or len(arg_list[0]) == 0:
        return (Arg_Type.NONE, "", None, [])

    arg_list[0] = arg_list[0].lstrip()
    if arg_list[0][0] == '"':
        err, s = get_set(arg_list)
        rem = arg_list[len(s):]
        s = ','.join(s).rstrip()
        if err < 0:
            return (Arg_Type.INVALID, None, s, rem)

        s = ''.join(sorted(s[1:-1]))
        ns = ''.join(sorted(set(s)))
        if env.tutorial and ns != s:
            dialogue.warn(title="Invalid Set Argument", msg="Set arguments must have unique characters:\n"+s+"\n"+ns)
        if env.tutorial and len(s) == 0:
            dialogue.warn(title="Invalid Set Argument", msg="Set arguments must not be empty.")
        
        return (Arg_Type.SET, None, ns, rem)

    arg = arg_list[0].strip()
    rem = arg_list[1:]
    if arg.find('=') < 0:
        val = parse_range(arg, False)
        if val == None:
            return (Arg_Type.INVALID, None, arg, rem)
        return (Arg_Type.RANGE, None, val, rem)
    
    # name of arg determines the type
    arg = arg.split('=')
    if len(arg) < 2:
        return (Arg_Type.AMBIG, arg[0], arg[1:], rem)

    err, an = longest_arg_match(arg[0].strip())
    if err == Exp_Retval.AMBIG:
        return (Arg_Type.AMBIG, an, arg[1], rem)
    elif err < 0:
        return (Arg_Type.INVALID, an, arg[1], rem)

    arg[1] = arg[1].strip()
    if an == "length":
        val = parse_range(arg[1], False)
        if val == None:
            return (Arg_Type.INVALID, an, arg, rem)
        return (Arg_Type.RANGE, an, val, rem)
    elif an == "caps":
        err, val = longest_val_match(arg[1], Expression_Config.quad_map)
        if err < 0:
            return (Arg_Type.INVALID, an, arg[1], rem)
        return (Arg_Type.QUAD, an, val, rem)
    elif an == "subs" or an == "regen" or an == "reverse":
        err, val = longest_val_match(arg[1], Expression_Config.bool_map)
        if err < 0:
            return (Arg_Type.INVALID, an, arg[1], rem)
        return (Arg_Type.BOOL, an, val, rem)
    elif an == "name":
        if arg[1].isalnum():
            return (Arg_Type.STRING, an, arg[1], rem)

    return (Arg_Type.INVALID, None, None, rem)

def parse_exp_string(exp_str : str) -> Tuple[Exp_Retval, Expression]:
    exp = Expression()
    if len(exp_str) == 0:
        return (Exp_Retval.EMPTY, exp)

    if exp_str.startswith(env.escape):
        t, n = longest_exp_substring(exp_str)
        if t == Exp_Type.NONE:
            exp.type = Exp_Type.LITERAL
            exp.exp = Exp_LITERAL(exp_str)
            return (Exp_Retval.OK, exp)
        
        exp.type = t
        if t == Exp_Type.RANDOM:
            exp.exp = Exp_Random([])
            return (Exp_Retval.OK, exp)

        arg_str = exp_str[len(n):]
        if arg_str.startswith('['):
            arg_str = arg_str[1:]
        if arg_str.endswith(']'):
            arg_str = arg_str[:-1]
        args = arg_str.split(',')
        
        while len(args) != 0:
            at, an, val, args =  get_next_arg(args)
            if at == Arg_Type.AMBIG:
                return (Exp_Retval.INVALARG, exp)
            elif at < 0:
                return (Exp_Retval.INVALARG, exp)
            # match case for each expression type
            match at:
                case Arg_Type.RANGE:
                    dialogue.info(msg="Arg:\n"+str(at)+'\n'+str(an)+'\n'+str(val.get()))
                case Arg_Type.QUAD:
                    dialogue.info(msg="Arg:\n"+str(at)+'\n'+an+'\n'+str(val))
                case Arg_Type.BOOL:
                    dialogue.info(msg="Arg:\n"+str(at)+'\n'+an+'\n'+str(val))
                case Arg_Type.SET:
                    dialogue.info(msg="Arg:\n"+str(at)+'\n'+str(an)+'\n'+val)
                case Arg_Type.STRING:
                    dialogue.info(msg="Arg:\n"+str(at)+'\n'+an+'\n'+val)
                case Arg_Type.NONE:
                    dialogue.info(msg="Arg:\nNo argument given")
    else:
        exp.type = Exp_Type.LITERAL
        exp.exp = Exp_LITERAL(exp_str)
    
    return (Exp_Retval.OK, exp)

def parse(pattern : str) -> Tuple[Exp_Retval, List[Expression]]:
    while len(pattern) != 0:
        ret, expr, pattern = get_next_exp_string(pattern)
        if ret < 0:
            return (ret, expr)
        elif ret == Exp_Retval.EMPTY:
            break
        ret, exp = parse_exp_string(expr)
        if ret < 0:
            return (ret, expr)
    return (ret, [Expression()])

def validate(pattern : str) -> Exp_Retval:
    ret, _ = parse(pattern)
    return ret

def generate(pattern : str) -> Tuple[Exp_Retval, str]:
    ret, exprs = parse(pattern)
    # generate a string from the list of expressions

    return (ret, "someday")
