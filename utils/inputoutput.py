import utils.settings as settings
import codecs

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
