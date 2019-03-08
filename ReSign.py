# -*- coding: utf-8 -*-
# author:kongyanan
# date:2019-03-08

# 功能实现：参考https://www.jianshu.com/p/2070041b5efa
# Certificates文件下存放相应证书的embedded.mobileprovision，entitlements.plist（考虑以后可能会有多证书打签名包）
# 1.安装好相应的证书到mac中
# 2.把打好的adhoc包放到此文件夹下
# 3.执行ReSign.py
# 

#出现问题：xcrun: error: unable to find utility "PackageApplication", not a developer tool or in PATH，参考下面链接修改
# https://www.cnblogs.com/Crazy-ZY/p/7115076.html

import os
import sys
import shutil
import subprocess
import commands

# 证书名称，必填
certificate = "BINDOW"
certificateName = "\"iPhone Distribution: "+certificate+"\""
#注入的库文件
hookLib = "hook.dylib"
# 测试库文件使用，不用时，请删掉 ********
# sourcePath="/Users/wangmeili/Library/Developer/Xcode/DerivedData/hook-dgaqzlolyfusmihfqgtseukonjlr/Build/Products/Debug-iphoneos/hook.dylib"
# targetPath="/Users/wangmeili/Documents/work/ReSignTools/hook.dylib"
# open(targetPath, "wb").write(open(sourcePath, "rb").read())

os.chdir(os.path.dirname(os.path.realpath(__file__)))
# 执行系统命令
def execSys(cmd):
	print cmd
	(status, output) = commands.getstatusoutput(cmd)
	print status,output

# 获取ipa名称
def getFileName(path,endstr):
	files = os.listdir(path)
	for file in files:
		if file.endswith(endstr):
			return file

# 检查文件是否存在
def checkFileExits(path):
	if not os.path.exists(path):
		print "error:未找到文件夹："+path
		sys.exit()

# 逆向注入代码
def hook(appName):
	shutil.copy(hookLib,  "Payload/"+appName+"/"+hookLib)
	execSys("./yololib Payload/%s/%s %s"%(appName,appName[:-4],hookLib))
	execSys("codesign -f -s %s %s" % (certificateName,"Payload/"+appName+"/"+hookLib))

if __name__ == '__main__':
	# 清理过名的包
	execSys("rm *-Resigned.ipa")
	ipaName = getFileName(os.getcwd(),".ipa")
	if not ipaName:
		print "error:请拷贝ipa包到此文件夹下！"
		sys.exit()
	resignName = ipaName[:-4]+"-Resigned.ipa"
	# 清理上次遗留的文件
	if(os.path.exists("Payload")):
		shutil.rmtree("Payload")
	if(os.path.exists("__MACOSX")):
		shutil.rmtree("__MACOSX")

	# 解压ipa
	execSys("unzip "+ipaName)
	# 程序名称app
	appName = getFileName("Payload",".app")
	# 删除原签名文件
	shutil.rmtree("Payload/"+appName+"/_CodeSignature")
	# 检查是否有证书相关的信息,
	checkFileExits("Certificates/"+certificate)
	checkFileExits("Certificates/"+certificate+"/embedded.mobileprovision")
	checkFileExits("Certificates/"+certificate+"/entitlements.plist")
	# 注入脚本(如果不需要，可以去掉这一步骤)
	hook(appName)
	# 拷贝文件
	open("Payload/"+appName+"/embedded.mobileprovision", "wb").write(open("Certificates/"+certificate+"/embedded.mobileprovision", "rb").read())
	# 重新签名
	print "Resign start:"
	entitlements = "Certificates/"+certificate+"/entitlements.plist"
	appPath = "Payload/"+appName
	execSys("codesign -v -vvvv -f -s "+certificateName+" --entitlements "+entitlements+" "+appPath)
	print "build resign ipa:"
	execSys("xcrun -sdk iphoneos PackageApplication -v "+appPath+" -o "+os.path.join(os.getcwd(),resignName))
	# 清理垃圾文件
	if(os.path.exists("Payload")):
		shutil.rmtree("Payload")
	if(os.path.exists("__MACOSX")):
		shutil.rmtree("__MACOSX")

	print "Resign finish!"

