#!/usr/bin/python
# -*- coding: UTF-8 -*-

from models import DLL, API
from HTMLParser import HTMLParser
from tools import writeFile, readHtml

WriteToLocal = False
LocalRootPath = r"C:\Users\iscas\Desktop\Wingear\dll&api"

def analysis_index(root_url):
    """
    input the url of index page, return the DLL list of each first letter.
    :param root_url: a '/' needed in the end of the url
    :return: a dict of DLL
    """
    letter_url_list = map(lambda x: x + ".html", [chr(i) for i in range(97, 123)])
    dlls = dict()
    for letter_url in letter_url_list:
        dlls.update(analysis_letter_page(root_url, letter_url))
    return dlls


def analysis_letter_page(root_url, relative_url):
    class LetterPageHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            # use a dict to store the dll info in a letter page. the info store include dll_name, dll_intro, dll_url
            self.dll_dict = dict()
            self.content = None
            self.url_tmp = None
            self.name_tmp = None

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                if len(attrs) == 0:
                    pass
                else:
                    for (variable, value) in attrs:
                        if variable == "href" and value.find("dll.html") != -1:
                            self.url_tmp = value
                            self.content = "dll_name"

            elif tag == "td":
                if self.content == "dll_intro_td":
                    self.content = "dll_intro"

        def handle_data(self, data):
            if self.content == "dll_name":
                self.content = "dll_intro_td"
                self.name_tmp = data
                return

            elif self.content == "dll_intro":
                self.dll_dict[self.name_tmp] = {"url": self.url_tmp, "intro": data}
                self.content = None
                return

    html = readHtml(root_url + relative_url)

    writeFile(LocalRootPath, relative_url, html, WriteToLocal)
    letter_page_html_parser = LetterPageHTMLParser()
    letter_page_html_parser.feed(html)
    dll_dict = letter_page_html_parser.dll_dict

    dlls = dict()
    for dll_info in dll_dict.items():
        dll = analysis_dll_page(root_url, dll_info[1]["url"])
        if dll == None:
            continue
        dll.name = dll_info[0].lower()

        dll.intro = dll_info[1]["intro"]

        dlls[dll.name] = dll

    return dlls


def analysis_dll_page(root_url, relative_url):
    class DLLPageHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.content = None
            self.new_api = False
            self.api_list = []
            self.depend_dll_list = []
            self.__cont_data = False

        def handle_starttag(self, tag, attrs):
            if tag == "table":
                if self.content == "api list":
                    self.content = "api list start"
            elif tag == "a":
                if self.content == "depend dll list":
                    self.content = "depend dll"
            elif tag == "p":
                if self.content == "depend dll":
                    self.content = None
            elif tag == "td" and self.content == "api list start":
                self.new_api = True

        def handle_endtag(self, tag):
            if tag == "table":
                self.content = None
            if tag == "a" and self.content == "depend dll":
                self.content = "depend dll list"

        def handle_data(self, data):
            if data == "Exported Functions List":
                self.content = "api list"

            if self.content == "api list start":
                if self.new_api:
                    if data.strip() != "":
                        self.api_list.append(data)
                        self.new_api = False
                else:
                    if data.strip() != "":
                        self.api_list[-1] = self.api_list[-1] + data

            if data == "Static Linking":
                self.content = "depend dll list"

            if self.content == "depend dll":
                self.depend_dll_list.append(data.strip())

    try:
        html = readHtml(root_url + relative_url)
        writeFile(LocalRootPath, relative_url, html, WriteToLocal)
        dll_page_html_parser = DLLPageHTMLParser()
        dll_page_html_parser.feed(html)

        dll = DLL()

        for api_name in dll_page_html_parser.api_list:
            api = API()
            api.name = api_name.strip()
            dll.api_list.append(api)

        for dll_name in dll_page_html_parser.depend_dll_list:
            dll.dependent_dll_list.append(dll_name.lower())

        return dll
    except Exception as e:
        f = open(r"C:\Users\iscas\Desktop\Wingear\dll&api\error.info", "a")
        f.write(e.__str__())
        f.close()


if __name__ == "__main__":
    analysis_letter_page("http://www.win7dll.info/", "c.html")
    # LocalRootPath = r"D:\win7_dlls"
    # analysis_index("http://www.win7dll.info/")
    # LocalRootPath = r"D:\winXP_dlls"
    # analysis_index("http://xpdll.nirsoft.net/")
    # LocalRootPath = r"D:\win8_dlls"
    # analysis_index("http://www.nirsoft.net/dll_information/windows8/")
    # LocalRootPath = r"D:\win10_dlls"
    # analysis_index("http://windows10dll.nirsoft.net/")