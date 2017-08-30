#coding:utf-8

import re
from common import ENVERIONMENT
from functools import reduce
import json,xml.etree.ElementTree as ET


INNERMETHOD=["m_save","m_format","m_get","m_len","m_in","m_notin"]


'''没有内置方法的异常'''
class NotFoundInnerMethod(Exception):
	'''
	使用了不存在的内置方法
	'''


'''封装内置函数方法,返回执行结果'''
class I_Express:

	#exe_body:执行对象
	#exe_expr:执行表达式
	def __init__(self,exe_body,exe_expr,body_type):
		self.exe_body=exe_body
		self.body_type=body_type
		self.exe_expr=exe_expr
		

    #执行表达式，并返回结果
	def exec(self,exe_expr=None):
		pattern=re.compile("([^\(]+)\((.*)\)")
		expr_list=pattern.findall(self.exe_expr if exe_expr is None else exe_expr)[0]
		expr_method=expr_list[0]
		expr_args=expr_list[1]
		if expr_method not in INNERMETHOD:
			raise NotFoundInnerMethod("the inner method "+expr_method+" is not found!")
	
		return getattr(self,expr_method)(expr_args)

	#保存数据到全局变量中:save
	def m_save(self,expr_args):
		exprlist=expr_args.split(";")
		for expr in exprlist:
			key,expr=re.findall("(.*?)=(.*)",expr)[0]
			ENVERIONMENT[key]=self.exec(expr)

	#格式化变量输出
	def m_format(self,expr_args):
		templist=[expr_args]
		keyslist=re.findall("\{(.*?)\}",expr_args)
		return reduce(lambda x,y: re.sub("\{"+y+"\}",ENVERIONMENT[y],x),templist+keyslist)


	#取长度
	def m_len(self,expr_args):
		if expr_args is None or expr_args=="":
			result=self.exe_body
		else:
			result=self.m_get(expr_args)
		if isinstance(result,(list,dict,tuple)):
			return len(result)
		elif isinstance(result,(str)):
			if not result.startswith("[") and result.startswith["{"]:
				result='"'+result+'"'
			return len(json.loads(result))

	#获取元素值
	def m_get(self,expr_args):
		argArr=expr_args.split(".")
		if self.body_type=="json":
			exe_body=json.loads(self.exe_body)
			result=exe_body
			for arg in argArr:
				if(str(arg).isdigit()):
					result=result[int(arg)]
				else:
					result=result.get(arg)
		elif self.body_type=="xml":
			result=root=ET.fromstring(self.exe_body)
			for arg in argArr:
				if(str(arg).isdigit()):
					result=result[int(arg)]
				elif str(arg).startswith("@"):
					result=result.attrib[arg[1:]]
				else:
					result=result.findall(arg)
			return result.text if isinstance(result,ET.Element) else result

		return str(result)
		
    #是否包含串
	def m_in(self,expr_args):
		return expr_args in str(self.exe_body)

	#是否不包含串	
	def m_notin(self,expr_args):
		return expr_args not in str(self.exe_body)

	


if __name__=="__main__":
	body={"name":"lydia","fav":["music","sleeping"],"info":{"age":"28","fav":["music","sleeping"]}}
	# expr=I_Express(body,"m_get(name)")
	# expr=I_Express(body,"m_get(info.fav.0)")
	# expr=I_Express(body,"m_len()")
	# expr=I_Express(body,"m_len(info.fav)")
	# expr=I_Express(body,"m_notin(info.fav)")
	# expr=I_Express(body,"m_in(name)")
	# expr=I_Express(body,"m_save(name=m_get(name);age=m_get(info.age))")
	# expr=I_Express(body,"m_format(name={name}&age={age})")
	# expr=I_Express(body,"m_test(1233344)")
	# print(expr.exec())
	print("{name} is welcoming".format(name="lydia"))







