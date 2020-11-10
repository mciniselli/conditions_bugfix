import os
import json
import csv
from collections import Counter
import shutil
from datetime import datetime
import codecs # to read file using utf-8 encoding
from subprocess import Popen, PIPE, STDOUT #use subprocess to run a python file inside the script. It is quicker than os.system()

import re


def count_slash(ss, position):
    count=0;
    pos=position-1
    try:
        while ss[pos]=="\\":
            count+=1
            pos-=1
    except:
        pass
    return count  

def get_strings(code):
    start=list()
    end=list()
    
    start_string=False
    
    for i,c in enumerate(code):
        if c=="\"":
            num_slash=count_slash(code, i)
            if num_slash % 2 == 0 and start_string:
                end.append(i)
                start_string=False
            elif num_slash % 2 == 0:
                start.append(i)
                start_string=True
                
                
    return start, end


def is_in_string(starts, ends, position):
    for x, y in zip(starts, ends):
        if position > x and position < y:
            return True
    return False

#ss, ee=get_strings("ciao\"vero\" mamma")



one_char=["!", "#", "$", "%", "&", "\\", "'", "(", ")", "*", "+","-", ".", "/",
          ":", ";", "<", "=", ">", "?", "[", "]", "^", "{", "|", "}", "~", ","]
# they must be ordered by decreasing length
multi_char=["...", ">>=", "<<=",">>>","<<<","===","!=", "==", "===", "<=", ">=", "*=","&&", "-=", "+=",  
            "||", "--", "++", "|=", "&=", "%=", "/=", "^="]


def NewFind(code, char, start_string, end_string, jolly=[".", " "]):
    
    #occurr=[m.start() for m in re.finditer(old_char, code)] #this may cause an error if contains +, * and other chars
    occurr=[n for n in range(len(code)) if code.find(char, n) == n]
    
            
    multi_char_first=[a[0] for a in multi_char]
    multi_char_second=[a[-1] for a in multi_char]  
    
    starts=list()
    
    for occ in occurr:
        
        if is_in_string(start_string, end_string, occ):
            continue
        
        len_=len(char)
        
        before=False #char before word is ok
        after=False #char after word is ok
        
        try:
            if code[occ+len_] in jolly or code[occ+len_] in one_char or code[occ+len_] in multi_char_first:
                before=True
     
            if code[occ-1] in jolly or code[occ-1] in one_char or code[occ-1] in multi_char_second:
                after=True
            
            if before and after:
                starts.append(occ)
                #print(code_result)
                #print(gap)
        except Exception as e:
            #print("ERROR FIND: {}".format(str(e)))
            continue
    return starts
 
def FindBrackets(code, starts, ends, position): 
    len_=len(code)
    
    start=-1
    end=-1
    count_open=0
    count_closed=0
    
    for i in range(position, len_):
        if code[i]=="(":
            is_string=is_in_string(starts, ends, i)
            if not is_string:
                count_open+=1
                if start==-1:
                    start=i
        elif code[i]==")":
            is_string=is_in_string(starts, ends, i)
            if not is_string:
                count_closed+=1
        if count_open==count_closed and count_open>0:
            end=i
            return start, end
    
    return -1, -1          

def FindBracketsAbs(abs_code, position): #it works on lists and strings
    len_=len(abs_code)
    
    start=-1
    end=-1
    count_open=0
    count_closed=0
    
    for i in range(position, len_):
        token=abs_code[i]

        if "(" in token:
            
            count_open+=1
            if start==-1:
                start=i
        elif ")" in token:
            
            count_closed+=1
        if count_open==count_closed and count_open>0:
            end=i
            return start, end
    
    return -1, -1 


def FindFirstBracket(code): 
    len_=len(code)
    
    for i in range(len_):
        if code[i]=="(":
            return i
    
    return -1


def FindFirstBracketAbs(abs_code):
    len_=len(abs_code)
    for i in range(len_):
        token=abs_code[i]
        if "(" in token:
            return i
    return -1


def ProcessMethod (code, keywords):

    print("CODE")
    print(code)

    s, e = get_strings(code)
    
    result=list()
    
    if len(s) != len(e):
        print("PROBLEM ON STRINGS {} {}".format(len(s), len(e)))
        return result
    
    
    
    for keyword in keywords:
    
        positions=NewFind(code, keyword, s, e)
        
        positions_new=list()
                
        for position in positions:
            st, en= FindBrackets (code, s, e, position)
            print(st,en)
            if st != -1:
                positions_new.append((position, st, en))

                result.append((st, en+1))

    return result

