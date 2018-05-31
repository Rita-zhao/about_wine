#!/usr/bin/python
#-*-coding:utf-8-*-

import xlrd
import MySQLdb

def imple_couple_():

    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    try:
        connect.autocommit(0)
        cursor = connect.cursor()  
        cursor.execute("select distinct dll_name,imple from winetest_data_bak")  
        rows = cursor.fetchall()
        ###循环读取winetest信息
        for row in rows:
            dll_name = row[0].strip()
            if "." in dll_name:
                dll_name = dll_name
            else:
                dll_name = dll_name+".dll"            
            imple = row[1].strip()
            if imple.startswith("p"):
                index = imple.find("p")
                imple_ = imple[index+1:]
            elif imple.startswith("I"):
                index = imple.find("I")
                imple_ = imple[index+1:]   
            elif imple.startswith("__"):
                index = imple.find("_")
                imple_ = imple[index+1:]                  
            else:
                imple_ = imple
            #api_basic中出现了存储错误de问题，部分以__开头的API缺少了第一个_
            if imple_.startswith("__"):
                index_ = imple_.find("_")
                imple__ = imple_[index_+1:]
            else:
                imple__ = imple_
            cursor.execute(r"select id from t_api_basic_2 where binary d_name = (%s) and (binary a_name = (%s) or binary a_name = (%s) or binary a_name = (%s)) ",[dll_name,imple,imple_,imple__])
            res_ = cursor.fetchone()
            if res_:
                continue
            else:
                cursor.execute(r"select * from com_data where name = (%s)",[imple])
                res = cursor.fetchone()
                if res:
                    continue
                else:
                    if '_' in imple:
                        imple = imple.split('_')
                        com = imple[0].strip()
                        fun = imple[1].strip()
                        fun = "\'"+fun+"\'"
                        cursor.execute(r"select id,funlist from com_data where name = (%s)",[com])
                        res = cursor.fetchone()
                        if res:
                            continue
                        else:
                            print row
                            row = str(row)
                            with open(r"C:/Users/iscas/Desktop/com.log", "a") as f:
                                f.write("/t".join([row])+"\n")
                            continue
                    else:
                        continue
            
        connect.commit()    
        
    finally:
        connect.close()    
    
    


if __name__ == "__main__":
    imple_couple_()