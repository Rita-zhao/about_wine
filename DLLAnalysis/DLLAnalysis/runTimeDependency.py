def main():
    with open(r"D:/QQ/343289715/FileRecv/WeChat.log") as f:
        content = f.read()
    lines = content.split("\n")

    res_set = set()

    dll_left = None
    for line in lines:
        if "load_builtin_dll" in line:
            index = line.find("=")
            dll_name = line[index+1:]
            if '"' in dll_name:
                start_index = dll_name.find('"') + 1
                end_index = dll_name.rfind('"')
                dll_name = dll_name[start_index:end_index].strip()

                slash_index = dll_name.rfind("\\")
                dll_name = dll_name[slash_index+1:]


                dll_left = dll_name
        elif "fixup_imports iscas:dlls" in line:
            index = line.find("=")
            dll_name = line[index+1:].strip()
            if dll_left:
                res_set.add((dll_left.lower(), dll_name.lower()))
                print dll_left, dll_name
        else:
            dll_left = None

    res_list = list(res_set)
    res_list.sort()

    with open("E:/res.txt", "w") as f:
        for res in res_list:
            f.write(res[0] + "\t" + res[1] + "\n")

if __name__ == "__main__":
    main()