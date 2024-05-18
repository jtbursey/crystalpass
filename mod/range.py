import string

def validate_range(low, high = None, step = 1, single_digit : bool = True) -> bool:
    if step <= 0:
        return False

    if (type(low) != str or len(low) != 1) and type(low) != int:
        return False

    if type(low) == str and low not in string.ascii_lowercase:
        return False
    
    if single_digit and type(low) == int and (low < 0 or low > 9):
        return False

    if high != None:
        if (type(high) != str or len(high) != 1) and type(high) != int:
            return False
        if type(high) != type(low):
            return False
        if type(high) == int and high < low:
            return False
        if type(high) == str and ord(high) < ord(low):
            return False
        if type(high) == str and high not in string.ascii_lowercase:
            return False
        if single_digit and type(high) == int and (high < 0 or high > 9):
            return False

    return True

class Range:
    single_digit_only = False
    def __init__(self, l, h = None, s = 1, d = single_digit_only) -> None:
        if validate_range(l, h, s, d):
            self.low = l
            self.high = h
            self.step = s
        else:
            self.low = None
            self.high = None
            self.step = None

    def get(self):
        if self.low == None:
            return None
        if self.high == None:
            return [self.low]
        if type(self.low) == str:
            return [chr(c) for c in range(ord(self.low), ord(self.high) + 1, self.step)]
        return [i for i in range(self.low, self.high + 1, self.step)]
    
    def len(self) -> int:
        return len(self.get())

def parse_range(s : str, single_digit : bool = True) -> Range:
    if len(s) == 0:
        return None
    # expect a string in the form a-z or 0-9
    split = s.split('-')
    if len(split) > 2:
        return None

    split[0] = split[0].strip()
    if split[0].isdigit():
        split[0] = int(split[0])
    else:
        split[0] = split[0].lower()

    if len(split) == 2:
        split[1] = split[1].strip()
        if split[1].isdigit():
            split[1] = int(split[1])
        else:
            split[1] = split[1].lower()
        check = validate_range(split[0], split[1], single_digit=single_digit)
        if not check:
            return None
        return Range(split[0], split[1])
    else:
        check = validate_range(split[0], single_digit=single_digit)
        if not check:
            return None
        return Range(split[0])
