# -*- coding:utf-8 -*-

import subprocess
import re
import os

import config


def run_dumpbin(dll_path, cmd):
    print config.DUMPBINPATH + " " + cmd + " " + dll_path
    p = subprocess.Popen([config.DUMPBINPATH, cmd, dll_path.encode("gbk")], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout

def exports(dll_path):
    stdout = run_dumpbin(dll_path, "/EXPORTS")
    # s = r"(\d+)\s+([0-9A-F]+)\s+([0-9A-F]+)?\s+(\S+)(?:\s+\(forwarded to (\S+)\))?(?:\r)"
    s = r"(\d+)\s+([0-9A-F]+)\s+(?:([0-9A-F]+)\s+)?(\S+)(?:\s+\(forwarded to (\S+)\))?(?:\r)"
    pattern = re.compile(s)
    res = pattern.findall(stdout)
    export_list = list()
    for r in res:
        export_list.append((r[3], r[4]))
    return export_list

def exports_full(dll_path):
    stdout = run_dumpbin(dll_path, "/EXPORTS")
    s = r"(\d+)\s+([0-9A-F]+)\s+(?:([0-9A-F]+)\s+)?(\S+)(?:\s+\(forwarded to (\S+)\))?(?:\r)"
    pattern = re.compile(s)
    res = pattern.findall(stdout)
    export_list = list()
    for r in res:
        export_list.append(r)
    return export_list

def imports(dll_path, DLL_API_ORDINAL_DICT={},DLL_PATH=r"D:\Work\Wine\dlls\win7_ultimate_32bit"):
    def get_dll_api_ori(dll_name_nosuffix):
        if dll_name_nosuffix not in DLL_API_ORDINAL_DICT:
            res = exports_full(os.path.join(DLL_PATH, dll_name_nosuffix))
            api_ordinal = dict()
            for r in res:
                api_ordinal[r[0]] = r[3]
            DLL_API_ORDINAL_DICT[dll_name_nosuffix] = api_ordinal
        return DLL_API_ORDINAL_DICT[dll_name_nosuffix]


    stdout = run_dumpbin(dll_path, "/IMPORTS")

    s1 = r"((?:(?: *(?:[0-9A-F]+ +){1,2}(?:\S+)\r\n)|(?: *[0-9A-F]+ +Ordinal +\d+\r\n))*)"
    s1 = r"((?:(?: *(?:[0-9A-F]+ +){1,2}(?:\S+)\r\n)|(?: *(?:[0-9A-F]+ +)?Ordinal +\d+\r\n))*)"

    s2 = r"([0-9A-F]*) *([0-9A-F]+) +(\S+)\r\n"

    s = r"(\S+)\.(?:dll|DLL|exe|EXE|sys|SYS|drv|DRV)\s+" \
        r"[0-9A-F]+\s+Import Address Table\s+" \
        r"[0-9A-F]+\s+Import Name Table\s+" \
        r"[0-9A-F]+\s+time date stamp\s+" \
        r"[0-9A-F]+\s+Index of first forwarder reference\s+" + s1
    s = r"(\S+\.(?:dll|DLL|exe|EXE|sys|SYS|drv|DRV))\s+" \
        r"[0-9A-F]+\s+Import Address Table\s+" \
        r"[0-9A-F]+\s+Import Name Table\s+" \
        r"[0-9A-F]+\s+time date stamp\s+" \
        r"[0-9A-F]+\s+Index of first forwarder reference\s+" + s1


    #s = r"(([0-9A-F]+)\s+([0-9A-F]+)\s+(\S+)\s*)+"
    pattern = re.compile(s)
    res = pattern.findall(stdout)

    import_list = list()
    for r in res:
        import_dict = dict()
        import_dict["name"] = r[0]
        api_list = list()
        s = s2
        p = re.compile(s)
        api_info_list = p.findall(r[1])
        for api_info in api_info_list:
            api_list.append(api_info[2])


        s = "Ordinal +(\d+)\s+"
        p = re.compile(s)
        api_info_list = p.findall(r[1])
        for api_info in api_info_list:
            dll_api_ori = get_dll_api_ori(r[0])
            if api_info in dll_api_ori:
                api_list.append(dll_api_ori[api_info])
            else:
                api_list.append("Ordinal_" + api_info)


        import_dict["api"] = api_list
        import_list.append(import_dict)


    s = r"(\S+)\.(?:dll|DLL|exe|EXE|sys|SYS|drv|DRV)\s+" \
        r"[0-9A-F]+\s+Characteristics\s+" \
        r"[0-9A-F]+\s+Address of HMODULE\s+" \
        r"[0-9A-F]+\s+Import Address Table\s+" \
        r"[0-9A-F]+\s+Import Name Table\s+" \
        r"[0-9A-F]+\s+Bound Import Name Table\s+" \
        r"[0-9A-F]+\s+Unload Import Name Table\s+" \
        r"[0-9A-F]+\s+time date stamp\s+" + s1
    s = r"(\S+\.(?:dll|DLL|exe|EXE|sys|SYS|drv|DRV))\s+" \
        r"[0-9A-F]+\s+Characteristics\s+" \
        r"[0-9A-F]+\s+Address of HMODULE\s+" \
        r"[0-9A-F]+\s+Import Address Table\s+" \
        r"[0-9A-F]+\s+Import Name Table\s+" \
        r"[0-9A-F]+\s+Bound Import Name Table\s+" \
        r"[0-9A-F]+\s+Unload Import Name Table\s+" \
        r"[0-9A-F]+\s+time date stamp\s+" + s1
    pattern = re.compile(s)
    res = pattern.findall(stdout)
    delay_import_list = list()
    for r in res:
        import_dict = dict()
        import_dict["name"] = r[0]
        api_list = list()
        s = s2
        p = re.compile(s)
        api_info_list = p.findall(r[1])
        for api_info in api_info_list:
            api_list.append(api_info[2])

        s = "Ordinal +(\d+)\s+"
        p = re.compile(s)
        api_info_list = p.findall(r[1])
        for api_info in api_info_list:
            dll_api_ori = get_dll_api_ori(r[0])
            if api_info in dll_api_ori:
                api_list.append(dll_api_ori[api_info])
            else:
                api_list.append("Ordinal_" + api_info)

        import_dict["api"] = api_list
        delay_import_list.append(import_dict)

    return  import_list, delay_import_list

def dump_export_dlls():
    for version in config.VERSIONS:
        dlls_path = os.path.join(config.DLL_ROOT_PATH, version)
        dll_list = os.listdir(dlls_path)

        res_path = os.path.join(config.EXPORT_PATH, version)
        if not os.path.exists(res_path):
            os.mkdir(res_path)

        for dll in dll_list:
            res = exports(os.path.join(dlls_path, dll))
            res_file = open(os.path.join(res_path, dll), "w")
            for r in res:
                res_file.write(r[0] + "\t" + r[1] + "\n")
            res_file.close()

def dump_import_dlls():
    for version in config.VERSIONS:
        dlls_path = os.path.join(config.DLL_ROOT_PATH, version)
        dll_list = os.listdir(dlls_path)

        res_path = os.path.join(config.IMPORT_PATH, version)
        if not os.path.exists(res_path):
            os.mkdir(res_path)

        for dll in dll_list:
            load, delay_load = imports(os.path.join(dlls_path, dll))
            res_file = open(os.path.join(res_path, dll), "w")
            for l in load:
                name = l["name"]
                if len(l["api"]) == 0:
                    res_file.write(name + "\t" + "load" + "\n")
                for api in l["api"]:
                    res_file.write(name + "\t" + api + "\t" + "load" + "\n")
            for l in delay_load:
                name = l["name"]
                if len(l["api"]) == 0:
                    res_file.write(name + "\t" + "delay_load" + "\n")
                for api in l["api"]:
                    res_file.write(name + "\t" + api + "\t" + "delay_load" + "\n")
            res_file.close()

def undname(name):
    p = subprocess.Popen([config.UNDNAMEPATH, name], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    clue_str = "is :- \""
    start_index = stdout.find(clue_str)
    end_index = stdout.find("\"", start_index+len(clue_str))
    return stdout[start_index + len(clue_str): end_index]


if __name__ == "__main__":
    print exports(r"D:\Work\Wine\dlls\win7_ultimate_32bit\mfc42.dll")

#    dump_export_dlls()
#    dump_import_dlls()
#    print undname("??ab")