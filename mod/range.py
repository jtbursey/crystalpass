def validate_range(low, high, step) -> bool:
    if step <= 0:
        return False

    if (type(low) != str or len(low) != 1) and type(low) != int:
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
            # checking for a-z and 0-9 will be done outside

    return True

class Range:
    def __init__(self, l, h = None, s = 1) -> None:
        if validate_range(l, h, s):
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
