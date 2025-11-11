import pandas as pd
import numpy as np
import streamlit as st

st.markdown("""#### 数据捕获""")

st.markdown("""#### 代码示例""")

st.markdown("""##### 使用selenium获取百度地图路线信息""")

st.markdown("""####  真心希望面试官可以看一下，可以的话，帮忙回复一下，在这里我致以感谢""")

st.markdown(r"""
```python
from selenium import webdriver    
from selenium.webdriver.chrome.service import Service   
from selenium.webdriver.common.by import By   
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
from selenium.common import NoSuchElementException   
from PIL import Image    
from io import BytesIO   
import os   
import time 

def input_start_end(start,end):
    start_input = driver.find_element(By.CLASS_NAME,"route-start-input")
    start_input.send_keys(start)
    time.sleep(0.5)
    end_input = driver.find_element(By.CLASS_NAME,"route-end-input")
    end_input.send_keys(end)
    time.sleep(0.5)
    search_button = driver.find_element(By.ID,"search-button")
    search_button.click()
    time.sleep(1)

def show_search_box():
    route_button = driver.find_element(By.XPATH,"//div[@data-title='路线']")
    route_button.click()
    time.sleep(1)
    
def parse_route_basic(route_li_element):

    route_head_element = route_li_element.find_element(By.CLASS_NAME,"route-head")
    scheme_price_element = route_head_element.find_element(By.CLASS_NAME,"schemePrice")
    scheme_price = scheme_price_element.text
    scheme_tag = "无"
    try:
        scheme_tag_element = route_head_element.find_element(By.CLASS_NAME,"schemeTag")
        scheme_tag = scheme_tag_element.text
    except NoSuchElementException:
        print("路线无标签")
    scheme_name_element = route_head_element.find_element(By.CLASS_NAME,"schemeName")
    scheme_name_text = scheme_name_element.text
    scheme_name_text = scheme_name_text.replace(" → ","→")
    scheme_name_text_list = scheme_name_text.split(" ")
    scheme_name = scheme_name_text_list[-1]
    bus_time_element = route_head_element.find_element(By.CLASS_NAME,"bus_time")
    bus_time = bus_time_element.text
    bl_dis_element = route_head_element.find_element(By.XPATH,"//span[contains(@id,'blDis_')]")
    total_distance = bl_dis_element.text
    span_elements = route_head_element.find_elements(By.TAG_NAME,"span")
    walk_distance_element = span_elements[-1]
    walk_distance = walk_distance_element.text
    print(
        f"路线名称:{scheme_name},票价:{scheme_price},标签:{scheme_tag},耗时：{bus_time},距离:{total_distance},步行距离:{walk_distance}"
    )
    return scheme_name

def parse_route_detail(route_li_element):
    route_li_element.click()  # 展开详情
    time.sleep(1.5)
    table_element = route_li_element.find_element(By.CLASS_NAME,"info-table")
    tr_elements = table_element.find_elements(By.TAG_NAME,'tr')  # 查找每个tr标签
    print("以下是路线的分段路径：")
    for tr_element in tr_elements:
        data_type = tr_element.get_attribute("data-type")
        transfer_detail_element = tr_element.find_element(By.CLASS_NAME,"transferDetail")
        if data_type.strip() == 'walk':
            walk_distance_element = transfer_detail_element.find_element(By.CLASS_NAME,"walkdisinfo")
            walk_distance = walk_distance_element.text
            print(f"分段类型:{data_type},距离:{walk_distance}")
        elif data_type.strip() == 'bus':
            getonstop_element = transfer_detail_element.find_element(By.CLASS_NAME,"getonstop")
            start_station = getonstop_element.text
            getoffstop_element = transfer_detail_element.find_element(By.CLASS_NAME,'getoffstop')
            end_station = getoffstop_element.text
            kl_element = transfer_detail_element.find_element(By.CLASS_NAME,"kl")
            line_name_element = kl_element.find_element(By.CLASS_NAME,"line-name")
            line_name = line_name_element.text
            line_direction = '未提供'
            # 查找始末站点数据
            try:
                line_direction_element = kl_element.find_element(By.CSS_SELECTOR,".l-grey.direction")
                line_direction = line_direction_element.text
            except NoSuchElementException:
                print("公交或地铁路线没有提供始末站点数据")
            line_via_station_cnt_element = kl_element.find_element(By.CSS_SELECTOR,".cs.tf")
            line_via_station_cnt = line_via_station_cnt_element.text
            print(f"分段类型:{data_type},路线名:{line_name},上车站点:{start_station},下车站点:{end_station},"
                f"线路始末站:{line_direction},途径站点数:{line_via_station_cnt}")
        else:
            print(f"未知的交通类型:{data_type=}")

def screenshot_line(scheme_name):
    mask_element = driver.find_element(By.ID,"mask")
    map_img_bytes = mask_element.screenshot_as_png  # 获取图片的字节数据
    img_file_dir = f"map_images/{start}-{end}"
    if not os.path.exists(img_file_dir):
        os.makedirs(img_file_dir)
        print(f"已创建图片目录:{img_file_dir}")
    image_obj = Image.open(BytesIO(map_img_bytes))
    img_file_path = f"{img_file_dir}/{scheme_name}.png"
    image_obj.save(img_file_path)  # 保存图片

def parse_route_list():
    wait = WebDriverWait(driver,10)
    route_list_element = wait.until(
        EC.visibility_of_element_located((By.ID,"route_list"))
    )
    route_li_elements = route_list_element.find_elements(By.TAG_NAME,"li")  # 查找路线的数量
    print(f"{len(route_li_elements)=}")
    # 遍历路线列表中的每条路线
    for route_li_element in route_li_elements:
        # 3.1解析路线基本信息
        scheme_name = parse_route_basic(route_li_element)
        # 3.2 解析路线详细信息
        parse_route_detail(route_li_element)
        # 3.3截图路线地图
        screenshot_line(scheme_name)
        print()

if __name__ == '__main__':
    service = Service("C:/Users/77945/Desktop/Chatbox/chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.get("https://map.baidu.com")

    # 1.展开路线查询输入框
    show_search_box()
    # 2.输入起点和终点，并点击搜索按钮
    start = "环球影城"
    end = "天安门"
    input_start_end(start,end)
    # 3.解析路线列表
    parse_route_list()

""")

st.markdown("""#### 使用scrapy获取住房信息""")


st.markdown("""#### 目前只是了解一些基础用法""")
st.markdown("""#### 对自己的评价：感觉我个人有点自私了，为了自己喜欢的事务，不顾及父母的感受，让他们时不时为了我个人的事而担忧，感觉有点愧疚。""")







