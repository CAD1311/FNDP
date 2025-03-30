import json
import re

def parse_prediction_json(predict_json_str):
    """
    解析预测 JSON 字符串，转换为 Python 对象

    Args:
        predict_json_str (str): 包含预测结果的 JSON 字符串

    Returns:
        dict: 包含解析后的预测结果，如果解析失败则返回默认值
    """
    try:
        # 尝试直接解析 JSON
        prediction = json.loads(predict_json_str)

        # 提取关键字段
        result = {
            'IsNewsTrue': prediction.get('IsNewsTrue'),
            'reasons': prediction.get('reasons', []),
            'recommendation': prediction.get('recommendation', '')
        }

        return result

    except json.JSONDecodeError:
        # JSON 解析失败，尝试使用正则表达式提取 IsNewsTrue
        is_news_true_match = re.search(r'"IsNewsTrue"\s*:\s*([01])', predict_json_str)
        if is_news_true_match:
            return {
                'IsNewsTrue': int(is_news_true_match.group(1)),
                'reasons': [],
                'recommendation': '无法解析完整JSON，仅提取了预测结果'
            }
        else:
            # 完全无法解析
            return {
                'IsNewsTrue': None,
                'reasons': [],
                'recommendation': '无法解析JSON'
            }