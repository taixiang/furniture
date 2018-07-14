import requests
from bs4 import BeautifulSoup
import xlsxwriter
from io import BytesIO
from urllib.request import urlopen
import jieba
import re


def get_data():
    # 定义一个列表存储数据
    furniture = []
    # 用于存放家具名，后续用于生成词频
    title_all = ""
    # 分页数据获取
    for num in range(1, 9):
        url = "http://www.likoujiaju.com/sell/list-66-%d.html" % num
        response = requests.get(url)
        content = BeautifulSoup(response.content, "lxml")
        # 找到数据所在的div块
        sm_offer = content.find("div", class_="sm-offer")
        lis = sm_offer.ul.find_all("li")
        # 遍历每一条数据
        for li in lis:
            # 价格
            price_span = li.find("span", class_="sm-offer-priceNum")
            price = price_span.get_text()
            # 名称
            title_div = li.find("div", class_="sm-offer-title")
            title = title_div.a.get_text()
            title_all = title_all + title + " "
            # 图片
            photo_div = li.find("div", class_="sm-offer-photo")
            photo = photo_div.a.img.get("src")
            # 详情链接
            href = photo_div.a.get("href")
            # 数组里每一项是元祖
            furniture.append((price, title, photo, href))
    # 排序
    furniture.sort(key=take_price, reverse=True)
    # 生成excel
    create_excel(furniture, title_all)


# 传参是列表的每一个元素，这里即元祖
def take_price(enum):
    # 取元祖的第一个参数--价格，处理价格得到数值类型进行比较
    price = enum[0]
    if "面议" in price:  # 面议的话就设为0
        return 0
    start = price.index("¥")
    end = price.index("/")
    new_price = price[start + 1:end]
    return float(new_price)


# 创建excel
def create_excel(furniture, title_all):
    # 创建excel表格
    file = xlsxwriter.Workbook("furniture.xlsx")
    # 创建工作表1
    sheet1 = file.add_worksheet("sheet1")
    # 定义表头
    headers = ["价格", "标题", "图片", "详情链接"]
    # 写表头
    for i, header in enumerate(headers):
        # 第一行为表头
        sheet1.write(0, i, header)
    # 设置列宽
    sheet1.set_column(0, 0, 24)
    sheet1.set_column(1, 1, 54)
    sheet1.set_column(2, 2, 34)
    sheet1.set_column(3, 3, 40)
    for row in range(len(furniture)):  # 行
        # 设置行高
        sheet1.set_row(row + 1, 180)
        for col in range(len(headers)):  # 列
            # col=2是当前列为图片，通过url去读取图片展示
            if col == 2:
                url = furniture[row][col]
                image_data = BytesIO(urlopen(url).read())
                sheet1.insert_image(row + 1, 2, url, {"image_data": image_data})
            else:
                sheet1.write(row + 1, col, furniture[row][col])

    # 创建工作表2，用于存放词频
    sheet2 = file.add_worksheet("sheet2")
    # 生成词频
    word_count(title_all, sheet2)

    # 关闭表格
    file.close()


# 生成词频
def word_count(title_all, sheet):
    word_dict = {}
    # 结巴分词
    word = jieba.cut(title_all)
    word_str = ",".join(word)
    # 处理掉特殊的字符
    new_word = re.sub("[ 【】-]", "", word_str)
    # 对字符串进行分割出列表
    word_list = new_word.split(",")
    for item in word_list:
        if item not in word_dict:
            word_dict[item] = 1
        else:
            word_dict[item] += 1
    # 对字典进行排序，按照数目排序
    val = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)
    # 写入excel
    for row in range(len(val)):
        for col in range(0, 2):
            sheet.write(row, col, val[row][col])


get_data()
