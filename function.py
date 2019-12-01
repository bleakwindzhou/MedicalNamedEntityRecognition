# -*- coding: utf-8 -*-
import pymssql
import pandas as pd
import re
from lxml import etree
'''
class product():
    def __init__(self, product_name, product_SKU, product_class_num = 'na'):
        self.product_name = str(product_name)
        self.product_SKU = str(product_SKU)
        self.product_class = str(product_class_num)

    def get_parameter(self, **kwargs):
'''

class sql_find():
    
    def __init__ (self, database='ZI_DataBase', localhost=True):
        if localhost:
            self.conn = pymssql.connect(host='localhost', user='********',password='********',database=database,autocommit=True)
        else:
            self.conn = pymssql.connect(host='***.**.***.***', user='********',password='*********',database=database,autocommit=True)
        self.cursor = self.conn.cursor()

class mysql_find():
    
    def __init__ (self, database='ZI_DataBase', localhost=True):
        if localhost:
            self.conn = pymssql.connect(host='localhost', user='********',password='********',database=database,autocommit=True)
        else:
            self.conn = pymssql.connect(host='**.***.***.***', user='********',password='********',database=database,autocommit=True)
        self.cursor = self.conn.cursor()
    '''
    def execute(self, sql_sentence):
        self.cursor.execute(sql_sentence)
        return self.cursor
    '''

def BN(brand):
    brand = str(brand)
    try:
        country = brand.split('[')[1].split(']')[-2]
        brand = brand.replace(country,'')
    except IndexError:
        pass
    res = re.findall(r'[0-9\u4E00-\u9FA5]', brand)
    new_res = ''.join(res)
    if new_res.isdigit():
        new_res = ''
	#print(len(new_res))
    if len(new_res) == 0:
        res1 = re.findall(r'[a-zA-Z0-9]', brand)
        new_res = ''.join(res1)
        new_res = new_res.upper()
    return new_res
    
class Index(object):
    def __init__(self, number=50, decimal=2):
        """
        :param decimal: 你保留的保留小数位
        :param number: # 号的 个数
        """
        self.decimal = decimal
        self.number = number
        self.a = 100/number   # 在百分比 为几时增加一个 # 号
 
    def __call__(self, now, total):
        # 1. 获取当前的百分比数
        percentage = self.percentage_number(now, total)
 
        # 2. 根据 现在百分比计算
        well_num = int(percentage / self.a)
        # print("well_num: ", well_num, percentage)
 
        # 3. 打印字符进度条
        progress_bar_num = self.progress_bar(well_num)
 
        # 4. 完成的进度条
        result = "\r%s %s" % (progress_bar_num, percentage)
        return result
 
    def percentage_number(self, now, total):
        """
        计算百分比
        :param now:  现在的数
        :param total:  总数
        :return: 百分
        """
        return round(now / total * 100, self.decimal)
 
    def progress_bar(self, num):
        """
        显示进度条位置
        :param num:  拼接的  “#” 号的
        :return: 返回的结果当前的进度条
        """
        # 1. "#" 号个数
        well_num = "#" * num
 
        # 2. 空格的个数
        space_num = " " * (self.number - num)
 
        return '[%s%s]' % (well_num, space_num)

class tool():
    def __init__(self):
        self.peijian_table = pd.read_excel('是否需要配件.xlsx')
        self.brand_table = pd.read_excel('品牌对应表.xlsx')
    
    def judge_brand(self, brand, brandcode_original):
        if brandcode_original == '没有对应指数品牌':
            BRANDID = '没有对应指数品牌'
            for ID,Chinese_brand,English_brand in zip(self.brand_table['ID'], self.brand_table['中文品牌'], self.brand_table['英文品牌']):
                if brand == Chinese_brand:
                    BRANDID = str(ID).zfill(5)
                    return BRANDID
                elif BN(brand) == English_brand:
                    BRANDID = str(ID).zfill(5)
                    return BRANDID
        else:
            BRANDID = str(brandcode_original).zfill(5)[-5:]
        return BRANDID
    
    def judge_peijian(self, data_table):
        ispeijian_lyst = []
        isunique_lyst = []
        for class_code in data_table['指数子类编码']:
            mark = '0'
            mark2 = '0'
            class_code = str(class_code).zfill(4)
            if class_code != '没有匹配的指数子类编码':
                for categorycode, ispeijian, isunique in zip(self.peijian_table['categorycode'], self.peijian_table['ispeijian'], self.peijian_table['isunique']):
                    if class_code == str(categorycode).zfill(4):
                        if str(ispeijian) != '0':
                            mark = '1'
                        if str(isunique) != '0':
                            mark2 = '1'
                        break
                ispeijian_lyst.append(mark)
                isunique_lyst.append(mark2)
            else:
                ispeijian_lyst.append(mark)
                isunique_lyst.append(mark2)
        #print(len(ispeijian_lyst), len(data_table['指数子类编码']))
        data_table['有无配件'] = ispeijian_lyst
        data_table['型号_only'] = isunique_lyst
        return data_table

def judge_unit(string):
    unit_list = {'MM','CM', 'DM', 'ML', 'W', 'KW'}
    if not string[0].isdigit():
        return True
    m = 0
    for char in string:
        if char.isdigit() or char == '.':
            m += 1
            continue
        elif char.isalpha():
            if string[m:].upper() in unit_list:
                return False
            else:
                return True
    return True

def type_extract_JD(name, params, brand):
    #params = eval(params)
    try:
        brand_remove = re.findall(r"[A-Za-z0-9]+", brand)[0].upper()
    except IndexError:
        brand_remove = '没有英文品牌！'
    param_xinghao = 'NA'
    if '产品型号' in params:
        param_xinghao = params['产品型号']
    if '型号' in params:
        param_xinghao = params['型号']
    elif r'\t型号\t' in params:
        param_xinghao = params[r'\t型号\t']
    name_xinghao_lyst = list(filter(lambda x: len(x) >= 2, re.findall(r"[A-Za-z0-9-+/.*]+", name)))
    for i in range(len(name_xinghao_lyst)):
        name_xinghao_lyst[i] = name_xinghao_lyst[i].upper()
    try:
        name_xinghao_lyst.remove(brand_remove)
    except ValueError:
        pass
    if len(name_xinghao_lyst) == 0:
        #type_lyst.append(param_xinghao.upper())
        return param_xinghao.upper()
    else:
        if param_xinghao in name_xinghao_lyst:
            #type_lyst.append(param_xinghao.upper())
            return param_xinghao.upper()
        else:
            xinghao_data = max(name_xinghao_lyst, key=len)
            for xinghao in name_xinghao_lyst:
                if len(xinghao) > 2 and '*' not in xinghao and judge_unit(xinghao):
                    xinghao_data = xinghao
                    break
            if not judge_unit(xinghao_data):
                xinghao_data == 'NA'
            #type_lyst.append(xinghao_data.upper())
            return xinghao_data


def type_extract(name, params):
    #params = eval(params)
    param_xinghao = 'NA'
    if '型号' in params:
        param_xinghao = params['型号']
    elif r'\t型号\t' in params:
        param_xinghao = params[r'\t型号\t']
    name_xinghao_lyst = list(filter(lambda x: len(x) >= 2, re.findall(r"[A-Za-z0-9-+/.*]+", name)))
    if len(name_xinghao_lyst) == 0:
        #type_lyst.append(param_xinghao.upper())
        return param_xinghao.upper()
    else:
        if param_xinghao in name_xinghao_lyst:
            #type_lyst.append(param_xinghao.upper())
            return param_xinghao.upper()
        else:
            xinghao_data = max(name_xinghao_lyst, key=len)
            for xinghao in name_xinghao_lyst:
                if len(xinghao) > 2 and '*' not in xinghao and judge_unit(xinghao):
                    xinghao_data = xinghao
                    break
            if not judge_unit(xinghao_data):
                xinghao_data == 'NA'
            #type_lyst.append(xinghao_data.upper())
            return xinghao_data.upper()

def param_load(product_id, xml_string):
    """
    传入sku，和xml原始代码
    :param product_id:sku
    :param xml_string:xml数据
    :return:csv
    """
    xml_str = etree.HTML(xml_string)
    #title = xml_str.xpath("//th[@class='tdTitle']")
    secend = xml_str.xpath("//td[@class='tdTitle']")
    zhi = xml_str.xpath("//tr//td[position()>1]")
    data_dict = {}
    for j, k in zip(secend, zhi):
        #item = i.xpath("./text()")[0]
        sec = j.xpath("./text()")[0]
        value = k.xpath("./text()")[0]
        data_dict[sec] = value
    return data_dict

if __name__ == '__main__':
    sqlserver = sql_find('ZI_BAK', True)
    sqlserver.cursor.execute("select * from ZI_Price_Quote where  productcode = '0506003750007'")
    print(sqlserver.cursor.fetchall())

    
