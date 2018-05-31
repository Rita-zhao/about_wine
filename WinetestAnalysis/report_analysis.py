#!/usr/bin/python
#-*-coding:utf-8-*-

import re
import MySQLdb
import time
import sys  
import codecs  

def report_analysis():
   # line_=""
    count = 1
    file = ""
    sql_insert_list=[]
    '''
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    '''
    try:
        #cursor = connect.cursor()
   
#    sql_insert_list = []
        with open("C:/Users/iscas/Desktop/suceeandfail.tmp",'r') as f:
            for line in f:
                print line 
                if " start " in line and "-" in line:
                    index = line.find("start")
                    line = line[index+5:]
                    index_ = line.rfind("-")
                    line = line[:index_]
                    file = line.strip()
                    print file
                
                elif ".c" in line and ("Test " in line or "Tests " in line):
                    line = line.split(":")
                    line_num = line[1]
                    result = line[2]
                    if len(line) > 3:
                        descri = line[3]
                    else:
                        descri = ""
                    ###这样要进行两千万次查找，效率很低，因此在后面重新写了函数进行查找
                    '''
                    cursor.execute("select imple from winetest_data where path = (%s) and line_num = (%s)",[file,line_num])
                    res = cursor.fetchone()   
                    if res:
                        imple = res[0]
                    '''
                    sql_insert = "insert into winetest_report (file, line_num, result, descri,count)" \
                                        "VALUES ('%s', '%s', '%s', %s', '%s') on duplicate key update count=count+1" % (
                                                     file, line_num, result, descri.replace("'", r"\'"), count)
                    sql_insert_list.append(sql_insert)
                else:
                    continue
        f.close
    finally:
        __run_sql(sql_insert_list)

###先存report的数据再更新imple信息
def update_imple():
    print "*****update_start****"
    sql_insert_list=[]
    file_base = ''
    count_success = 0
    count_todo = 0
    count_fail = 0
    count_skip = 0
  #  txt_name = 'winetest_report_after'  #  path = 'C:/User/iscas/Desktop/' + txt_name + '.txt' 
 #   print path
 #   paper_keywords = codecs.open(path.decode('utf-8'), 'wb',encoding="utf-8")      
    paper_keywords = open('C:/Users/iscas/Desktop/winetest_report_after','w')    
    
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")    
    try:
        cursor = connect.cursor()    
        cursor.execute("select file,line_num,result,descri,count from winetest_report_copy")  
        rows = cursor.fetchall()
        for row in rows:
            file = row[0]
            line_num = row[1]
        #    print file,line_num
            result = row[2].strip('\n')
            descri = row[3]
            count = row[4]
            cursor.execute("select imple from winetest_data where path=(%s) and line_num=(%s)",[file,line_num]) 
            imple = cursor.fetchone()
            if imple:
                imple = imple[0]
            else:
                imple = ''
                
            #####t统计数据：一个文件所有的测试数据t###########
            if file_base == file:
                if 'Test succeeded' in result:
                    count_success += count
                elif 'Tests skipped' in result:
                    count_skip += count
                elif 'Test marked todo' in result:
                    count_todo += count
                elif 'Test failed' in result:
                    count_fail += count
                else:
                    pass
            else:
                if file_base == '':
                    pass
                else:
                    test_all = count_success + count_todo + count_fail
                    summary = file_base +': '+ str(test_all)+' tests executed('+str(count_success)+' successed, '+str(count_todo)+' marked as todo, '+str(count_fail)+' failures), '+ str(count_skip)+' skipped.\n'
                    paper_keywords.write(summary)
                file_base = file
                if 'Test succeeded' in result:
                    count_success = count
                    count_todo = 0
                    count_fail = 0
                    count_skip = 0                     
                elif 'Tests skipped' in result:
                    count_skip = count
                    count_todo = 0
                    count_fail = 0
                    count_success = 0                     
                elif 'Test marked todo' in result:
                    count_todo = count
                    count_success = 0
                    count_fail = 0
                    count_skip = 0                     
                elif 'Test failed' in result:
                    count_fail = count  
                    count_todo = 0
                    count_success = 0
                    count_skip = 0                     
                else:
                    count_success = 0
                    count_todo = 0
                    count_fail = 0
                    count_skip = 0                    
            ##########################
            
         #   print imple
        #    cursor.execute("update winetest_report_copy set imple=(%s) where file = (%s) and line_num = (%s)",[imple, file, line_num])
            content = file+':'+str(line_num)+': '+imple+':' +result +' count = '+ str(count) +'\n'
            print content
            paper_keywords.write(content)
            
      #  connect.commit()
    finally:
        paper_keywords.close()  
        connect.close()         
        
'''
###将结果写入txt，方便进行diff比对        
def export_to_txt():
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")    
    try:
        cursor = connect.cursor()    
        
        #生成txt文件  
        txt_name = 'winetest_report_after'
        path = 'C:\\User\\iscas\\Desktop\\' + txt_name + '.txt' #\是一个特殊符号，需要转义  
        paper_keywords = codecs.open(path.decode('utf-8'), 'wb',encoding="utf-8") #在打开文件的时候，为了防止出现中文乱码的问题，用codecs.open去打开文件      
        #把结果先放到sql里面  
        sql = "SELECT * FROM winetest_report"  
        cur.execute(sql)  
        results = cur.fetchall()  
        #把结果写到txt里面  
        for result in results:  
            paper_keywords.write(result[0])  
    finally:
        cursor.close()  
        connect.close()  
        paper_keywords.close()      

'''
def __run_sql(sql_insert_list):
    connect = MySQLdb.connect(host="127.0.0.1", port=3306,
                              user="root", passwd="iscasztb",
                              db="dk_construction")
    try:
        connect.autocommit(0)
        cursor = connect.cursor()

        for sql in sql_insert_list:
            cursor.execute(sql)

        connect.commit()
    finally:
        connect.close()     
#    __run_sql(sql_insert_list)    

if __name__ == '__main__':
    start=time.asctime()
  #  report_analysis()
    update_imple()
  #  export_to_txt()
    end=time.asctime()
    print start,end