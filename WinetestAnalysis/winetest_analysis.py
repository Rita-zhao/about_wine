#!/usr/bin/python
#-*-coding:utf-8-*-


import xlrd
import MySQLdb
import time

###从excel中读数据

def exl_read():
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    connect.autocommit(0)
    cursor = connect.cursor()    
        
    sql_insert_list = []
    bk = xlrd.open_workbook(r"C:\Users\iscas\Desktop\winetest.xls")
    for i in xrange(0,5):
        table = bk.sheets()[i]
        nrows = table.nrows
        #ncols = table.ncols    
        for i in range(1,nrows):
            row_data = table.row_values(i)
           # print row_data
            path = row_data[0].encode("utf-8") 
           # file = path.split("/")[-1]
            file = path[:]
            line_num = row_data[1].encode("utf-8")
            line_num = int(line_num)
            print path,line_num
            ###与动态数据库的匹配，暂时不要
            '''
            cursor.execute("select distinct result,descri from winetest_report where file = (%s) and line_num = (%s)",[file,line_num])
            res = cursor.fetchone()
            print "res: ",res
            if res:
                #res = res[0]
                result = res[0]
                descri = res[1]
            else:
                result = ""
                descri = ""   
                count = ""
            '''
            vari = row_data[2].encode("utf-8")
            imple = row_data[3].encode("utf-8")
            args = row_data[4].encode('utf-8')
            args = args.replace("'", r"")            
            imple = imple.replace("'", r"")
            if path.startswith("dlls") and imple != "[]":
                dll = path.split("/")
                dll = dll[1].encode("utf-8") 
                print path,dll,line_num,imple
                ###提取出来的都是unicode类型，插入数据库需进行类型转换
                sql_insert = "insert into winetest_data (path, dll_name, line_num, vari, imple)"\
                             "VALUES ('%s', '%s', '%s','%s','%s')" % \
                             (file, dll, line_num, vari, imple)
            #    sql_insert = "update winetest_report_copy set imple=(%s) where file = (%s) and line_num = (%s)",[imple,file, line_num]
                sql_insert_list.append(sql_insert)
             #   print dll
            
        
            else:
                print row_data
                continue
            
    __run_sql(sql_insert_list)
    
    
###存入数据库中
def __run_sql(sql_insert_list):
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    try:
        connect.autocommit(0)
        cursor = connect.cursor()

        for sql in sql_insert_list:
            print sql
            cursor.execute(sql)

        connect.commit()
    finally:
        connect.close()


if __name__ == "__main__":
    start=time.asctime()
    exl_read()
    end=time.asctime()
    print start,end