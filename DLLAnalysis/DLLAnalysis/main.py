# -*- coding: utf-8 -*-
from models import DLL, API
from DLLAnalyser import DLLAnalyser
import openpyxl
import MySQLdb
import traceback

Database = "dk_construction"

def main_database():
    wine_dll_analyser = DLLAnalyser()
    wine_dll_analyser.load_from_html(r"C:/Users/iscas/Desktop/Wingear/dll&api/html/html/", "wine")
    wine_dll_analyser.add_info_from_spec(r"C:/Users/iscas/Desktop/Wingear/dll&api/wine-2.0.2/wine-2.0.2/dlls/")
    __insert_dll_analyser(wine_dll_analyser, "wine-dll")
   # __insert_dll_depend(wine_dll_analyser, "wine-dll")
    print "wine finish."

def __insert_dll_analyser(da, version_name):
    #dll_analyser = DLLAnalyser()
    dll_analyser = da
    try:
        connect = MySQLdb.connect(host="127.0.0.1", port=3306, \
                                  user="root", passwd="iscasztb", \
                                  db=Database)
        connect.autocommit(0)
        cursor = connect.cursor()
        cursor.execute("select max(ID) from t_dll_basic")
        res = cursor.fetchone()
        res = res[0]
        if res:
            id_ = res + 1
        else:
            id_ = 1
       # print id_

        cursor.execute("select max(ID) from t_api_basic")
        res = cursor.fetchone()
        res = res[0]
        if res:
            id2_ = res + 1
        else:
            id2_ = 1
       # print id2_    
        
        version_id = -1
        if version_name == "wine-dll":
            version_id = 1
#        elif version_name == "windowsXP":
#            version_id = 3
        elif version_name == "windows7":
            version_id = 2
#        elif version_name == "windows8":
#            version_id = 5
#        elif version_name == "windows10":
#            version_id = 6
        '''
        for dll in dll_analyser.dlls.values():
            dll.id = id_
            #锟斤拷锟斤拷dll锟斤拷锟斤拷锟斤拷锟叫讹拷dll锟斤拷缀
            str=dll.name
            suffix = str[str.find(".")+1:]
 #           print suffix
            cursor.execute("INSERT INTO t_dll_basic (id, d_version_id,  d_name, d_suffix, d_category,d_description) "
                           "VALUES (%d, %d, '%s', '%s', '%s', '%s')" % (dll.id, version_id, dll.name, suffix, " ",dll.intro.replace("'", r"\'"), ))
            id_ += 1
        '''
        for dll in dll_analyser.dlls.values():
            for api in dll.api_list:
                api.id = id2_
                #锟介看wine锟斤拷api锟斤拷实锟斤拷状态
                str=api.state
                str=str[str.find(":")+1:]
             #   print str
                if str.startswith("stdcall") or str.startswith(" stdcall"):
                    state = "stdcall"
                elif str.startswith("stub") or str.startswith(" stub"):
                    state  = "stub"
                elif str.startswith("pascal") or str.startswith(" pascal"):
                    state  = "pascal"
                elif str.startswith("cdecl") or str.startswith(" cdecl"):
                    state  = "cdecl"
                elif str.startswith("varargs") or str.startswith(" varargs"):
                    state  = "varargs"           
                elif str.startswith("thiscall") or str.startswith(" thiscall"):
                    state  = "thiscall"  
                elif str.startswith("not documented") or str.startswith(" not documented"):
                    state  = "not documented" 
                elif str.startswith("forward") or str.startswith(" forward"):
                    state  = "forward"                    
                else:
                    state  = " "
            #    print state
                #锟接诧拷锟斤拷锟斤拷去锟斤拷锟斤拷锟斤拷注锟斤拷
                str = api.params.__str__()
                parameters = "{"
            #    print str
                for s in eval(str).keys():
                    parameters+=s+","
                if len(parameters) > 1:
                    parameters=parameters[:len(parameters)-1]
                else:
                    parameters = parameters
                parameters+="}"  
            #    parameters=eval(str).keys()
        
            #    print parameters
                print "INSERT INTO t_api_basic "\
                               "VALUES (%d, %d, '%s', '%s', '%s', '%s', '%s', '%s')" %\
                               (api.id, version_id, dll.name, api.name.replace("'", r"\'"), parameters.replace("'", r"\'"), api.params.__str__().replace("'", r"\'"), state, api.description.replace("'", r"\'"),\
                                )
                cursor.execute("INSERT INTO t_api_basic "
                               "VALUES (%d, %d, '%s', '%s', '%s', '%s', '%s', '%s')" %
                               (api.id, version_id, dll.name, api.name.replace("'", r"\'"), parameters.replace("'", r"\'"), api.params.__str__().replace("'", r"\'"), state, api.description.replace("'", r"\'"),
                                ))
                id2_ += 1

        connect.commit()
        connect.close()
    finally:
#        connect.close()
        print "end insert dll&api basic"      
        
if __name__ == "__main__":
#    __insert_t_version()
#    __insert_t_source()
    main_database()