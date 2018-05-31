from models import DLL, API
from DLLAnalyser import DLLAnalyser
import MySQLdb
import re
import get_api_line

import datetime
import os

def __parse_implemention(impl):
    decl_pattern = r'Declared in "([\.\w\d_/]+)". source.winehq.org/source/([\.\w\d_/]+)'
    impl_pattern = r'Implemented in "([\.\w\d_/]+)". source.winehq.org/source/([\.\w\d_/]+)'
    decl_match = re.search(decl_pattern, impl)
    impl_match = re.search(impl_pattern, impl)
    decl_file = None
    impl_file = None
    if decl_match:
        decl_file = decl_match.group(2)
    if impl_match:
        impl_file = impl_match.group(2)
    return decl_file, impl_file


def __run_sql(sql_list):
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    try:
        connect.autocommit(0)
        cursor = connect.cursor()

        for sql in sql_list:
            print sql
            cursor.execute(sql)

        connect.commit()
    finally:
        connect.close()


def wine_file(analyser):
    file_set = set()
    for dll in analyser.dlls:
        for api in analyser.dlls[dll].api_list:
            decl_file, impl_file = __parse_implemention(api.implementation)
            if decl_file:
                file_set.add(decl_file)
            if impl_file:
                file_set.add(impl_file)
    file_list = list(file_set)
    file_list.sort()
    sql_list = []
    for file in file_list:
        file_name = os.path.basename(file)
        print file_name
        sql = r"insert into t_wine_file " \
              r"(w_version_id, f_path, f_name) " \
              r"values" \
              r"(1, '%s', '%s')" % (file, file_name)
        sql_list.append(sql)
    __run_sql(sql_list)

def wine_file_api_contain(analyser):
    sql_list = []
    for dll in analyser.dlls:
        name_file_abs_path_list = []
        api_file_list = []
        for api in analyser.dlls[dll].api_list:
            api_name = api.name
            _, impl_file = __parse_implemention(api.implementation)
            if impl_file:
                name_file_abs_path_list.append((api_name, os.path.join(r"C:\Users\iscas\Desktop\Wingear\dll&api\wine-2.0.2\wine-2.0.2", impl_file)))
                api_file_list.append((api, impl_file))
        line_num_list = get_api_line.get_api_begin_end_lines(name_file_abs_path_list)

        for i in xrange(len(line_num_list)):
            api = api_file_list[i][0]
            file_path = api_file_list[i][1]
            dll_version = 1
            dll_name = dll
            api_name = api.name
           # api_parameters = str(api.params.keys())
           # print api_parameters
           
           #填写api参数信息
            str = api.params.__str__()
            parameters = "{"
            # print str
            for s in eval(str).keys():
                parameters += s+","
            if len(parameters) > 1:
                parameters=parameters[:len(parameters)-1]
            else:
                parameters = parameters
            parameters+="}" 
       
           # print parameters             
           
            startline = line_num_list[i][0]
            endline = line_num_list[i][1]
            sql = r"insert into t_wine_file_api_contain " \
                  r"(wine_version, file_path, dll_version, dll_name, api_name, api_parameters, startline, endline) " \
                  r"values" \
                  r"(1, '%s', %d, '%s', '%s', '%s', '%d', '%d')" % \
                  (file_path, dll_version, dll_name, api_name, parameters.replace(r"'", r"\'"), startline, endline)
            sql_list.append(sql)

    __run_sql(sql_list)


def api_forward(analyser):
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    connect.autocommit(0)
    cursor = connect.cursor()    
    
    sql_list = []
  #  foward = []
    for dll in analyser.dlls:
        for api in analyser.dlls[dll].api_list:
            if api.forward_api != None and api.forward_api != "":
                dot_index = api.forward_api.rfind(".")
                if dot_index != -1:
                    forward_dll = api.forward_api[:dot_index]
                    forward_api = api.forward_api[dot_index+1:]
                else:
                    forward_dll = dll
                    forward_api = api.forward_api
                '''
                if forward_dll in foward:
                    continue
                else:
                    foward.append(forward_dll)
                print foward
                '''
                if len(api.name) > 500:
                    with open(r"C:/Users/iscas/Desktop/Wingear/dll&api/test.log", "a") as f:
                        f.write("/t".join([dll, api.name])+"\n")
                    continue

                #填写api参数信息
                str = api.params.__str__()
                parameters = "{"
               # print str
                for s in eval(str).keys():
                    parameters+=s+","
                if len(parameters) > 1:
                    parameters=parameters[:len(parameters)-1]
                else:
                    parameters = parameters
                parameters+="}" 
              
               # print parameters
                
                #在t_dll_basic中匹配名字，加上后缀    
                forward_dll = forward_dll.lower()             
                forward_dll_2 = forward_dll+'%'
                cursor.execute("SELECT d_name from t_dll_basic where d_name like (%s) and d_version_id = (%s)",[forward_dll_2,1] )
                res = cursor.fetchone()
                if res:
                    forward_dll = res[0]
                else:
                    forward_dll =forward_dll                                
                sql = r"insert into t_api_forward " \
                      r"(source_version, source_dllname, source_apiname, source_parameters, target_version, target_dllname, target_apiname, target_parameters) " \
                      r"values " \
                      r"(1, '%s', '%s', '%s', 1, '%s', '%s', '%s') " % \
                      (dll, api.name, parameters.replace(r"'", r"\'"), forward_dll, forward_api, ' ')
             #   print sql
                sql_list.append(sql)
                print "--------"
                print forward_dll
    __run_sql(sql_list)
    connect.close()

def main():
    start = datetime.datetime.now()
    wine_dll_analyser = DLLAnalyser()
    wine_dll_analyser.load_from_html(r"C:/Users/iscas/Desktop/Wingear/dll&api/html/html/", "wine")

    end = datetime.datetime.now()

    wine_file(wine_dll_analyser)
    wine_file_api_contain(wine_dll_analyser)
    wine_dll_analyser.add_info_from_spec(r"C:/Users/iscas/Desktop/Wingear/dll&api/wine-2.0.2/wine-2.0.2/dlls/")
    api_forward(wine_dll_analyser)

    print "Load time: ", (end-start).seconds, "seconds."

if __name__ == "__main__":
    main()
