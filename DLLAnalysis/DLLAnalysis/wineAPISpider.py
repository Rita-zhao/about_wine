# -*- coding: utf-8 -*-
from models import DLL, API
from HTMLParser import HTMLParser
from tools import readHtml, writeFile
import re

LocalRootPath = r"D:\wine_dlls"
WriteToLocal = False


def analysis_index(root_url):
    class IndexHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.content = None
            self.dll_dict = dict()
            self.url_tmp = None
            self.name_tmp = None

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                if self.content == "dll list" and len(attrs) != 0:
                    self.content = "dll"
                    for (variable, value) in attrs:
                        if variable == "href":
                            self.url_tmp = value
            if tag == "i" and self.content == "dll list":
                self.content = None

        def handle_endtag(self, tag):
            if tag == "a" and self.content == "dll":
                self.content = "dll list"

        def handle_data(self, data):
            if data == "DLLS":
                self.content = "dll list"
            if self.content == "dll":
                self.name_tmp = data
                self.dll_dict[self.name_tmp+".dll"] = {"url": self.url_tmp}


    html = readHtml(root_url + "index.html")

    writeFile(LocalRootPath, "index.html", html, WriteToLocal)

    index_html_parser = IndexHTMLParser()
    index_html_parser.feed(html)
    dlls = dict()
    for dll_info in index_html_parser.dll_dict.items():
        dll = analysis_dll(root_url, dll_info[1]["url"])
#        dll.name = dll_info[0].lower()
#        dlls[dll_info[0]] = dll
        dlls[dll.name] = dll

    return dlls


def analysis_dll(root_url, relative_url):
    class DLLHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.content = None
            self.api_name_tmp = None
            self.api_url_tmp = None
            self.api_dict = dict()

        def handle_starttag(self, tag, attrs):
            if tag == "p" and self.content == "api list":
                self.content = "api"
                self.api_name_tmp = ""
                self.api_url_tmp = []
            if tag == "a" and self.content == "api":
                for (variable, value) in attrs:
                    if variable == "href":
                        self.api_url_tmp.append(value)
            if (tag == "h2" or tag == "hr") and self.content == "api list":
                self.content = None

        def handle_endtag(self, tag):
            if tag == "p" and self.content == "api":
                self.api_dict[self.api_name_tmp] = {"url": self.api_url_tmp}
                self.api_name_tmp = None
                self.api_url_tmp = None
                self.content = "api list"

        def handle_data(self, data):
            if data == "EXPORTS":
                self.content = "api list"
            if self.content == "api":
                self.api_name_tmp = self.api_name_tmp + data

    html = readHtml(root_url + relative_url)
    # print "dll page", relative_url

    writeFile(LocalRootPath, relative_url, html, WriteToLocal)

    dll_html_parser = DLLHTMLParser()
    dll_html_parser.feed(html)
    match = re.search(r'<h2\s*class="section">\s*NAME\s*</h2>\s*<p>(.*)\s*</p>', html)
    dll_name = match.group(1).strip()
    dll = DLL()
    dll.name = dll_name

    for api_info in dll_html_parser.api_dict.items():
        if len(api_info[1]['url']) > 0:
          #  print api_info[1]['url']
            api = analysis_api(root_url, api_info[1]['url'][0])
   #         print "----------------------"
        else:
            api = API()
        api_name = api_info[0]
        left_bracket_index = api_name.find('(')
        if left_bracket_index != -1:
            name = api_name[0: left_bracket_index].strip()
            right_bracket_index = api_name.find(')')
            state = api_name[left_bracket_index+1: right_bracket_index].strip()
        else:
            name = api_name.strip()
            state = "normal"
        api.name = name
        dll.api_list.append(api)
  #有些API转发到自己的文件的其他API中实现，目标api并未出现在api_list中，需要添加入列表中          
        if "implemented as" in state:
       #     print state
            state = state.split("implemented as")
            forward_tar = state[1].strip()
            print forward_tar 
            print "***********"
            print dll_html_parser.api_dict.items()
            forward_tar = forward_tar + " "
            if forward_tar in  str(dll_html_parser.api_dict.items()):
                pass
            else:
       #         print forward_tar
                api_ = analysis_api(root_url, api_info[1]['url'][0])
       #         print "*****************************"            
                api_.name = forward_tar
 #       api.state = state
        
                dll.api_list.append(api_)
        
    return dll


def analysis_api(root_url, relative_url):
    class APISynopsisHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.content = None
            self.synopsis = ""

        def handle_starttag(self, tag, attrs):
            if tag == "pre" and self.content == "synopsis section":
                self.content = "synopsis"

        def handle_endtag(self, tag):
            if tag == "pre" and self.content == "synopsis":
                self.content = None

        def handle_data(self, data):
            if data == "SYNOPSIS":
                self.content = "synopsis section"
            if self.content == "synopsis":
                self.synopsis = self.synopsis + data

    class APIDescriptionHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.content = None
            self.description = ""

        def handle_starttag(self, tag, attrs):
            if tag == "p" and self.content == "description section":
                self.content = "description"

        def handle_endtag(self, tag):
            if tag == "p" and self.content == "description":
                self.content = None

        def handle_data(self, data):
            if data == "DESCRIPTION":
                self.content = "description section"
            if self.content == "description":
                self.description = data

    class ParamsHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.content = None
            self.params = dict()
            self.api_param_name_tmp = ''

        def handle_starttag(self, tag, attrs):
            if tag == "tr" and self.content == "param section":
                self.content = "param"
            elif tag == "td":
                if self.content == "param":
                    self.content = "param name"
                elif self.content == "param name":
                    self.content = "param type"
                elif self.content == "param type":
                    self.content = "param description"
            elif tag == "h2" and self.content == "param section":
                self.content = None

        def handle_endtag(self, tag):
            if tag == "tr":
                self.content = "param section"
            elif tag == "td" and self.content == "param description":
                self.content = "param"

        def handle_data(self, data):
            if data == "PARAMS":
                self.content = "param section"
            elif self.content == "param name" and data.strip() != "":
                if data.strip() == "None.":
                    self.content = None
                else:
                    self.api_param_name_tmp = data
                    self.params[data] = ""
            elif self.content == "param type":
                self.params[self.api_param_name_tmp] = data
            elif self.content == "param description":
                self.params[self.api_param_name_tmp] = self.params[self.api_param_name_tmp] + data

    class ReturnsHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.content = None
            self.return_type_tmp = ""
            self.returns = dict()

        def handle_starttag(self, tag, attrs):
            if tag == "p" and self.content == "return section":
                self.content = "return"
            elif tag == "b" and self.content == "return":
                self.content = "return type"
            elif tag == "h2":
                self.content = None

        def handle_endtag(self, tag):
            if tag == "b" and self.content == "return type":
                self.content = "return"
            if tag == "p" and self.content == "return":
                self.content = "return section"

        def handle_data(self, data):
            if data == "RETURNS":
                self.content = "return section"
            if self.content == "return type":
                self.return_type_tmp = data
                self.returns[data] = None
            if self.content == "return":
                self.returns[self.return_type_tmp] = data.strip()
                
    class APIImplementationHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.content = None
            self.implementation = ""

        def handle_starttag(self, tag, attrs):
            if tag == "p" and self.content == "implementation section":
                self.content = "implementation"
            if tag ==  "hr" and self.content == "implementation section":
                self.content = None

        def handle_endtag(self, tag):
            if tag == "p" and self.content == "implementation":
                self.content = "implementation section"

        def handle_data(self, data):
            if data == "IMPLEMENTATION":
                self.content = "implementation section"
            if self.content == "implementation":
                self.implementation += data         

    html = readHtml(root_url + relative_url)

    writeFile(LocalRootPath, relative_url, html, WriteToLocal)

    api_synopsis_html_parser = APISynopsisHTMLParser()
    api_description_html_parser = APIDescriptionHTMLParser()
    params_html_parser = ParamsHTMLParser()
    returns_html_parser = ReturnsHTMLParser()
    api_implementation_html_parser = APIImplementationHTMLParser()

    api_synopsis_html_parser.feed(html)
    api_description_html_parser.feed(html)
    params_html_parser.feed(html)
    returns_html_parser.feed(html)
    api_implementation_html_parser.feed(html)

    api = API()
    api.synopsis = api_synopsis_html_parser.synopsis
    api.description = api_description_html_parser.description
    api.params = params_html_parser.params
    api.returns = returns_html_parser.returns
    api.implementation = api_implementation_html_parser.implementation

    return api

if __name__ == "__main__":
    #print analysis_index(r"C:/Users/iscas/Desktop/Wingear/dll&api/html/html/")
    dll = analysis_dll(r"C:/Users/iscas/Desktop/Wingear/dll&api/html/html/", r"rsaenh.html")

    for api in dll.api_list:
        print "------------------"
        print api.name
        print api.state
        print api.description
        print api.synopsis
        print api.returns
        print api.implementation
