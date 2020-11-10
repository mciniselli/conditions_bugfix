import re

class TextProcessing:
    def __init__(self, text):
        self.text=text

    def remove_comments(self):

        text=self.text

        self.text = re.sub("(?s)<comment.*?</comment>", "", text);

    def remove_tags(self):

        text=self.text

        text = text.replace("<function", "|||FUNCTION___START|||<function").replace("</function>",
                                                                                    "|||FUNCTION___END|||")
        text = text.replace("<constructor", "|||FUNCTION___START|||<function").replace("</constructor>",
                                                                                       "|||FUNCTION___END|||")
        # we have control tag starting the for condition. We treat it as a condition (as always happens in while and if)
        text = text.replace("<control>", "|||CONDITION___START|||<condition>").replace("</control>",
                                                                                       "|||CONDITION___END|||")

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

        self.text=res

    def get_list_of_methods(self):

        text=self.text

        text_new = text.replace("|||FUNCTION___START|||", "|||NEW_LINE||||||FUN|||")
        text_new = text_new.replace("|||FUNCTION___END|||", "|||NEW_LINE|||")

        methods = text_new.split("|||NEW_LINE|||")

        return methods