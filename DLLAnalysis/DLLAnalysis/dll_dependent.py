import os
import MySQLdb

DLL_DIR = "C:\\Users\\iscas\\Desktop\\Wingear\\dll&api\\wine-2.0.2\\wine-2.0.2\\dlls"

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

def parse_makefile_in(makefile_in_path):
    res = dict()
    with open(makefile_in_path) as f:
        content = f.read()
        content = content.replace("\\\n", "")
        lines = content.split("\n")
        for line in lines:
            if line.strip().startswith("MODULE"):
                index = line.find("=")
                module = line[index+1:].strip()
                res['MODULE'] = module
            if line.strip().startswith("IMPORTS"):
                index = line.find("=")
                import_list = line[index+1:].split()
                res['IMPORTS'] = map(lambda s : s.strip(), import_list)
    return res

def dll_depend():
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    connect.autocommit(0)
    cursor = connect.cursor()      
    def import_name_to_model_name(name):
        if name in dll_dict:
            return dll_dict[name]["MODULE"]
        else:
            for dir_name in dll_dict.keys():
                dot_index = dir_name.find(".")
                if dot_index != -1:
                    if dir_name[:dot_index] == name:
                        return dir_name
            return name

    dll_list = os.listdir(DLL_DIR)
    dll_dict = dict()
    for dll in dll_list:
        makefile_in_path = os.path.join(DLL_DIR, dll, "Makefile.in")
        dll_dict[dll] = parse_makefile_in(makefile_in_path)

    sql_list = []
    for dll in dll_list: 
        if "IMPORTS" in dll_dict[dll]:
            import_list = map(import_name_to_model_name, dll_dict[dll]["IMPORTS"])
            for import_dll in import_list:
                #在t_dll_basic中匹配名字，加上后缀    
                import_dll = import_dll.lower()             
                import_dll_2 = import_dll+'%'
                cursor.execute("SELECT d_name from t_dll_basic where d_name like (%s) and d_version_id = (%s)",[import_dll_2,1] )
                res = cursor.fetchone()
                if res:
                    import_dll = res[0]
                else:
                    print "****"+import_dll+"******"
                    import_dll = import_dll                 
                sql = r"insert into t_dll_depend " \
                      r"(dependent_version, dependent_name, dependence_version, dependence_name) " \
                      r"values " \
                      r"(%d, '%s', %d, '%s')" % \
                      (1, dll_dict[dll]["MODULE"], 1, import_dll)
                print import_dll
                sql_list.append(sql)

    __run_sql(sql_list)
    connect.close()

if __name__ == "__main__":
    dll_depend()

