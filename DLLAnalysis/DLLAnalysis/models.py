from xml.dom import minidom


class DLL:
    def __init__(self, name="", intro="", api_list=None, dependent_dll_list=None):
        self.name = name
        self.intro = intro

        if api_list:
            self.api_list = api_list
        else:
            self.api_list = []

        if dependent_dll_list:
            self.dependent_dll_list = dependent_dll_list
        else:
            self.dependent_dll_list = []

        self.call_dll_list = []
        self.depend_dll_num = -1
        self.call_dll_num = -1

    def dll_to_xml(self, dom):
        dll_node = dom.createElement("dll")

        dll_node.setAttribute("name", self.name)

        intro_node = dom.createElement("intro")
        intro_node.appendChild(dom.createTextNode(self.intro))
        dll_node.appendChild(intro_node)

        api_list_node = dom.createElement("api_list")
        for api in self.api_list:
            api_list_node.appendChild(api.api_to_xml(dom))
        dll_node.appendChild(api_list_node)

        dependent_dll_list_node = dom.createElement("dependent_dll_list")
        for dependent_dll in self.dependent_dll_list:
            dll_name_node = dom.createElement("dependent_dll")
            dll_name_node.setAttribute("name", dependent_dll)
            dependent_dll_list_node.appendChild(dll_name_node)
        dll_node.appendChild(dependent_dll_list_node)

        return dll_node

    def xml_to_dll(self, node):
        self.name = node.getAttribute("name")

        intro_node_list = node.getElementsByTagName("intro")
        if intro_node_list and len(intro_node_list) > 0:
            intro_node = intro_node_list[0]
            if intro_node.firstChild != None:
                self.intro = intro_node.firstChild.data

        api_list_node_list = node.getElementsByTagName("api_list")
        if api_list_node_list:
            api_node_list = api_list_node_list[0].getElementsByTagName("api")
            if api_node_list:
                for api_node in api_node_list:
                    api = API()
                    api.xml_to_api(api_node)
                    self.api_list.append(api)

        dependent_dll_list_node_list = node.getElementsByTagName("dependent_dll_list")
        if dependent_dll_list_node_list:
            dependent_dll_node_list = dependent_dll_list_node_list[0].getElementsByTagName("dependent_dll")
            if dependent_dll_node_list:
                for dependent_dll_node in dependent_dll_node_list:
                    self.dependent_dll_list.append(dependent_dll_node.getAttribute("name"))


class API:
    def __init__(self, name="", state="", dll="", synopsis="", description="", params=None, returns=None, implementation=""):
        self.name = name
        # "not documented", "stub" or "normal", or others.
        self.state = state
        self.dll = dll
        self.synopsis = synopsis
        self.description = description
        self.implementation = implementation
        self.forward_api = None

        if params:
            self.params = params
        else:
            self.params = dict()

        if returns:
            self.returns = returns
        else:
            self.returns = dict()

    def api_to_xml(self, dom):
        api_node = dom.createElement("api")

        api_node.setAttribute("name", self.name)
        api_node.setAttribute("state", self.state)
        api_node.setAttribute("dll", self.dll)

        synopsis_node = dom.createElement("synopsis")
        if self.synopsis and len(self.synopsis) > 0:
            synopsis_node.appendChild(dom.createTextNode(self.synopsis))
        api_node.appendChild(synopsis_node)

        description_node = dom.createElement("description")
        if self.description and len(self.description) > 0:
            description_node.appendChild(dom.createTextNode(self.description))
        api_node.appendChild(description_node)

        param_list_node = dom.createElement("param_list")
        for item in self.params.items():
            param_node = dom.createElement("param")
            param_node.setAttribute("name", item[0])
            param_node.appendChild(dom.createTextNode(item[1]))
            param_list_node.appendChild(param_node)
        api_node.appendChild(param_list_node)

        return_list_node = dom.createElement("return_list")
        for item in self.returns.items():
            return_node = dom.createElement("return")
            return_node.setAttribute("status", item[0])
            return_node.appendChild(dom.createTextNode(item[1]))
            return_list_node.appendChild(return_node)
        api_node.appendChild(return_list_node)

        return api_node

    def xml_to_api(self, node):
        self.name = node.getAttribute("name")
        self.state = node.getAttribute("state")
        self.dll = node.getAttribute("dll")

        synopsis_node_list = node.getElementsByTagName("synopsis")
        if synopsis_node_list and len(synopsis_node_list) > 0:
            synopsis_node = synopsis_node_list[0]
            if synopsis_node.firstChild:
                self.synopsis = synopsis_node.firstChild.data

        param_list_node_list = node.getElementsByTagName("param_list")
        if synopsis_node_list:
            for param_node in param_list_node_list:
                name = param_node.getAttribute("name")
                if param_node.firstChild:
                    intro = param_node.firstChild.data
                    self.params[name] = intro

        return_list_node_list = node.getElementsByTagName("return_list")
        if return_list_node_list:
            for return_node in return_list_node_list:
                status = return_node.getAttribute("status")
                if return_node.firstChild:
                    intro = return_node.firstChild.data
                    self.returns[status] = intro


if __name__ == "__main__":
    impl = minidom.getDOMImplementation()
    dom = impl.createDocument(None, "test", None)
    root = dom.documentElement

    dll = DLL("testDLL", "this is a test dll", [API(), API(), API()], ["a", "b", "c"])

    root.appendChild(dll.dll_to_xml(dom))

    f = open("d:/test.xml", "w")
    dom.writexml(f, "\t", "\t", "\n", "utf-8")
