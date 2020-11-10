import utils.settings as settings
import codecs
import json

def ReadFile(filepath):  # read generic file
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.readlines()
        c_ = list()
        for c in content:
            r = c.rstrip("\n").rstrip("\r")
            c_.append(r)

    except Exception as e:
        settings.logger.error("Error ReadFile: " + str(e))
        c_ = []
    return c_

def WriteFile(filename, list_item):  # write generic file
    file = codecs.open(filename, "w", "utf-8")

    for line in list_item:
        file.write(line + "\n")

    file.close()

def store_before_after_file(before, after, id_commit, repo, date_commit, tot_processed, URL, after_api,
                            before_api, message, file_path, id_internal, id_row):

    data = {}
    data["id_internal"] = id_internal
    data["tot_processed"] = tot_processed
    data["before"] = before
    data["after"] = after
    data["id_commit"] = id_commit
    data["repo"] = repo
    data["date_commit"] = date_commit
    data["before_api"] = before_api
    data["after_api"] = after_api
    data["URL"] = URL
    data["message"] = message
    data["file_path"] = file_path

    with open(settings.result_name, 'a+') as outfile:
        json.dump(data, outfile)
        outfile.write('\n')