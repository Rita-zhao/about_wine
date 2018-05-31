import os
import config
from dump import undname
import MySQLdb


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


def export_info():
    sql_dll_base_list = []
    sql_api_base_list = []
    version = "win7_ultimate_32bit"
    export_file_dir = os.path.join(config.EXPORT_PATH, version)

    dll_list = os.listdir(export_file_dir)

    for dll_file in dll_list:
        print dll_file
        dll_name = dll_file.lower()
        suffix = dll_name[dll_name.rfind(".") + 1:]


        sql_dll_base = \
            r"insert into t_dll_basic " \
            r"(d_version_id, d_name, d_suffix, d_category, d_description) " \
            r"values" \
            r"(%d, '%s', '%s', '%s', '%s')" % \
            (2, dll_name, suffix, '', version)
        sql_dll_base_list.append(sql_dll_base)
        api_name_set = set()
        with open(os.path.join(export_file_dir, dll_file)) as f:
            for line in f:
                content = line.strip().split("\t")
                api_name = content[0]

                description = ""
                if api_name.startswith("?"):
                    description = undname(api_name)

                if len(api_name) > 600:
                    with open("C:/Users/iscas/Desktop/Wingear/dll&api/log.log", "a") as x:
                        x.write(str(len(api_name)) + api_name+"\t"+description+"\n")
                    continue
                if api_name.lower() in api_name_set:
                    print len(api_name_set)
                    with open("C:/Users/iscas/Desktop/Wingear/dll&api/log_apiname.log", "a") as x:
                        x.write(dll_name+"\t"+api_name+"\n")
                    continue

                api_name_set.add(api_name.lower())
                sql_api_base = \
                    r"insert into t_api_basic " \
                    r"(d_version_id, d_name, a_name, a_parameters, a_status, a_description) " \
                    r"values " \
                    r"(%d, '%s', '%s', '%s', '%s', '%s')" % \
                    (2, dll_name, api_name, '', '', description.replace(r"'", r"\'"))
                sql_api_base_list.append(sql_api_base)
    __run_sql(sql_dll_base_list)
    __run_sql(sql_api_base_list)


def import_info():
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    connect.autocommit(0)
    cursor = connect.cursor()      
    sql_dll_depend_list = []
    sql_dll_api_depend_list = []
    version = "win7_ultimate_32bit"
    import_file_dir = os.path.join(config.IMPORT_PATH, version)
    dll_list = os.listdir(import_file_dir)
    for dll_file in dll_list:
        print dll_file
        dll_name = dll_file.lower()
        with open(os.path.join(import_file_dir, dll_file)) as f:
            depend_dll_name = ""
            for line in f:
                content = line.strip().split("\t")
                if depend_dll_name != content[0]:
                    depend_dll_name = content[0]
                    #原来的插入方式有重复，先插入api_dll depend，再查找dll_depend信息

          #          sql_dll_depend = \
          #              r"insert into t_dll_depend " \
          #              r"(dependent_version, dependent_name, dependence_version, dependence_name) " \
          #              r"values " \
          #              r"(%d, '%s', %d, '%s')" % \
          #              (2, dll_name, 2, depend_dll_name)
          #          sql_dll_depend_list.append(sql_dll_depend)

                if len(content) == 3:
                    api_name = content[1]
                    load_type = content[2]
                     
                    #在t_dll_basic中匹配名字，加上后缀    

                    depend_dll_name = depend_dll_name.lower()             
                    depend_dll_name_2 = depend_dll_name+'%'      
                                                       
                    cursor.execute("SELECT d_name from t_dll_basic where d_name like (%s) and d_version_id = (%s)",[depend_dll_name_2,2] )   
                    res = cursor.fetchone()   
                    if res:
                        depend_dll_name = res[0]
                    else:
                        print "****"+depend_dll_name+"******"
                        depend_dll_name =depend_dll_name                       
                    sql_dll_api_depend = \
                        r"insert into t_dll_api_depend " \
                        r"(dependent_version, dependent_dll, dependence_version, dependence_dll, dependence_api, dependence_style) " \
                        r"values " \
                        r"(%d, '%s', %d, '%s', '%s', '%s')" % \
                        (2, dll_name, 2, depend_dll_name, api_name, load_type)
                    sql_dll_api_depend_list.append(sql_dll_api_depend)
            
    __run_sql(sql_dll_api_depend_list)    
    
def import_info_2():
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    connect.autocommit(0)
    cursor = connect.cursor()   
    sql_dll_depend_list = []
    # 从t_dll_api_depend表中查重去除重复信息，填入dll_depend表
    cursor.execute(r"select distinct dependent_dll,dependence_dll from t_dll_api_depend ") 
    res = cursor.fetchall() 
    for i in xrange(0,len(res)):
        print i
        item = res[i]
        #item = list(item)
        dll_name = item[0]
        depend_dll_name = item[1]
        print dll_name,depend_dll_name 
        sql_dll_depend = \
            r"insert into t_dll_depend " \
            r"(dependent_version, dependent_name, dependence_version, dependence_name) " \
            r"values " \
            r"(%d, '%s', %d, '%s')" % \
            (2, dll_name, 2, depend_dll_name)
        print sql_dll_depend
        sql_dll_depend_list.append(sql_dll_depend)  
    __run_sql(sql_dll_depend_list)
    
if __name__ == "__main__":
    export_info()
    import_info()
    import_info_2()
