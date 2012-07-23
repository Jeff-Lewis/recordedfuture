import fileinput, base64

BASE64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

def b64encode(l):
    s = ""
    while l > 0:
        l, m = divmod(l, 64)
        s = BASE64_ALPHABET[m] + s
    return s

def b64decode(s):
    res = 0
    if s[0] == "A":
        return reduce(lambda a, b: 256*a + ord(b), base64.urlsafe_b64decode(s+"="), 0L)
    for c in s:
        res = 64*res + BASE64_ALPHABET.find(c)
    return res
    
def translate_id_to_str(i):
    try:
        i = int(i)
        i = b64encode(i)
    except:
        pass
    return i

def translate_id_to_int(i):
    if isinstance(i, str):
        try:
            i = int(i)
        except:
            i = b64decode(i)
    return i
        

def main():
    for l in fileinput.input():
        print b64decode(l)

if __name__ == "__main__":
    main()
