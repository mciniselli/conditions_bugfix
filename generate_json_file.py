import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

import gzip
import json
import re
import os
import sys
from datetime import datetime
from dateutil.parser import isoparse
import traceback

from subprocess import Popen, PIPE, STDOUT

import requests

from ctypes import *

from datetime import datetime, timezone
import time

import codecs

data_path = 'data'
archives_lower_limit = datetime(2015, 1, 1)

sha_regex = '[0-9a-f]{6,40}'

fix_words = ['fix', 'solve']
fix_stopwords = ['was', 'been', 'attempt', 'seem', 'solved', 'fixed', 'try', 'trie', 'by', 'test']
introd_stopwords = ['attempt', 'test']
bug_words = ['bug', 'issue', 'problem', 'error']


result_name='raw_data/bugfix_{}.txt'.format(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))

def extract_date(filename):
    return datetime.strptime(filename.split('.')[0], '%Y-%m-%d-%H')

# (“fix” or “solve”) and (“bug” or “issue” or “problem” or “error”)
def is_bugfix_commit(message):
    return ('Merge' not in message) and any(w in message for w in fix_words) and any(w in message for w in bug_words)


def ReadFile(filepath): # read generic file
    try:
        with open(filepath, encoding="utf-8") as f:
            content=f.readlines()
        c_=list()
        for c in content:
            r=c.rstrip("\n").rstrip("\r")
            c_.append(r)

    except Exception as e:
        logging.error("Error ReadFile: " + str(e) )
        c_=[]
    return c_

def WriteFile(filename, list_item): #write generic file
    file = codecs.open(filename, "w", "utf-8")

    for line in list_item:
        file.write(line+"\n")

    file.close()

def main(file_names):
    file_names = sorted(file_names, key=lambda f: extract_date(f))  


    logging.info(f'files count: {len(file_names)}')
    logging.info(f'from file: {file_names[0]}, to: {file_names[-1]}')


    if os.path.exists("raw_data") == False:
        os.makedirs("raw_data")

    tot_processed = 0
    tot = len(file_names)
    for i, file_name in enumerate(file_names):
        logging.info(f'{file_name} # {str(i + 1)} of {tot}')
        try:
            with gzip.open(os.path.join(data_path, file_name)) as f:

                list_of_json_lines=list()


                for line in f:
                    json_data = json.loads(line)
                    if json_data['type'] == 'PushEvent':


                        if extract_date(file_name) < archives_lower_limit:
                            try:
                                for commit in json_data['payload']['shas']:

                                    #if commit[0] !="3203cd1adaf96a56e68fb0c8245393198ffc5a26":
                                    #    continue


                                    repo_full_name = ''
                                    if 'repo' in json_data.keys():
                                        repo_full_name = json_data['repo']['name']
                                    elif 'repository' in json_data.keys():
                                        if 'full_name' in json_data['repository']:
                                            repo_full_name = json_data['repository']['full_name']
                                        elif 'name' in json_data['repository'] and 'owner' in json_data['repository']:
                                            repo_full_name = f"{json_data['repository']['owner']}/{json_data['repository']['name']}"
                                    
                                    if len(repo_full_name) < 3 or len(commit) < 4:
                                        logging.error(f'parsing exception: repo name or commit data not valid')
                                        continue

                                    commit_msg = commit[2]
                                    if is_bugfix_commit(commit_msg):
                                        tot_processed += 1

                                        '''
                                        current_item=list()
                                        current_item.append(json_data['id'])
                                        current_item.append(file_name)
                                        current_item.append(commit[0]) # hash
                                        current_item.append(repo_full_name)
                                        current_item.append(commit_msg)
                                        current_item.append(commit[3]) # author
                                        current_item.append(f'https://api.github.com/repos/{repo_full_name}/commits/{commit[0]}') #api url
                                        current_item.append(json_data['created_at']) # created at
                                        list_of_json_lines.append("|_|".join(current_item))
                                        '''

                                        data={}
                                        data["id"]=json_data['id']
                                        data["filename"]=file_name
                                        data["sha"]=commit[0]
                                        data["repo"]=repo_full_name
                                        data["message"]=commit_msg
                                        data["author"]=commit[3]
                                        data["api"]=f'https://api.github.com/repos/{repo_full_name}/commits/{commit[0]}'
                                        data["created_at"]=json_data['created_at']

                                        list_of_json_lines.append(data)



                            except Exception as e:
                                logging.error(f'parsing exception: {type(e).__name__} {e.args}')
                                print(traceback.format_exc())
                        else:    
                            for commit in json_data['payload']['commits']:
                                commit_msg = commit['message']
                                
                                #if "java" not in commit_msg.lower():
                                #    continue

                                if is_bugfix_commit(commit_msg) and bool(commit['distinct']):
                                    tot_processed += 1

                                    '''
                                    current_item=list()
                                    current_item.append(json_data['id'])
                                    current_item.append(file_name)
                                    current_item.append(commit['sha']) # hash
                                    current_item.append(json_data['repo']['name'])
                                    current_item.append(commit_msg.replace("\n", "|NEW_LINE|"))
                                    current_item.append(commit['author']['name']) # author
                                    current_item.append(commit['url']) #api url
                                    current_item.append(json_data['created_at']) # created at



                                    list_of_json_lines.append("|_|".join(current_item))                                    

                                    '''

                                    data={}
                                    data["id"]=json_data['id']
                                    data["filename"]=file_name
                                    data["sha"]=commit['sha']
                                    data["repo"]=json_data['repo']['name']
                                    data["message"]=commit_msg
                                    data["author"]=commit['author']['name']
                                    data["api"]=commit['url']
                                    data["created_at"]=json_data['created_at']

                                    list_of_json_lines.append(data)


                logging.info(f'total processed commits: {tot_processed}')

                logging.info("Saving commits")
                with open(result_name, 'a+') as outfile:
                    for d in list_of_json_lines:
                        json.dump(d, outfile)
                        outfile.write('\n')

        except Exception as file_error:
            logging.error(f'file exception: {type(file_error).__name__} {file_error.args}')
            print(traceback.format_exc())

        #WriteFile("raw_data/bugfix.txt", list_of_json_lines)



    print('+++ DONE +++')


  

if __name__ == "__main__":


    if len(sys.argv)==2:
        data_path=sys.argv[1]
        logging.info("Reading data from {}".format(data_path))
        file_names = [f for f in os.listdir(data_path) if f.endswith('.json.gz')]
    elif len(sys.argv) > 3:
        from_date = extract_date(sys.argv[1])
        to_date = extract_date(sys.argv[2])
        logging.info(f'from date: {from_date}, to date: {to_date}')
        data_path=sys.argv[3]
        logging.info("Reading data from {}".format(data_path))
        file_names = [f for f in os.listdir(data_path) if f.endswith('.json.gz') and (extract_date(f) >= from_date and extract_date(f) <= to_date)]
    else: 
        file_names = [f for f in os.listdir(data_path) if f.endswith('.json.gz')]

    main(file_names)