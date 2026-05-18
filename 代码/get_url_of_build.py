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

#增加暂存数据



def run_get_classinstreet(playwright: Playwright) -> None:
    """
    
    """
    # 1. 初始化浏览器环境
    browser = playwright.chromium.launch(headless=False)  # 显示浏览器窗口（调试用）
    context = browser.new_context(
        user_agent=random.choice(config.USER_AGENTS)  # 随机选择User-Agent
    )
    page = context.new_page()  # 创建新页面
    with open(config.INPUT_URL_FILE, 'r', encoding='utf-8') as f:
            data_url = json.load(f)
        
    all_results = []
    # 处理URL字段名
    for qu_class, street_url in data_url.items():
        qu_results = []
        for street_name, url in street_url.items():
            sub_page = context.new_page()
            sub_page.goto(url)
            sub_page.wait_for_timeout(config.PAGE_LOAD_WAIT)
            try:
                # 等待地图控件加载
                sub_page.wait_for_selector('.BMap_stdMpCtrl', timeout=10000)
                
                # 找到缩小按钮
                zoom_out_btn = sub_page.query_selector('.BMap_stdMpZoomOut')
                if zoom_out_btn:
                    log.run_logger.info(f"【{street_name}】开始点击缩小按钮5次")
                    
                    # 点击5次缩小按钮
                    for i in range(5):
                        try:
                            # 使用JavaScript点击，更可靠
                            sub_page.evaluate('''() => {
                                const zoomOutBtn = document.querySelector('.BMap_stdMpZoomOut');
                                if (zoomOutBtn) {
                                    zoomOutBtn.click();
                                    return true;
                                }
                                return false;
                            }''')
                            
                            log.run_logger.info(f"【{street_name}】第 {i+1} 次点击缩小按钮")
                            sub_page.wait_for_timeout(1000)  # 每次点击后等待1秒
                            
                        except Exception as click_error:
                            log.url_warning_logger.warning(f"【{street_name}】第 {i+1} 次点击缩小按钮失败: {str(click_error)}")
                            continue
                    
                    log.run_logger.info(f"【{street_name}】完成5次缩小操作")
                    sub_page.wait_for_timeout(2000)  # 等待地图缩放完成
                else:
                    log.url_warning_logger.warning(f"【{street_name}】未找到缩小按钮")
                    
            except Exception as e:
                log.url_warning_logger.warning(f"【{street_name}】地图缩放操作失败: {str(e)}")
            current_page = 1
            detail_links = []
            
            while True:
                time.sleep(3)  # 确保页面加载完成


                # 获取所有列表项
                list_items = sub_page.query_selector_all('div.listc')  # 注意：这里应该是sub_page而不是page
                print(f"找到 {len(list_items)} 个电梯项目")
                
                for item in list_items:
                    # 在每个listc元素中查找详情链接
                    detail_link = item.query_selector('a.lcm:not([style*="display: none"])')  # 只选择可见的链接
                    if detail_link:
                        detail_url = detail_link.get_attribute('href')
                        
                        # 获取项目标题
                        title_element = item.query_selector('h4')
                        title = title_element.text_content().replace('详情>>', '').strip() if title_element else "无标题"
                        
                        # 获取地址
                        address_element = item.query_selector('p')
                        address = address_element.text_content().replace('地址：', '').strip() if address_element else "无地址"
                        
                        # 构建完整URL
                        full_url = "https://map.beijing.gov.cn/" + detail_url
                        
                        detail_info = {
                            'title': title,
                            'address': address,
                            'detail_url': full_url,
                            'qu_class': qu_class,
                            'street_name': street_name,
                            'qu_name':qu_class
                        }
                        
                        detail_links.append(detail_info)
                        print(f"提取详情: {title} -> {full_url}")
                time.sleep(2)  # 等待，模拟人类操作
                log.run_logger.info(f"{qu_class}的{street_name}的第 {current_page} 页爬取完成，共 {len(detail_links)} 条数据")
                
                # 翻页逻辑 - 修改部分
                try:
                    # 检查是否还有下一页
                    next_btn = sub_page.query_selector('a.page-link.next:not(.disabled)')
                    
                    # 如果没有找到可用的下一页按钮，检查是否有禁用的下一页按钮
                    if not next_btn:
                        disabled_next = sub_page.query_selector('span.current.next')
                        if disabled_next:
                            log.run_logger.info(f"【{street_name}】已到达最后一页，终止爬取\n")
                            break
                        else:
                            log.run_logger.info(f"【{street_name}】未找到下一页按钮，终止爬取\n")
                            break
                    
                    # 点击下一页
                    log.run_logger.info(f"【{street_name}】点击下一页，当前页码：{current_page}")
                    
                    # 使用JavaScript点击，因为这是锚点链接
                    sub_page.evaluate('''() => {
                        const nextBtn = document.querySelector('a.page-link.next:not(.disabled)');
                        if (nextBtn) nextBtn.click();
                    }''')
                    
                    # 等待页面更新
                    sub_page.wait_for_timeout(3000)
                    
                    # 等待列表内容更新
                    sub_page.wait_for_selector('div.listc', timeout=10000)
                    
                    current_page += 1
                    sub_page.wait_for_timeout(config.NEXT_PAGE_WAIT + random.randint(0, config.NEXT_PAGE_RANDOM))
                    
                except Exception as e:
                    log.url_warning_logger.error(f"【{street_name}】翻页失败：{str(e)}，终止爬取\n", exc_info=True)
                    break
            
            # 保存这个街道的所有数据
            if detail_links:
                all_results.extend(detail_links)
                qu_results.extend(detail_links)
                # 这里可以添加保存数据的逻辑
                log.run_logger.info(f"【{street_name}】爬取完成，总共 {len(detail_links)} 条数据")
            sub_page.close()  # 关闭当前分类页面
        save_results(qu_results, f"北京电梯数据库/url地址/{qu_class}_电梯数据_社区.json")
    # 关闭浏览器
    context.close()
    browser.close()  # 关闭浏览器   
    save_results(all_results, config.OUTPUT_FILE_community)

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run_get_classinstreet(playwright)