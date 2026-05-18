# 导入必要的库
import random  # 生成随机数，模拟人类操作的随机性
import re
import json
import os
from datetime import datetime
from playwright.sync_api import (
    Playwright,        # Playwright核心类
    sync_playwright,   # 同步模式上下文管理器
    TimeoutError       # 超时异常类
)  # Playwright浏览器自动化库
import config  # 导入配置文件
from SAVE_AND_CHECK import save_results
import log
import time



def run_get_classinstreet(playwright: Playwright) -> None:
    """
    
    """
    # 1. 初始化浏览器环境
    browser = playwright.chromium.launch(headless=False)  # 显示浏览器窗口（调试用）
    context = browser.new_context(
        user_agent=random.choice(config.USER_AGENTS)  # 随机选择User-Agent
    )
    page = context.new_page()  # 创建新页面

    qu_streeet_class={}
    qu_class={}

    try:
        # 访问目标页面
        page.goto(config.TARGET_URL)
        # 随机等待，模拟人类浏览行为
        page.goto(config.TARGET_URL, wait_until='networkidle', timeout=30000)

        iframe_element = page.query_selector('iframe.ljxqjztdmap')
        if not iframe_element:
            log.run_logger.error("未找到iframe元素")

        iframe = iframe_element.content_frame()
        if not iframe:
            log.run_logger.error("无法获取iframe内容")

        iframe = iframe_element.content_frame()
        if not iframe:
            log.run_logger.error("无法获取iframe内容")
        print("已切换到iframe内部")

        iframe.wait_for_selector('div.xj#regionDiv a', timeout=15000)
        items = iframe.query_selector_all('div.xj#regionDiv a')
        print("==========")
        print(items)
        for item in items:
            qu_class_name = item.text_content().strip()
            qu_class_url = item.get_attribute("href")
            if qu_class_name and qu_class_url:
                # 处理相对路径为绝对路径
                full_url = "https://map.beijing.gov.cn" + qu_class_url if qu_class_url.startswith('/') else qu_class_url
                qu_class[qu_class_name]=full_url
        if qu_class:  # 过滤空内容
            for name, url in qu_class.items():
                log.run_logger.info(f"区：{name}，URL：{url}")
            del qu_class["各区加装电梯咨询电话"]

    except Exception as e:  
        log.url_warning_logger.error(f"主页面访问失败：{str(e)}")
        log.url_warning_logger.error(f"\n程序执行异常：{e}", exc_info=True)
    
    try:
        for class_name,url in qu_class.items():
            street_class={}
            log.run_logger.info(f"\n===== 开始爬取街道：{class_name} =====")
            sub_page = context.new_page()
            sub_page.goto(url)

            sub_page.wait_for_timeout(config.PAGE_LOAD_WAIT)
            items = sub_page.query_selector_all('#regionDiv > a')
            for item in items:
                street_class_name = item.text_content().strip()
                street_class_url = item.get_attribute("href")
                if street_class_name and street_class_url:
                    # 处理相对路径为绝对路径
                    full_url = "https://map.beijing.gov.cn" + street_class_url if street_class_url.startswith('/') else street_class_url
                    street_class[street_class_name]=full_url
            if street_class:  # 过滤空内容
            # 可选：打印每个区的信息
                for name, url in street_class.items():
                    log.run_logger.info(f"街道：{name}，URL：{url}")
            qu_streeet_class[class_name]=street_class
            sub_page.close()
    except Exception as e:  
        log.url_warning_logger.error(f"街道页面访问失败：{str(e)}")
        log.url_warning_logger.error(f"\n程序执行异常：{e}", exc_info=True)
    finally:
        browser.close()  # 确保浏览器关闭
        log.run_logger.info("\n浏览器已关闭")   
    return qu_streeet_class


# 程序入口
if __name__ == "__main__":
    with sync_playwright() as playwright:
        qu_streeet_class=run_get_classinstreet(playwright)
        save_results(qu_streeet_class, config.CLAASIFY_FILENAME)
