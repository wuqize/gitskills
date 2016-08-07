# -*- coding: utf-8 -*-
"""
Created on Sun Aug 07 20:26:55 2016

@author: wuqilv
"""


import requests
import re
import time
import cStringIO
from PIL import Image
import socket
import datetime

MaxSearchPage = 20 # 收索页数
CurrentPage = 0 # 当前正在搜索的页数
DefaultPath = "c:/baidupictures" # 默认储存位置
NeedSave = 0 # 是否需要储存

content = ""


def detectfacefeature(serverip, port, imagedata):
        try:
             image = Image.open(cStringIO.StringIO(imagedata))
             outfile = cStringIO.StringIO()
             image.save(outfile,'JPEG')
             converted_data = outfile.getvalue()
             #outfile.truncate()
             outfile.close()
             faceimagesize = len(converted_data)
             faceimage = converted_data
        except:
             return 0
        success = 0       
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((serverip, port))
    
        #包大小
        packsize=0

        #头部信息
        companyid = 3
        appid = 2
        appkey = "group01"
        locationid = 11
        
        #尾部信息
        checkcode='C48BB477A68D4F7D'
    
        time.sleep(0.05)
    
        tmp='%ld_%ld_%s_%ld_270_%ld_' % (companyid, appid, appkey, locationid, faceimagesize)
    
        t= tmp.encode('utf-8')
    
        #实际包大小
        t1 = t + faceimage + '_' + checkcode
        
        packsize = len(t1)
        tmp1='%ld_' %packsize
    
        #实际包大小 + 包长度
        packsize= packsize + len(tmp1)
        tmp1='%ld_' %packsize
        s = tmp1 + t1
        #print s
        temp = sock.send(s)
        #send_begin_time = datetime.datetime.now()+datetime.datetime.now().microsecond
        send_time = datetime.datetime.now()
        send_begin_time = time.time()
        #time.sleep(2)
        resp = sock.recv(1024)
        print resp
        sock.close()
        return resp

def imageFiler(content): # 通过正则获取当前页面的图片地址数组
        return re.findall('"objURL":"(.*?)"',content,re.S)

def nextSource(content): # 通过正则获取下一页的网址
        next = re.findall('<div id="page">.*<a href="(.*?)" class="n">',content,re.S)[0]
        print("---------" + "http://image.baidu.com" + next) 
        return next

def spidler(source):
        global content
        
        while 1:
             try:
                 content = requests.get(source).text  # 通过链接获取内容
                 break
             except:
                 print "get content faild !"
                 time.sleep(2)
                 

        imageArr = imageFiler(content) # 获取图片数组
        global CurrentPage
        print("Current page:" + str(CurrentPage) + "**********************************")
        for imageUrl in imageArr:
            print(imageUrl)
            if len(imageUrl.rsplit(".",1))>=2 and (imageUrl.rsplit(".",1)[1] not in ["JPEG","jpg", "png", "bmp","BMP","PNG"]):
                continue
            global  NeedSave
            if NeedSave:  # 如果需要保存保存
               global DefaultPath
               try:                
                    picture = requests.get(imageUrl,timeout=10) # 下载图片并设置超时时间,如果图片地址错误就不继续等待了
               except:                
                    print("Download image error! errorUrl:" + imageUrl)                
                    continue            
               pictureSavePath = DefaultPath + imageUrl.replace('/','')[5:] # 创建图片保存的路径
               facepictrue = picture.content
               if len(facepictrue) > (1024*1024-150):
                    continue
               #fp = open(pictureSavePath,'wb') # 以写入二进制的方式打开文件
               #fp.write(picture.content)
               #fp.close()
               
               resp = "0"
               try:
                    resp = detectfacefeature("192.168.17.2", 90, facepictrue)
               except Exception,e:
                    print e
               try:
                    temp = resp[0]
               except:
                    temp = "0"
               if temp in ["1","2","3","4","5","6","7"]:
                    with open(pictureSavePath, "wb") as f:
                         f.write(facepictrue)
               
                    if  len(resp.split("_eric")) < 2:
                         resp = "0"
                    with open("log.txt","a") as f:
                         f.write("%s__%s__%s\n"%(CurrentPage,imageUrl.replace('/','')[5:],resp.split("_eric")[0]))
                    print "Success !"
               time.sleep(2)
             

def  beginSearch(page=1,save=0,savePath="c:/baidupictures/"): # (page:爬取页数,save:是否储存,savePath:默认储存路径)
        global MaxSearchPage,NeedSave,DefaultPath,content,CurrentPage
        MaxSearchPage = page
        NeedSave = save
        DefaultPath = savePath

        #key = raw_input("Please input you want search ")
        StartSource = "https://image.baidu.com/search/flip?tn=baiduimage&ie=gbk&word=%D5%FD%C3%E6%C8%CB%C1%B3&ct=201326592&v=flip" # 分析链接可以得到,替换其`word`值后面的数据来收索关键词
        spidler(StartSource)
        
        if CurrentPage <= MaxSearchPage:
            if nextSource(content):
                CurrentPage += 1                                         
                spidler("http://image.baidu.com" + nextSource(content)) # 爬取完毕后通过下一页地址继续爬取
                
        
if __name__ == "__main__":
	beginSearch(page=10000,save=1)
		