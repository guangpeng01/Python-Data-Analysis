import pandas as pd
import numpy as np
import streamlit as st

st.markdown("""#### 姓名：常广鹏""")

st.markdown("""#### 电话：17662513419(微信同号)""")

st.markdown("""#### scrapy_spiders代码示例""")

"""
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

"""

st.markdown("""#### scrapy_spiders代码示例""")

'''
    import scrapy
    from scrapy_lianjia.items import ScrapyLianjiaItem
    import json


    class LianjieNewsSpider(scrapy.Spider):
        name = "lianjie_news"
        allowed_domains = ["bj.lianjia.com"]
        max_page = 2

        def start_requests(self):
            # page = 1
            # if page:
            #     return None
            for page in range(1,self.max_page + 1):
                
                # if page < 2:
                base_url = f'https://bj.lianjia.com/ershoufang/pg{page}rs天通苑/'
                self.logger.info(f"生成第{page}页请求: {base_url}")
                
                yield scrapy.Request(
                    url=base_url,
                    callback=self.parse,
                    meta={
                        "page": page}
                )

        # 标题，标签
        def get_title(self, info_item_element):
            title_list = info_item_element.xpath('./div[@class="title"]//text()').getall()
            if len(title_list) > 1:
                title = title_list[0].strip() if title_list[0] else None
                house_tag = title_list[1].strip() if title_list[1] else None
            else:
                title = title_list[0].strip() if title_list[0] else None
                house_tag = None
            return title, house_tag
        
        # 价钱
        def get_priceInfo(self, info_item_element):
            priceInfo_list = info_item_element.xpath('./div[@class="priceInfo"]//span/text()').getall()
            total_price = priceInfo_list[0] if priceInfo_list else None
            unit_price = priceInfo_list[1] if len(priceInfo_list) > 1 else None
            return total_price, unit_price

        # 地址
        def get_flood(self, info_item_element):
            flood_list = info_item_element.xpath('./div[@class="flood"]//a/text()').getall()
            community_name = flood_list[0].strip() if flood_list else None
            region_name = flood_list[1].strip() if len(flood_list) > 1 else None
            return community_name, region_name

        # 分页
        def get_page(self,page_data_json):
            
            if page_data_json:
                page_data = json.loads(page_data_json)
                total_pages = page_data.get("totalPage", 1)
                current_page = page_data.get("curPage", 1)
                
                self.logger.info(f"分页信息: 第{current_page}页/共{total_pages}页")
                # 更新最大页数
                self.max_page = total_pages
            return current_page

        def parse(self, response):
            """解析列表页"""
            info_item_element_list = response.xpath("//div[@class='info clear']")
            self.logger.info(f"页面 {response.meta['page']} 中有 {len(info_item_element_list)} 个房源")
            
            if not info_item_element_list:
                self.logger.warning(f"页面 {response.url} 没有找到房源信息")
                return
            
            for info_item_element in info_item_element_list:
                title, house_tag = self.get_title(info_item_element)
                total_price, unit_price = self.get_priceInfo(info_item_element)
                community_name, region_name = self.get_flood(info_item_element)
                title_url = info_item_element.xpath('./div[@class="title"]/a/@href').get()
                
                if title_url:
                    yield scrapy.Request(
                        url=title_url,
                        callback=self.parse_house_detail,
                        meta={
                            "title": title,
                            "house_tag": house_tag,
                            "total_price": total_price,
                            "unit_price": unit_price,
                            "community_name": community_name,
                            "region_name": region_name
                        }
                    )
                # page_data_json = response.xpath('//div[@class="page-box house-lst-page-box"]/@page-data').get()
            page_data_json = response.xpath('//div[@class="page-box house-lst-page-box"]/@page-data').get()
            current_page = self.get_page(page_data_json)
            if current_page < self.max_page:
                next_page = current_page + 1
                next_url = f'https://bj.lianjia.com/ershoufang/pg{next_page}rs天通苑/'
                if next_page < 2:
                    self.logger.info(f"生成下一页请求: 第{next_page}页")
                    yield scrapy.Request(
                        url=next_url,
                        callback=self.parse,
                        meta={"next_page": next_page})

        # 房屋基本属性
        def get_content_list(self, content_list):
            info_content_dict1 = {}
            info_name_list = ["房屋户型", "所在楼层", "建筑面积", "建筑类型", "装修情况", "房屋朝向"]
            for content in content_list:
                all_texts = content.xpath('.//text()').getall()
                if len(all_texts) > 1:
                    all_text1 = all_texts[1].strip()
                    all_text2 = all_texts[2].strip()
                    if all_text1 in info_name_list:
                        info_content_dict1[all_text1] = all_text2
            return info_content_dict1
        
        # 房源标签
        def get_tags_clear_list(self, tags_clear_list):
            info_content_dict2 = {"地铁": None, "房本": None, "看房": None}
            tags_clear_texts = tags_clear_list.xpath('.//text()').getall()
            for tags_clear in tags_clear_texts:
                for info_name in info_content_dict2.keys():
                    if info_name in tags_clear:
                        info_content_dict2[info_name] = tags_clear
            return info_content_dict2

        def parse_house_detail(self, response):
            """解析房屋详情页"""
            content_list = response.xpath('//*[@id="introduction"]/div/div/div[1]/div[2]/ul//li')
            info_content_dict1 = self.get_content_list(content_list)

            tags_clear_list = response.xpath('/html/body/div[7]/div[1]/div[2]/div/div[1]/div[2]//a')
            info_content_dict2 = self.get_tags_clear_list(tags_clear_list)
            
            item_data = ScrapyLianjiaItem(
                title=response.meta['title'],
                house_tag=response.meta['house_tag'],
                total_price=response.meta['total_price'],
                unit_price=response.meta['unit_price'],
                community_name=response.meta['community_name'],
                region_name=response.meta['region_name'],
                layout=info_content_dict1.get("房屋户型"),
                floor=info_content_dict1.get("所在楼层"),
                area=info_content_dict1.get("建筑面积"),
                building_type=info_content_dict1.get("建筑类型"),
                decorate_status=info_content_dict1.get("装修情况"),
                orientation=info_content_dict1.get("房屋朝向"),
                is_near_subway=info_content_dict2.get("地铁"),
                tax_free_type=info_content_dict2.get("房本"),
                is_has_key=info_content_dict2.get("看房"),
            )
            
            self.logger.info(f"成功提取房屋: {response.meta['title']}")
            yield item_data'''


