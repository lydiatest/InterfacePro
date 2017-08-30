#coding:utf-8

import configparser
import os
import sys
import requests
import re
import json

from util.express import I_Express

class _HttpObj(object):
	''' 封装http请求的参数和请求'''
	def __init__(self,method=None, url=None, data=None,headers=None):
		self.method=method
		self.url=url
		self.headers={} if headers is None else headers
		self.data={} if data is None else self.formatdict(data)

	
	#如果data是string转成dict类型
	def formatdict(self,data):
		return dict(self.formattuple(data))

	#如果data是string转成元祖
	def formattuple(self,data):
		if isinstance(data,(str)):
			return re.compile("([^=&]*)=([^=&]*)").findall(data)

	def run(self):
		if self.method.lower()=="get":
			self.status_code,self.res_body=self.get()
		else:
			self.status_code,self.res_body=self.post()

	def __call__(self,*args,**kwgs):
		self.run()


	def get(self):
		res=requests.get(self.url,params=self.data,headers=self.headers)
		return res.status_code,res.text

	def post(self):
		res=requests.post(self.url,data=self.data,headers=self.headers)
		return res.status_code,res.text


class I_TestCase(object):

	'''封装testcase'''
	def __init__(self,**kwgs):
		self.caseid=kwgs["caseid"]
		self.url=kwgs["host"]+"/"+kwgs["path"]
		self.data=kwgs["data"]
		self.method=kwgs["method"]
		self.res_type=kwgs["res_type"]
		self.checkpoint=kwgs["checkpoint"]
		self.expectresult=kwgs["expectresult"]

	def descript(self):
		return "test interface===="+self.url


class I_TestResult(object):
	'''封装测试结果'''
	def __init__(self,stream=sys.stdout):
		self.stream=stream

	def writeln(self,desc):
		self.stream.write(desc+"\n")
		self.stream.flush()



def loadTestCases(casefilepath):

	totalcount=0 #统计总的用例数
	test=[] #保存用例
	cpobj=configparser.ConfigParser()
	if os.path.isdir(casefilepath):
		for configfile in os.listdir(casefilepath):
			configfile=casefilepath+os.sep+configfile
			cpobj.read(configfile)
			'''解析并封装用例'''
			host=cpobj.get("env",cpobj.get("testrunner","env"))
			testcases=cpobj.get("testrunner","runner")
			for testcaseid in testcases.split(","):
				''''skip'''
				if cpobj.getboolean(testcaseid,"skip"):
					continue
				'''封装测试用例'''
				testdict={"caseid":configfile+":"+testcaseid}
				testdict["host"]="http://"+host

				for key,value in cpobj.items(testcaseid):
					testdict[key]=value
			
				test.append(I_TestCase(**testdict))
				totalcount=totalcount+1

	return totalcount,test

def runner(casefilepath,result=I_TestResult()):
	'''执行接口请求'''
	totalcount,test=loadTestCases(casefilepath)
	totalfailed=0
	totalsuccess=0

	result.writeln("================starttest======")
	for testcase in test:
		httpobj=_HttpObj(testcase.method,testcase.url,testcase.data)
		httpobj()
		try:
			if testcase.res_type=="json":
				express=I_Express(httpobj.res_body,testcase.checkpoint,testcase.res_type)
				actual_result=express.exec()

			else:
				express=I_Express(httpobj.res_body,testcase.checkpoint,testcase.res_type)
				actual_result=express.exec()

			if(str(actual_result).lower()==str(testcase.expectresult).lower()):
				result.writeln("sucess======"+testcase.caseid)
				totalsuccess=totalsuccess+1
			else:
				result.writeln("fail======"+testcase.caseid)
				totalfailed=totalfailed+1
		except Exception as e:
			result.writeln("fail======"+testcase.caseid)
			totalfailed=totalfailed+1
			print(e)

	result.writeln("=============endtest======\n\
		======total:{total}==success:{success}==fail:{fail}\
		".format(total=totalcount,success=totalsuccess,fail=totalfailed))

					
if __name__=="__main__":
	runner(os.getcwd()+os.sep+"testData")

	
