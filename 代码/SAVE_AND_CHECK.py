import json
import os
import logging
from datetime import datetime
import log


def save_results(results, filename):
    """保存爬取结果到JSON文件"""
    try:
        # 确保保存目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        log.save_logger.info(f"已保存 {len(results)} 条数据到 {filename}")
    except Exception as e:
        log.save_logger.warning(f"保存文件失败: {e}",extra=True)







