import os
from shutil import rmtree
import logging
from ctypes import *

from datetime import datetime, timezone
import time

from subprocess import Popen, PIPE, STDOUT

from construct_processing import *

import os

import sys
import codecs

import utils.settings as settings

from utils.inputoutput import WriteFile, ReadFile

java_path="output_files"

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

def run_command(cmd, cwd=None): # run a specific command and return the output

    cur_work_dir=cwd

    if cur_work_dir is None:
        cur_work_dir=os.getcwd()

    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=cur_work_dir)
    output = p.stdout.read()
    logging.info(output)
    logging.info("______________________________________")

    output2 = str(output)

    return output2


class Commit(object):
    def __init__(self, hash, repository, message, api_url, created_at, before, after, changes):
        self.hash = hash
        self.repository = repository
        self.message = message
        self.api_url = api_url
        self.created_at = created_at
        self.before=before
        self.after=after
        self.changes=changes


class Repository:
    def __init__(self, repo_full_name):
        self.repo_name = repo_full_name
        if not os.path.isdir('temp'):
            os.makedirs('temp')
        self.repo_dir = os.path.join(os.getcwd(), 'temp', self.repo_name.replace('/', '_'))
        self.ok_repo=True

        self.before="None"
        self.after="None"

    def cleanup(self):
        if os.path.isdir(self.repo_dir):
            rmtree(self.repo_dir)

    def removeComments(self, text):

        res = re.sub("(?s)<comment.*?</comment>", "", text);
        return res

    def removeTag(self, text):

        text = text.replace("<function", "|||FUNCTION___START|||<function").replace("</function>",
                                                                                    "|||FUNCTION___END|||")
        text = text.replace("<constructor", "|||FUNCTION___START|||<function").replace("</constructor>",
                                                                                       "|||FUNCTION___END|||")
        # we have control tag starting the for condition. We treat it as a condition (as always happens in while and if)
        text = text.replace("<control>", "|||CONDITION___START|||<condition>").replace("</control>", "|||CONDITION___END|||")

        text = text.replace("<for>", "|||FOR___START|||<for>").replace("</for>", "|||FOR___END|||")
        text = text.replace("<if>", "|||IF___START|||<if>").replace("</if>", "|||IF___END|||")
        text = text.replace("<if type=\"elseif\">", "|||IF___START|||<if type=\"elseif\">").replace("</if>",
                                                                                                    "|||FUNCTION___END|||")
        text = text.replace("<while>", "|||WHILE___START|||<while>").replace("</while>", "|||WHILE___END|||")
        text = text.replace("<condition>", "|||CONDITION___START|||<condition>").replace("</condition>",
                                                                                         "|||CONDITION___END|||")
        l = ["|||FOR___START|||", "|||FOR___END|||", "|||IF___START|||", "|||IF___END|||",
             "|||WHILE___START|||", "|||WHILE___END|||", "|||CONDITION___START|||", "|||CONDITION___END|||"]


        for el in l:
            text = text.replace(el, "|_|{}|_|".format(el))

        res = (re.sub(r'\<[^>]*\>', '|_|', text))

        res = res.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;",
                                                                    "&")  # these characters are replaced with HTML version => we replace them all

        # if there are some comments, once removed it remains an empty line. We want to remove all empty lines
        while "\n    \n    " in res:
            res = res.replace("\n    \n    ", "\n    ")

        res = res.replace("\n    ", "|_|")

        while "|_| |_|" in res:
            res = res.replace("|_| |_|", "|_|")
        while "|_||_|" in res:
            res = res.replace("|_||_|", "|_|")
        return res

    def get_list_of_methods(self, text):

        text_new = text.replace("|||FUNCTION___START|||", "|||NEW_LINE||||||FUN|||")
        text_new = text_new.replace("|||FUNCTION___END|||", "|||NEW_LINE|||")

        result = text_new.split("|||NEW_LINE|||")

        #print(result)

        return result

    def srcml_connection(self, before_code, after_code):
        # BAR VERSION
        ##srcml = cdll.LoadLibrary("/usr/lib/libsrcml.so.1.0.0")
        ##version = srcml.srcml_version_number()
        #print("srcML version: {}".format(version))

        # before file
        WriteFile("before.java", before_code)

        java_path = os.path.join(os.getcwd(), "before.java")
        xml_path = os.path.join(os.getcwd(), "before.xml")

        print(java_path)

        run_command("srcml {} -o {}".format(java_path, xml_path), os.getcwd())

        f = open(xml_path, "r")
        textxml = ""
        skip_line = True
        for x in f:
            # print(x)
            if skip_line == True:
                skip_line = False
                continue
            if len(x.strip()) == 0:
                continue
            textxml += x.strip() + "\n    "

        f.close()

        res_ = self.removeComments(textxml)

        res_before = self.removeTag(res_)

        # after file

        WriteFile("after.java", after_code)

        java_path = os.path.join(os.getcwd(), "after.java")
        xml_path = os.path.join(os.getcwd(), "after.xml")

        print(java_path)

        run_command("srcml {} -o {}".format(java_path, xml_path), os.getcwd())

        f = open(xml_path, "r")
        textxml = ""
        skip_line = True
        for x in f:
            # print(x)
            if skip_line == True:
                skip_line = False
                continue
            if len(x.strip()) == 0:
                continue
            textxml += x.strip() + "\n    "

        f.close()

        res_ = self.removeComments(textxml)

        res_after = self.removeTag(res_)

        #print("METHODS")
        methods_before = self.get_list_of_methods(res_before)
        methods_after = self.get_list_of_methods(res_after)

        self.check_before_after(methods_before, methods_after)

    def check_before_after(self, methods_before_original, methods_after_original):

        # check if non function before and after are the same

        if len(methods_before_original) != len(methods_after_original):
            return -1

        methods_before = list()
        methods_after = list()

        for x, y in zip(methods_before_original, methods_after_original):
            if x.startswith("|||FUN|||") == False:
                if x != y:  # the code is different
                    return -1

            else:
                if y.startswith("|||FUN|||") == False:  # this is not a function
                    return -1


                methods_before.append(x.replace("|||FUN|||", "").strip())
                methods_after.append(y.replace("|||FUN|||", "").strip())


        if len(methods_before) != len(methods_after):
            return -1

        methods_preprocessed_before = list()
        methods_preprocessed_after = list()

        self.CheckMethodsBeforeAfter(methods_before, methods_after)

    def CheckMethodsBeforeAfter(self, before, after):

        num_changes = 0

        id_method_changed = -1

        for i, (x, y) in enumerate(zip(before, after)):
            if x != y:
                num_changes += 1
                id_method_changed = i

        print("NUM CHANGES: {}".format(num_changes))

        if num_changes != 1:
            return

        in_if = False
        in_for = False
        in_while = False
        in_condition = False

        is_changing = False

        before_method = list()
        after_method = list()

        method_changed_before = before[id_method_changed]
        method_changed_after = after[id_method_changed]

        tokens_before = method_changed_before.split("|_|")
        tokens_after = method_changed_after.split("|_|")

        # remove empty tokens
        tokens_before = [x for x in tokens_before if len(x) > 0]
        tokens_after = [x for x in tokens_after if len(x) > 0]

        index_before = 0
        index_after = 0

        num_changes = 0

        while (1 == 1):

            if index_before >= len(tokens_before) - 1:
                if index_after != len(tokens_after) - 1:  # there are other tokens in method_after
                    return
                elif tokens_before[index_before] != tokens_after[index_after]:  # last token is different
                    return
                else:  # OK
                    break

            b = tokens_before[index_before]
            a = tokens_after[index_after]

            #print("TOKENS: {} {}".format(b, a))

            real_token = False

            if b == "|||IF___START|||":
                in_if = True
            elif b == "|||FOR___START|||":
                in_for = True
            elif b == "|||WHILE___START|||":
                in_while = True
            elif b == "|||CONDITION___START|||":
                in_condition = True
            elif b == "|||IF___END|||":
                in_if = False
            elif b == "|||FOR___END|||":
                in_for = False
            elif b == "|||WHILE___END|||":
                in_while = False
            elif b == "|||CONDITION___END|||":
                in_condition = False
            else:
                real_token = True

            #print(in_condition)

            if a != b:
                #print("DIFFERENT TOKEN")
                return

            if in_condition and (in_for or in_while or in_if):

                before_condition = list()
                after_condition = list()

                cannot_exit=False
                if in_for:
                    cannot_exit=True

                while (tokens_before[index_before] != "|||CONDITION___END|||" or cannot_exit==True):

                    add=True

                    if tokens_before[index_before]=="|||CONDITION___START|||":
                        add=False
                    if tokens_before[index_before]=="|||CONDITION___END|||":
                        cannot_exit=False # we have found the first condition end (the end of the second term of for loop). we can not exit
                        add=False
                    if add:
                        before_condition.append(tokens_before[index_before])
                    index_before += 1

                cannot_exit=False
                if in_for:
                    cannot_exit=True
                while (tokens_after[index_after] != "|||CONDITION___END|||" or cannot_exit==True):

                    add=True
                    if tokens_after[index_after]=="|||CONDITION___START|||":
                        add=False
                    if tokens_after[index_after]=="|||CONDITION___END|||":
                        add=False
                        cannot_exit=False

                    if add:
                        after_condition.append(tokens_after[index_after])
                    index_after += 1

                if before_condition != after_condition:
                    num_changes += 1

                #print("BEF COND: {}".format(before_condition))

                before_method.extend(before_condition)  # remove |||CONDITION_START|||
                after_method.extend(after_condition)

                if num_changes > 1:
                    return

                continue

            if real_token:
                before_method.append(b)
                after_method.append(a)

            index_before += 1
            index_after += 1

        self.before=str(before_method)
        self.after=str(after_method)

    def wait_if_requests_finished(self, response_header):

        if int(response_header["X-RateLimit-Remaining"]) != 0:
            return

        ts = int(response_header["X-RateLimit-Reset"])

        #print(ts)

        # if you encounter a "year is out of range" error the timestamp
        # may be in milliseconds, try `ts /= 1000` in that case

        date_end = datetime.utcfromtimestamp(ts)

        #print(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
        #time.sleep(0.3)

        date_now = datetime.now(timezone.utc)

        #print(date_now.strftime("%Y-%m-%dT%H:%M:%S.%f%Z"))

        date_now_notz = date_now.replace(tzinfo=None)
        date_end_notz = date_end.replace(tzinfo=None)

        num_sec_to_wait=(date_end_notz - date_now_notz).total_seconds()

        print("SEC TO WAIT {} REMAINING REQUESTS {}".format(num_sec_to_wait, response_header["X-RateLimit-Remaining"]))

        ###settings.useapi=False
        ###settings.time_end=date_end_notz

        time.sleep(num_sec_to_wait+10)

    def store_before_after_file(self, before, after, id_commit, repo, date_commit, tot_processed, URL, after_api, before_api, message, file_path, id_internal, id_row):

        filename=settings.result_name


        data={}
        data["id_internal"]=id_internal
        data["tot_processed"]=tot_processed
        data["before"]=before
        data["after"]=after
        data["id_commit"]=id_commit
        data["repo"]=repo
        data["date_commit"]=date_commit
        data["before_api"]=before_api
        data["after_api"]=after_api
        data["URL"]=URL
        data["message"]=message
        data["file_path"]=file_path

        print(settings.result_name)

        with open(settings.result_name, 'a+') as outfile:
            json.dump(data, outfile)
            outfile.write('\n')




    # working version but it uses api github
    def miner(self, fix_commit, repository, tot_processed, gh_name, id_internal, id_row):

        commit_id=fix_commit.hash
        URL=fix_commit.api_url
        url_before=fix_commit.before
        url_after=fix_commit.after

        path_before=os.path.join(java_path, "{}_before.txt".format(id_internal))
        path_after=os.path.join(java_path, "{}_after.txt".format(id_internal))

        code_before=ReadFile(path_before)
        code_after=ReadFile(path_after)

        self.srcml_connection(code_before, code_after)


        if self.before != "None" and self.after !="None":

            print("STORE")

            self.store_before_after_file(self.before, self.after, commit_id, repository, str(fix_commit.created_at), tot_processed, URL, url_after, url_before, fix_commit.message, gh_name, id_internal, id_row)
