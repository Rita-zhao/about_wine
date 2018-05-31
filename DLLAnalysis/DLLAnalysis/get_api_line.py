import re


def __find_pair(s, begin_index, left, right):
    beg = begin_index
    while s[beg] != left and beg < len(s):
        beg += 1

    pair_count = 1
    end = beg + 1
    while pair_count and end < len(s):
        if s[end] == left:
            pair_count += 1
        if s[end] == right:
            pair_count -= 1
        end += 1

    if end != len(s):
        end += 1

    return beg, end


def __get_api_begin_end_line_with_content(api_name, content):
    api_name_pattern = r"WINAPI\s*" + api_name + r"\s*(?=\()"  #TODO may need to consider other conditions.
    begin_line = 0
    end_line = 0
    api_name_matches = re.finditer(api_name_pattern, content)
    for match in api_name_matches:
        match_beg, match_end = match.span()
        parm_beg, parm_end = __find_pair(content, match_end, '(', ')')
        body_beg, body_end = __find_pair(content, parm_end, '{', '}')
        if content[parm_end:body_beg].strip() == "":
            begin_line = content.count('\n', 0, match_beg) + 1
            end_line = content.count('\n', 0, body_end) + 1
            break
        else:
            continue

    print begin_line, end_line
    return begin_line, end_line


def get_api_begin_end_line(api_name, file_path):
    with open(file_path) as f:
        content = f.read()
        return __get_api_begin_end_line_with_content(api_name, content)


def get_api_begin_end_lines(api_name_file_path_pair_list):
    file_content_dict = {}
    for pair in api_name_file_path_pair_list:
        file_path = pair[1]
        if not file_content_dict.get(file_path):
            with open(file_path) as f:
                file_content_dict[file_path] = f.read()

    res_list = []
    for pair in api_name_file_path_pair_list:
        api_name = pair[0]
        file_path = pair[1]
        res_list.append(__get_api_begin_end_line_with_content(api_name, file_content_dict[file_path]))
    return res_list

if __name__ == "__main__":
    get_api_begin_end_line(r"TpCallbackLeaveCriticalSectionOnCompletion", r"D:\Source Insight\Projects\wine-2.0.1\wine-2.0.1\dlls\ntdll\threadpool.c")

