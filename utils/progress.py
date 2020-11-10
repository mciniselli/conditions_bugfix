import os
import utils.settings as settings

from utils.inputoutput import ReadFile, WriteFile


def read_progress_file():
    if os.path.exists('progress.txt') == False:
        res = ["{} -1".format(x) for x in settings.file_list]
        write_progress_file(res)
    else:
        res = ReadFile("progress.txt")
        if len(res) == 0:  # empty file
            res = ["{} -1".format(x) for x in settings.file_list]
            write_progress_file(res)

    return res


def update_progress_bar(filename, id_num):
    res = read_progress_file()

    for i, r in enumerate(res):
        t = r.split(" ")
        if t[0] == filename:
            res[i] = "{} {}".format(filename, id_num)

    write_progress_file(res)


def get_progress_value(filename):
    res = read_progress_file()

    for r in res:
        t = r.split(" ")
        if t[0] == filename:
            return int(t[1])

    return -1


def write_progress_file(res):
    WriteFile("progress.txt", res)
