# 导入必要的库
import random  # 生成随机数，模拟人类操作的随机性
import time
import re
import json
import os
from datetime import datetime
from urllib.parse import urljoin  # 处理 URL 拼接
from playwright.sync_api import (
    Playwright,        # Playwright核心类
    sync_playwright,   # 同步模式上下文管理器
    TimeoutError       # 超时异常类
)  # Playwright浏览器自动化库
import config  # 导入配置文件
from SAVE_AND_CHECK import save_results,has_bordered_table_in_content
import log


def extract_table_data(page,item):
    """提取表格内容并返回字典"""
    table_data = {
        "title": item["title"],
        "address": item["address"],
        "qu_class": item["qu_class"],
        "street_name": item["street_name"],
    }
    
    try:
        # 找到表格
        table = page.query_selector('table.nxq_ctab')
        if not table:
            return table_data
        
        # 获取所有行
        rows = table.query_selector_all('tr')
        
        for row in rows:
            # 获取表头和表数据单元格
            th = row.query_selector('th')
            td = row.query_selector('td')
            
            if th and td:
                # 提取键（表头文本）
                key = th.text_content().strip().rstrip('：').rstrip(':')
                
                # 提取值（表数据文本）
                # 如果有span元素，优先使用span的文本
                span = td.query_selector('span')
                if span:
                    value = span.text_content().strip()
                else:
                    value = td.text_content().strip()
                
                # 添加到字典
                table_data[key] = value
        
        return table_data
        
    except Exception as e:
        print(f"提取表格数据时出错: {e}")
        log.content_warning_logger.error(f"提取表格数据时出错: {e}", exc_info=True)
        return table_data


def run_get_content(playwright: Playwright) -> None:
    """
    核心执行函数：根据URL列表爬取详细内容
    参数：playwright - Playwright实例，用于创建浏览器
    """
    # 1. 初始化浏览器环境
    browser = playwright.chromium.launch(headless=False)  # 显示浏览器窗口（调试用）
    context = browser.new_context(
        user_agent=random.choice(config.USER_AGENTS)  # 随机选择User-Agent
    )
    page = context.new_page()  # 创建新页面

    # 存储所有页面的爬取结果
    all_results = []
    # 临时结果列表，用于达到阈值时保存一次
    temp_results = []
    save_count = 0  # 记录保存次数
    counter = 1  # 计数器，记录处理的条目数
    warnings_item=[]

    try:
        # 读取URL列表
        with open(config.INPUT_CONTENT_FILE, 'r', encoding='utf-8') as f:
            data_url = json.load(f)
        

        # 遍历每个URL，爬取详细内容
        for item in data_url:
            print(item)
            url=item['detail_url']
                   # 重试机制：确保页面成功加载
            while True:
                try:
                    page.goto(url)
                    page.wait_for_timeout(3)
                    break  # 成功则退出重试循环
                except Exception as e:
                    log.content_warning_logger.error(f"URL {url} 网络请求失败，重试中... 错误：{e}", exc_info=True)
                    time.sleep(random.uniform(*config.RETRY_WAIT_RANGE))  # 随机延迟后重

            data_table=extract_table_data(page,item)
            all_results.append(data_table)
            if not data_table:
                warnings_item.append({'区':item["qu_class"],'街道':item['street_name'],'address':item['address'],'url':url})
                log.content_warning_logger.warning(f"【{item['address']}】未提取到表格数据，已记录警告项。")
        
            log.run_logger.info(f'=======已经爬取了{counter}条数据=======')
            temp_results.append(data_table)
            counter += 1

            # 达到临时保存阈值则保存
            if len(temp_results) >= config.TEMP_SAVE_THRESHOLD_CONTENT:
                save_count += 1
                temp_filename = config.CONTENT_TEMP_FILENAME_TEMPLATE.format(save_count)
                save_results(all_results, temp_filename)
                temp_results = []  # 清空临时列表

        # 输出总结果
        log.run_logger.info(f"\n===== 爬取完成 =====")
        log.run_logger.info(f"共爬取累计 {len(all_results)} 条数据")
        log.run_logger.info("部分结果示例：", all_results[:3] if all_results else "无数据")  # 打印前3条示例
        
        # 保存最终结果
        save_results(all_results, config.CONTENT_FINAL_FILENAME)
        save_results(warnings_item,config.WARNINGS_ITEM_FILR)
        log.run_logger.info(f"最终结果已保存到 {config.CONTENT_FINAL_FILENAME}")

    except Exception as e:
        log.content_warning_logger.error(f"\n程序执行异常：{e}",exc_info=True)
        # 异常发生时保存已爬取的数据
        if all_results:
            error_filename = config.CONTENT_ERROR_FILENAME_TEMPLATE.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
            save_results(all_results, error_filename)
            log.run_logger.info(f"已将当前已爬取的 {len(all_results)} 条数据保存到 {error_filename}")

    finally:
        browser.close()  # 确保浏览器关闭
        log.run_logger.info("\n浏览器已关闭")


# 程序入口
if __name__ == "__main__":
    with sync_playwright() as playwright:
        run_get_content(playwright)
