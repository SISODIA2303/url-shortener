#evrery time someone shortens a URL, this function converts it into a code
CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" #string of 63 characters. at index 0 = 0, index 10 = a, & index 36 = A

def encode(num:int)->str: #takes a database id like 125 and returns a short code like 1z
    if num==0:
        return CHARS[0] #special case if ID is 0, just return '0'.
    result=[] #collect characters one by one

    while num>0: #keep going until nothing left to convert
        remainder=num%62 #gives remainder like 125%62 = 1
        result.append(CHARS[remainder]) #use that remainder as an index to pick a character from CHARS
        num=num//62 #integer division, 125//62 = 2. now repeat the same steps with 2
    return "".join(reversed(result)) #we built the string backwards, so we reverse it before returning

def decode(code:str)->int: #reverse process. Converst 1z into 125. Useful for debugging
    num=0
    for char in code:
        num=num*62+CHARS.index(char)
    return num