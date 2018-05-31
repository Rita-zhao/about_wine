#!/usr/bin/python
#-*-coding:utf-8-*-

import xlrd
import MySQLdb


###接口匹配/原始方式
'''
def imple_couple():
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    try:
        connect.autocommit(0)
        cursor = connect.cursor()  

        cursor.execute(r"select MIN(ID) from t_api_basic_2") 
        minn = cursor.fetchone()
        if minn:
            minn = minn[0]
        else:
            print "no min_data in t_api_basic_2"
        cursor.execute(r"select MAX(ID) from t_api_basic_2") 
        maxx = cursor.fetchone()
        if maxx:
            maxx = maxx[0]
        else:
            print "no max_data in t_api_basic_2"       

        #循环读取接口信息
      #  print minn,maxx
        for i in xrange(minn,maxx+1):
            cursor.execute(r"select a_name,d_name from t_api_basic_2 where id = (%s)",[i]) 
            res = cursor.fetchone()
            if res:
                print res
                a_name = res[0].strip()
                d_name = res[1].strip()
                index_ = d_name.rfind(".")
                if index_ == -1:
                    d_name = d_name
                else:
                    d_name = d_name[:index_]
                print "****",a_name,d_name,"*****"
                #循环匹配接口有没有被测试到
                cursor.execute(r"select imple from winetest_data where dll_name = (%s)",[d_name])
                res_ = cursor.fetchall()
                print "++++",res_,"++++++"
                if a_name in res_:
                    cursor.execute(r"update t_api_basic_2 set flag= (%s) where id = (%s)",[1,i])
                else:
                    continue

        connect.commit()    

    finally:
        connect.close()    
'''

def imple_couple_():
    i = 0
    j = 0
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    try:
        connect.autocommit(0)
        cursor = connect.cursor()  
        cursor.execute("select distinct dll_name,imple from winetest_data_bak")  
        rows = cursor.fetchall()
        ###循环读取winetest信息
      #  print minn,maxx
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
            ###匹配接口有没有被测试到
            #print j,"****",dll_name,imple,imple_,"****"
            cursor.execute(r"select id from t_api_basic_2 where binary d_name = (%s) and (binary a_name = (%s) or binary a_name = (%s) or binary a_name = (%s)) ",[dll_name,imple,imple_,imple__])
            res_ = cursor.fetchone()
            #print res_
            if res_:
                j+=1
                id = res_[0]
                cursor.execute(r"update t_api_basic_2 set flag= (%s) where id = (%s)",[1,id])
            else:
              #  print i
                cursor.execute(r"select * from com_data where name = (%s)",[imple])
                res = cursor.fetchone()
                if res:
                    i+=1
                    cursor.execute(r"update com_data set flag_couple = (%s) where name = (%s)",[1,imple])
                else:
                    if '_' in imple:
                        imple = imple.split('_')
                        com = imple[0].strip()
                        fun = imple[1].strip()
                        fun = "\'"+fun+"\'"
                        print "com: ",com,"fun: ",fun
                        cursor.execute(r"select id,funlist from com_data where name = (%s)",[com])
                        res = cursor.fetchone()
                        if res:
                            id = res[0]
                            funlist = res[1]
                            print "id: ",id,"funlist: ",funlist
                            if fun in funlist:
                                i+=1
                                cursor.execute(r"update com_data set flag_couple = (%s) where id = (%s)",[1,id])
                            else:
                                continue
                    else:
                        
                        continue
            
        connect.commit()    
        
    finally:
        connect.close()    
    
    


if __name__ == "__main__":
    imple_couple_()