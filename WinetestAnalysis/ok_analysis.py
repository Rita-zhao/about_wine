#!/usr/bin/python
#-*-coding:utf-8-*-

import re
import MySQLdb
import linecache
import xlwt
import xlrd
def ok_analysis():
    f = open("C:/Users/iscas/Desktop/ok_log",'r')
 #   result = open("C:/Users/iscas/Desktop/winetest.xls",'w')
    wb= xlwt.Workbook()
    ws= wb.add_sheet('Sheet1')

    flag = 0
    j = 1
    for line in f.readlines():
      #  print line
        imple = []
        args = []
       # print "line:"+line
        ###����line������·����������
        line = line.split(":")
        path = line[0].strip('./')
        linenum = line[1]
        func = line[2]
        func =func.strip() 
        # print path
        # print linenum
        vari = func.split(",")
        if vari:
            vari = vari[0].strip()
           # print vari
            if "ok(" in vari:
                vari = vari.split("ok(")
            if "ok (" in vari:
                vari =vari.split("ok (")
               
         #   vari = vari.split("ok(")
         #   print vari 
            if len(vari) > 1: 
                vari = vari[1]
            else:
                continue
            
            if "SUCCEEDED" in vari:
                vari = vari.strip('SUCCEEDED')
                vari = vari.strip("(")
                vari = vari.strip(")")              
            if "==" or "!=" or "||" or "&&" or "->" or "<" in vari:
                vari = vari.split("==")
                vari = vari[0]
                vari = vari.split("!=")
                vari = vari[0]
                vari = vari.split("&&")
                vari = vari[0]
                vari = vari.split("||")
                vari = vari[0]
              #  vari = vari.split("->")
              #  vari = vari[0]
                vari = vari.split("->")
                vari = vari[0]
                vari = vari.split("<")
                vari = vari[0].strip()
                ###�ж�variǰ���Ƿ��У�
                if ">" in vari:
                    vari = vari.split(">")
                    vari = vari[0]
                if vari.startswith("!"):
                    vari = vari.strip("!")
                if vari.startswith("*"):
                    vari = vari.strip("*")
                    
            if "(" in vari:
                while vari.startswith("("):
                    vari = vari[1:]
                index_ = vari.find("(")
                imple = vari[:index_]
                vari=""
            else:
                ###���ļ���ȥƥ�������ֵ���
                p = r"%s\s*=\s*([^;]*);" % (vari)
                content = ""
            #        with open('/var/lib/mock/cdos-2.A-build-amd64/root/builddir/build/wine-2.0.1/'+path) as f:
                searchfile = "C:/Users/iscas/Desktop/Wingear/dll&api/wine-2.0.1/wine-2.0.1/" + path
                theline = []
                i = int(linenum)
            
                while i > int(linenum)-20:
                    templine = linecache.getline(searchfile,i-1)
                    print templine
                    if (" ok(" in templine or " ok (" in templine or ("\t"+"ok(") in templine or ("\t"+"ok (") in templine) and vari in templine:
                        break
                    elif " "+vari+" = " in  templine or "\t"+vari+" = " in templine or (("&"+vari) in templine and " = " in templine and "(" in templine):
                        imple.insert(0,templine)
                        break
                    else: 
#                        templine += templine
                        i = i-1                  
#                    if " "+vari in templine:
#                        imple.insert(0,templine)
                imple = str(imple)        
                print vari,imple
            
                ###��ƥ�䵽������н��б�������
                if vari + " = " in imple:
                    index_ = imple.find(vari + " = ")
                    imple = imple[index_:]
                    if ";" in imple:
                        index_ = imple.find(";")
                        imple = imple[:index_]
                    if "(" in imple:
                        index_ = imple.find("(")
                        args = imple[index_:]
                        imple = imple[:index_]
                    index_2 = imple.find("=")
                    imple = imple[index_2+1:].strip()
                elif "&"+vari in imple and " = " in imple and "(" in imple:
                    index_ = imple.find(" = ")
                    imple = imple[index_+1:]
                    if ";" in imple:
                        index_ = imple.find(";")
                        imple = imple[:index_]
                    if "(" in imple:
                        index_ = imple.find("(")
                        args = imple[index_:]
                        imple = imple[:index_]                
                else:
                    imple = '' 
                    vari = vari.strip('\'')
            
            print flag                
                
            
     #       if "*)" in vari:
     #           vari = vari.split("*)")
     #           vari = vari[1]          
     #       else:
     #           vari = ""
      #  if "(" or ")" or "[" or "]" in vari:
      #      vari=""
      #  print "vari:"+vari
      
      
        
        
        ###д����
        if 0 <= flag <= 65535:
          #  print "**"
            ws.write(flag,0,path)
            ws.write(flag,1,linenum)
            ws.write(flag,2,vari)
            ws.write(flag,3,imple)
            ws.write(flag, 4, str(args))
            flag = flag +1
        elif flag > 65535:
        #    print "++"
            j += 1
            flag = 0
            ws= wb.add_sheet('Sheet'+str(j))
            ws.write(flag,0,path)
            ws.write(flag,1,linenum)
            ws.write(flag,2,vari)
            ws.write(flag,3,str(imple))
            ws.write(flag, 4, str(args))
            flag += 1
        else:
            print "insert error"
            break

    wb.save('C:/Users/iscas/Desktop/winetest.xls')
  #  result.close
    f.close

if __name__ == '__main__':
    ok_analysis()