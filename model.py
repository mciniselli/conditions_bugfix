import os
from shutil import rmtree
import logging
from ctypes import *

from datetime import datetime, timezone
import time

from subprocess import Popen, PIPE, STDOUT

import os

from utils.textprocessing import TextProcessing

from utils.methodscomparison import MethodComparison

from utils.inputoutput import WriteFile, ReadFile, store_before_after_file

java_path = "output_files"

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')


def run_command(cmd, cwd=None):  # run a specific command and return the output

    cur_work_dir = cwd

    if cur_work_dir is None:
        cur_work_dir = os.getcwd()

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
        self.before = before
        self.after = after
        self.changes = changes


class Repository:
    def __init__(self, repo_full_name):
        self.repo_name = repo_full_name
        if not os.path.isdir('temp'):
            os.makedirs('temp')
        self.repo_dir = os.path.join(os.getcwd(), 'temp', self.repo_name.replace('/', '_'))
        self.ok_repo = True

        self.before = "None"
        self.after = "None"

    def cleanup(self):
        if os.path.isdir(self.repo_dir):
            rmtree(self.repo_dir)

    def srcml_connection(self, before_code, after_code):
        # BAR VERSION
        ##srcml = cdll.LoadLibrary("/usr/lib/libsrcml.so.1.0.0")
        ##version = srcml.srcml_version_number()
        # print("srcML version: {}".format(version))

        # before file
        WriteFile("before.java", before_code)

        java_path = os.path.join(os.getcwd(), "before.java")
        xml_path = os.path.join(os.getcwd(), "before.xml")

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

        text_before = TextProcessing(textxml)

        text_before.remove_comments()
        text_before.remove_tags()

        # after file
        WriteFile("after.java", after_code)

        java_path = os.path.join(os.getcwd(), "after.java")
        xml_path = os.path.join(os.getcwd(), "after.xml")

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

        text_after = TextProcessing(textxml)

        text_after.remove_comments()
        text_after.remove_tags()

        # print("METHODS")
        methods_before = text_before.get_list_of_methods()
        methods_after = text_after.get_list_of_methods()

        self.check_before_after(methods_before, methods_after)

        #
        # comparison=MethodComparison(methods_before, methods_after)
        #
        # comparison.check_before_after()
        #
        # return comparison

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

            # print("TOKENS: {} {}".format(b, a))

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

            if a != b:  # different conditions
                return

            if in_condition and (in_for or in_while or in_if):

                before_condition = list()
                after_condition = list()

                cannot_exit = False
                if in_for:
                    cannot_exit = True

                while (tokens_before[index_before] != "|||CONDITION___END|||" or cannot_exit == True):

                    add = True

                    if tokens_before[index_before] == "|||CONDITION___START|||":
                        add = False
                    if tokens_before[index_before] == "|||CONDITION___END|||":
                        cannot_exit = False  # we have found the first condition end (the end of the second term of for loop). we can not exit
                        add = False
                    if add:
                        before_condition.append(tokens_before[index_before])
                    index_before += 1

                cannot_exit = False
                if in_for:
                    cannot_exit = True
                while (tokens_after[index_after] != "|||CONDITION___END|||" or cannot_exit == True):

                    add = True
                    if tokens_after[index_after] == "|||CONDITION___START|||":
                        add = False
                    if tokens_after[index_after] == "|||CONDITION___END|||":
                        add = False
                        cannot_exit = False

                    if add:
                        after_condition.append(tokens_after[index_after])
                    index_after += 1

                # sometimes there are <condition> tag due to ternary conditions outside the if/while/for condition
                # so once we found the condition we can avoid to process other conditions in the same if/while/for
                in_for = 0
                in_while = 0
                in_if = 0

                if before_condition != after_condition:
                    num_changes += 1

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

        self.before = str(before_method)
        self.after = str(after_method)

    def miner(self, fix_commit, repository, tot_processed, gh_name, id_internal, id_row):

        commit_id = fix_commit.hash
        URL = fix_commit.api_url
        url_before = fix_commit.before
        url_after = fix_commit.after

        path_before = os.path.join(java_path, "{}_before.txt".format(id_internal))
        path_after = os.path.join(java_path, "{}_after.txt".format(id_internal))

        code_before = ReadFile(path_before)
        code_after = ReadFile(path_after)

        self.srcml_connection(code_before, code_after)
        # comparison=self.srcml_connection(code_before, code_after)

        if self.before != "None" and self.after != "None":
            # if comparison.code_before != "None" and comparison.code_after != "None":
            print("STORE")

            store_before_after_file(self.before, self.after, commit_id, repository, str(fix_commit.created_at),
                                    tot_processed, URL, url_after, url_before, fix_commit.message, gh_name,
                                    id_internal, id_row)
