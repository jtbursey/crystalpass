import string
import secrets
import math
from enum import IntEnum
from typing import List, Tuple

from mod.range import Range
from mod.range import parse_range
import mod.common as common
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
    EXTRAARG = -7
    NOARG = -8

class Exp_Type(IntEnum):
    NONE = 0
    WORD = 1
    DIGIT = 2
    LETTER = 3
    SYMBOL = 4
    CHARACTER = 5
    NAMED = 6
    LITERAL = 7

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

class Quad(IntEnum):
    FALSE = 0
    TRUE = 1
    BEGIN = 2
    END = 3

class Names:
    map = {}
    generated = {}

class Exp_None:
    def entropy(self) -> float:
        return 0.0

    def generate(self) -> str:
        return ""

class Exp_Word:
    def __init__(self, l : Range = None, c : Quad = Quad.FALSE, s : bool = False) -> None:
        self.length = l
        self.caps = c
        self.subs = s
    
    def get_wl(self) -> List[str]:
        wl = []
        if self.length == None:
            for l in env.wordlists:
                if len(l) > 0:
                    wl += l
        else:
            for x in self.length.get():
                wl += env.wordlists[x-1]
        return wl

    def entropy(self) -> float:
        ent = len(self.get_wl())
        if ent == 0:
            return 0
        if self.caps == Quad.TRUE:
            ent *= 2**(float(sum(self.length.get()))/float(len(self.length.get())))
        return math.log(ent, 2)

    def generate(self) -> str:
        wl = self.get_wl()
        if len(wl) == 0:
            return ""
        word = secrets.choice(wl)
        if self.caps == Quad.TRUE:
            newword = ""
            for l in word:
                if secrets.SystemRandom().random() < env.capsFreq:
                    newword += l.upper()
                else:
                    newword += l
            word = newword
        elif self.caps == Quad.BEGIN:
            word = word[0].upper() + word[1:]
        elif self.caps == Quad.END:
            word = word[:-1] + word[-1].upper()
        
        if self.subs:
            dialogue.info(msg="Subs is not implemented yet")
        return word

class Exp_Digit:
    def __init__(self, l : Range = Range(1), s : List[int] = None) -> None:
        self.length = l
        self.set = s
    
    def entropy(self) -> float:
        ent = float(len(self.set)**(float(sum(self.length.get()))/float(len(self.length.get()))))
        if ent <= 0:
            ent = 1.0
        return math.log(ent, 2)

    def generate(self) -> str:
        digit = ""
        set = []
        if self.set != None:
            set = list(self.set)
        
        length = secrets.choice(self.length.get())
        for _ in range(length):
            digit += secrets.choice(set)
        return digit

class Exp_Letter:
    def __init__(self, l : Range = Range(1), s : str = None, c : bool = False) -> None:
        self.length = l
        self.set = s
        self.caps = c
    
    def entropy(self) -> float:
        num = len(self.set)
        if self.caps:
            num *= 2
        ent = float(num**(float(sum(self.length.get()))/float(len(self.length.get()))))
        if ent <= 0:
            ent = 1.0
        return math.log(ent, 2)

    def generate(self) -> str:
        chars = ""
        set = []
        if self.set != None:
            set = list(self.set)
        
        length = secrets.choice(self.length.get())
        for _ in range(length):
            chars += secrets.choice(set)
        
        newchars = ""
        if self.caps:
            for c in chars:
                if secrets.SystemRandom().random() < env.capsFreq:
                    newchars += c.upper()
                else:
                    newchars += c
            chars = newchars

        return chars

class Exp_Symbol:
    def __init__(self, l : Range = Range(1), s : str = env.symbolSet) -> None:
        self.length = l
        self.set = s
    
    def entropy(self) -> float:
        ent = float(len(self.set)**(float(sum(self.length.get()))/float(len(self.length.get()))))
        if ent <= 0:
            ent = 1.0
        return math.log(ent, 2)

    def generate(self) -> str:
        syms = ""
        set = []
        if self.set != None:
            set = list(self.set)
        
        length = secrets.choice(self.length.get())
        for _ in range(length):
            syms += secrets.choice(set)
        return syms

class Exp_Character:
    def __init__(self, l : Range = Range(1), s : str = env.symbolSet + string.ascii_letters + string.digits) -> None:
        self.length = l
        self.set = s
    
    def entropy(self) -> float:
        ent = float(len(self.set)**(float(sum(self.length.get()))/float(len(self.length.get()))))
        if ent <= 0:
            ent = 1.0
        return math.log(ent, 2)

    def generate(self) -> str:
        chars = ""
        set = []
        if self.set != None:
            set = list(self.set)
        
        length = secrets.choice(self.length.get())
        for _ in range(length):
            chars += secrets.choice(set)

        return chars

class Exp_Named:
    def __init__(self, n : str, rev : bool = False, reg : bool = False) -> None:
        self.name = n
        self.reverse = rev
        self.regen = reg
    
    def entropy(self) -> float:
        if self.regen:
            return Names.map[self.name].entropy()
        return 0.0

    def generate(self) -> str:
        gen = ""
        if self.regen:
            if self.name in Names.map:
                gen = Names.map[self.name].generate()
            else:
                dialogue.err(title="Unknown Named Reference", msg=self.name + " does not exist.")
                return None
        else:
            if self.name in Names.generated:
                gen = Names.generated[self.name]
            else:
                dialogue.err(title="Unknown Named Reference", msg=self.name + " has not been generated yet. The referenced expression must come first.")
                return None
        
        if self.reverse:
            gen = gen[::-1]
        
        return gen


class Exp_Literal:
    def __init__(self, s : str = "") -> None:
        self.literal = s
    
    def entropy(self) -> float:
        return 0.0

    def generate(self) -> str:
        return self.literal

class Expression:
    def __init__(self) -> None:
        self.type = Exp_Type.NONE
        self.exp = Exp_None()
        self.name = None
    
    def entropy(self) -> float:
        return self.exp.entropy()

    def generate(self) -> str:
        return self.exp.generate()
    # TODO: json style output for saving patterns

# this seems like a better idea than globals
class Expression_Config:
    expression_names = [(Exp_Type.WORD, "word"), (Exp_Type.DIGIT, "digit"), (Exp_Type.LETTER, "letter"), (Exp_Type.SYMBOL, "symbol"), (Exp_Type.CHARACTER, "character"), (Exp_Type.NAMED, "named")]
    arg_names = ["length", "caps", "subs", "name", "regen", "reverse"]
    quad_map = [(Quad.TRUE, "true"), (Quad.FALSE, "false"), (Quad.BEGIN, "begin"), (Quad.END, "end")]
    bool_map = [(True, "true"), (False, "false")]
    quad_dict = {Quad.TRUE : "True", Quad.FALSE : "False", Quad.BEGIN : "Begin", Quad.END : "End"}
    escaped_chars = env.escape + "[]\""

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
    if pattern == env.escape:
        return (Exp_Type.NONE, "")

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

def escape(s : str) -> str:
    new = ""
    for c in s:
        if c == env.escape:
            continue
        if c in Expression_Config.escaped_chars:
            new += "\\"+c
        else:
            new += c
    return new

def get_next_exp_string(pattern : str) -> Tuple[Exp_Retval, str, str]:
    if len(pattern) == 0:
        return (Exp_Retval.EMPTY, "", "")

    if pattern.startswith(env.escape):
        # dealing with possible expression
        if len(pattern) == 1:
            return (Exp_Retval.INVALSYMBOL, pattern, "")

        _, exp = longest_exp_substring(pattern)
        if len(exp) == 1:
            if len(pattern) > 1 and pattern[1] in env.escape:
                # here we only return the escaped charater as a literal, later the literal will be identified by this
                return (Exp_Retval.OK, pattern[1], pattern[2:])
            return (Exp_Retval.INVALEXPR, exp, "")
        
        rem = find_exp_parity(pattern[len(exp):])
        if rem[0] < 0:
            return (rem[0], rem[1], pattern[len(exp)+len(rem):])
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

def get_next_arg(arg_list : List[str], quiet : bool = False) -> Tuple[Arg_Type, str, any, List[str]]:
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
        if env.tutorial and ns != s and not quiet:
            dialogue.warn(title="Invalid Set Argument", msg="Set arguments must have unique characters:\n"+s+"\n"+ns)
        if env.tutorial and len(s) == 0 and not quiet:
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
        return (Arg_Type.AMBIG, arg[0], '='.join(arg), rem)

    err, an = longest_arg_match(arg[0].strip())
    if err == Exp_Retval.AMBIG:
        return (Arg_Type.AMBIG, an, arg[0], rem)
    elif err < 0:
        return (Arg_Type.INVALID, an, arg[0], rem)

    arg[1] = arg[1].strip()
    if an == "length":
        val = parse_range(arg[1], False)
        if val == None:
            return (Arg_Type.INVALID, an, '='.join(arg), rem)
        return (Arg_Type.RANGE, an, val, rem)
    elif an == "caps":
        err, val = longest_val_match(arg[1], Expression_Config.quad_map)
        if err < 0:
            return (Arg_Type.INVALID, an, '='.join(arg), rem)
        return (Arg_Type.QUAD, an, val, rem)
    elif an == "subs" or an == "regen" or an == "reverse":
        err, val = longest_val_match(arg[1], Expression_Config.bool_map)
        if err < 0:
            return (Arg_Type.INVALID, an, '='.join(arg), rem)
        return (Arg_Type.BOOL, an, val, rem)
    elif an == "name":
        if arg[1].isalnum():
            return (Arg_Type.STRING, an, arg[1], rem)

    return (Arg_Type.INVALID, None, '='.join(arg), rem)

def parse_exp_string(exp_str : str, quiet : bool = False) -> Tuple[Exp_Retval, Expression]:
    exp = Expression()
    if len(exp_str) == 0:
        return (Exp_Retval.EMPTY, exp)

    if exp_str.startswith(env.escape):
        t, n = longest_exp_substring(exp_str)
        if t == Exp_Type.NONE:
            exp.type = Exp_Type.LITERAL
            exp.exp = Exp_Literal(exp_str)
            return (Exp_Retval.OK, exp)
        
        exp.type = t

        arg_str = exp_str[len(n):]
        if arg_str.startswith('['):
            arg_str = arg_str[1:]
        if arg_str.endswith(']'):
            arg_str = arg_str[:-1]
        args = arg_str.split(',')
        
        length = caps = subs = set = None
        name = reverse =  regen = None
        dup = None

        while len(args) > 0 and (len(args) != 1 or len(args[0]) != 0):
            at, an, val, args =  get_next_arg(args, quiet)
            if at == Arg_Type.AMBIG:
                return (Exp_Retval.AMBIG, val)
            elif at < 0:
                return (Exp_Retval.INVALARG, val)
        
            match an:
                case "length":
                    if length == None:
                        length = val
                    else:
                        dup = "length"
                case "caps":
                    if caps == None:
                        caps = val
                    else:
                        dup = "caps value"
                case "subs":
                    if subs == None:
                        subs = val
                    else:
                        dup = "subs value"
                case "name":
                    if name == None:
                        name = val
                    else:
                        dup = "name"
                case "reverse":
                    if reverse == None:
                        reverse = val
                    else:
                        dup = "reverse value"
                case "regen":
                    if regen == None:
                        regen = val
                    else:
                        dup = "regen value"
                case None:
                    if at == Arg_Type.SET:
                        if set == None:
                            set = val
                        else:
                            dup = "set"
                    elif at == Arg_Type.RANGE:
                        if set == None:
                            set = ''.join([str(x) for x in val.get()])
                        else:
                            dup = "range"
                case _:
                    return (Exp_Retval.INVALARG, an)

            if dup != None:
                if not quiet and env.tutorial:
                    dialogue.warn(title="Duplicate Argument", msg="A duplicate "+dup+" was provided. Ignoring.")
                dup = None
        
        if name != None:
            exp.name = name

        match t:
            case Exp_Type.WORD:
                if length == None:
                    length = Range(3, len(env.wordlists))
                if caps == None:
                    caps = Quad.FALSE
                if subs == None:
                    subs = False
                if set != None or reverse != None or regen != None:
                    return (Exp_Retval.EXTRAARG, str([set, reverse, regen]))
                exp.exp = Exp_Word(length, caps, subs)
                if exp.name != None:
                    Names.map[exp.name] = exp
                return (Exp_Retval.OK, exp)
            case Exp_Type.DIGIT:
                if length == None:
                    length = Range(1)
                if set == None:
                    set = ''.join([str(x) for x in Range(0, 9).get()])
                if caps != None or subs != None or reverse != None or regen != None:
                    return (Exp_Retval.EXTRAARG, str([caps, subs, reverse, regen]))
                if not all(x in string.digits for x in set):
                    return (Exp_Retval.INVALARG, set)
                exp.exp = Exp_Digit(length, set)
                if exp.name != None:
                    Names.map[exp.name] = exp
                return (Exp_Retval.OK, exp)
            case Exp_Type.LETTER:
                if length == None:
                    length = Range(1)
                if set == None:
                    set = string.ascii_lowercase
                if caps == None:
                    caps = False
                elif caps in [Quad.BEGIN, Quad.END]:
                    if not quiet and env.tutorial:
                        dialogue.warn(title="Invalid Caps Value", msg="Caps value for a letter should be true or false. Using true.")
                    caps = False
                if subs != None or reverse != None or regen != None:
                    return (Exp_Retval.EXTRAARG, str([subs, reverse, regen]))
                if not all(x in string.ascii_letters for x in set):
                    return (Exp_Retval.INVALARG, set)
                exp.exp = Exp_Letter(length, set, caps)
                if exp.name != None:
                    Names.map[exp.name] = exp
                return (Exp_Retval.OK, exp)
            case Exp_Type.SYMBOL:
                if length == None:
                    length = Range(1)
                if set == None:
                    set = env.symbolSet
                if caps != None or subs != None or reverse != None or regen != None:
                    return (Exp_Retval.EXTRAARG, str([caps, subs, reverse, regen]))
                if not all(x in string.punctuation for x in set):
                    return (Exp_Retval.INVALARG, set)
                exp.exp = Exp_Symbol(length, set)
                if exp.name != None:
                    Names.map[exp.name] = exp
                return (Exp_Retval.OK, exp)
            case Exp_Type.CHARACTER:
                if length == None:
                    length = Range(1)
                if set == None:
                    set = env.symbolSet + string.ascii_letters + string.digits
                if caps != None or subs != None or reverse != None or regen != None:
                    return (Exp_Retval.EXTRAARG, str([caps, subs, reverse, regen]))
                if not all(x in string.punctuation + string.ascii_letters + string.digits for x in set):
                    return (Exp_Retval.INVALARG, set)
                exp.exp = Exp_Character(length, set)
                if exp.name != None:
                    Names.map[exp.name] = exp
                return (Exp_Retval.OK, exp)
            case Exp_Type.NAMED:
                exp.name = None
                if name == None:
                    return (Exp_Retval.NOARG, n + "[name=?]")
                if reverse == None:
                    reverse = False
                if regen == None:
                    regen = False
                if length != None or set != None or caps != None or subs != None:
                    return (Exp_Retval.EXTRAARG, str([length, set, caps, subs]))
                exp.exp = Exp_Named(name, reverse, regen)
                return (Exp_Retval.OK, exp)
            case _:
                return (Exp_Retval.INVALEXPR, n)

    else:
        exp.type = Exp_Type.LITERAL
        exp.exp = Exp_Literal(exp_str)
    
    return (Exp_Retval.OK, exp)

def do_parse(pattern : str, index : int = 0, quiet : bool = False) -> Tuple[Exp_Retval, List[Expression], Exp_Type]:
    elist = []
    t = Exp_Type.NONE
    if index >= len(pattern):
        index = len(pattern)-1
    while len(pattern) != 0:
        ret, expr, pattern = get_next_exp_string(pattern)
        if ret < 0:
            return (ret, expr, t)
        elif ret == Exp_Retval.EMPTY:
            break
        ret, exp = parse_exp_string(expr, quiet)
        if ret < 0:
            return (ret, exp, t)
        if index <= len(expr) and t == Exp_Type.NONE:
            t = exp.type
        else:
            index -= len(expr)
        elist.append(exp)
    if t == Exp_Type.NONE:
        t = elist[-1].type
    return (ret, elist, t)

def parse(pattern : str, quiet : bool = False) -> Tuple[Exp_Retval, List[Expression]]:
    err, l, _ = do_parse(pattern, quiet)
    return (err, l)

def validate(pattern : str) -> Exp_Retval:
    ret, _ = parse(pattern, True)
    return ret

def generate(pattern : str) -> Tuple[Exp_Retval, str]:
    ret, exprs = parse(pattern)
    if ret < 0:
        return (ret, exprs)

    password = ""
    for e in exprs:
        gen = e.generate()
        if gen == None:
            return (Exp_Retval.ERR, "Generation Error")
        if e.name != None:
            Names.generated[e.name] = gen
        password += gen
    Names.generated.clear()
    Names.map.clear()
    return (ret, password)

def handle_err(err : Exp_Retval, txt : str):
    if err == Exp_Retval.INVALARG:
        dialogue.err(title="Invalid Argument", msg="Invalid argument:\n"+txt)
    elif err == Exp_Retval.INVALEXPR:
        dialogue.err(title="Invalid Expression", msg="Invalid expression:\n"+txt)
    elif err == Exp_Retval.INVALSYMBOL:
        dialogue.err(title="Invalid Symbol", msg="Invalid symbol:\n"+txt)
    elif err == Exp_Retval.AMBIG:
        dialogue.err(title="Ambiguous Expression", msg="Ambiguous expression:\n"+txt)
    elif err == Exp_Retval.EXTRAARG:
        dialogue.err(title="Extra Argument", msg="Extra argument:\n"+txt)
    elif err == Exp_Retval.NOARG:
        dialogue.err(title="Missing Argument", msg="Missing argument:\n"+txt)
    elif int(err) < 0:
        dialogue.err(title="Invalid Pattern", msg="Failed to parse pattern:\n"+txt)

def get_explanation(exprs : List[Expression]) -> List[str]:
    lines = []
    for e in exprs:
        match e.type:
            case Exp_Type.WORD:
                if e.exp.length == None:
                    l = "Any"
                else:
                    l = str(e.exp.length.get())
                lines += ["Expression Type: Word",
                          "   Possible word lengths:   " + l,
                          "   Use Capitals:            " + Expression_Config.quad_dict[e.exp.caps],
                          "   Use ASCII Substitutions: " + str(e.exp.subs)
                         ]
            case Exp_Type.DIGIT:
                lines += ["Expression Type: Digit",
                          "   Possible lengths: " + str(e.exp.length.get()),
                          "   Possible digits:  " + e.exp.set
                         ]
            case Exp_Type.LETTER:
                lines += ["Expression Type: Letter",
                          "   Possible lengths: " + str(e.exp.length.get()),
                          "   Possible letters: " + e.exp.set,
                          "   Use caps: " + str(e.exp.caps)
                         ]
            case Exp_Type.SYMBOL:
                lines += ["Expression Type: Symbol",
                          "   Possible lengths: " + str(e.exp.length.get()),
                          "   Possible symbols: " + e.exp.set
                         ]
            case Exp_Type.CHARACTER:
                lines += ["Expression Type: Character",
                          "   Possible lengths: " + str(e.exp.length.get()),
                          "   Possible symbols: " + e.exp.set
                         ]
            case Exp_Type.NAMED:
                lines += ["Expression Type: Named Reference",
                          "   Reference:             " + e.exp.name,
                          "   Reverse expression:    " + str(e.exp.reverse),
                          "   Regenerate expression: " + str(e.exp.regen)
                         ]
            case Exp_Type.LITERAL:
                lines += ["Expression Type: Literal",
                          "   Value: " + e.exp.literal
                         ]
        if e.name != None:
            lines += ["   Expression Name: " + e.name]
        lines += [""]
    return lines
