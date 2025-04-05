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
    # 尝试提取 JSON 部分
    json_pattern = r'```json\s*(.*?)\s*```'
    json_match = re.search(json_pattern, predict_json_str, re.DOTALL)

    if json_match:
        json_content = json_match.group(1)
    else:
        json_pattern = r'({[\s\S]*})'
        json_match = re.search(json_pattern, predict_json_str)
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = predict_json_str  # 使用整个字符串

    try:
        prediction = json.loads(json_content)

        result = {
            'IsNewsTrue': prediction.get('IsNewsTrue', None),
            'reasons': prediction.get('reasons', ['暂无原因分析']),
            'recommendation': prediction.get('recommendation', '暂无建议')
        }
        return result
    except json.JSONDecodeError:
        result = {}

        is_news_true_match = re.search(r'"IsNewsTrue"\s*:\s*([01])', predict_json_str)
        if is_news_true_match:
            result['IsNewsTrue'] = int(is_news_true_match.group(1))
        else:
            result['IsNewsTrue'] = None

        reasons_pattern = r'"reasons"\s*:\s*\[(.*?)\]'
        reasons_match = re.search(reasons_pattern, predict_json_str, re.DOTALL)
        if reasons_match:
            reasons_str = reasons_match.group(1)
            reasons = re.findall(r'"(.*?)"', reasons_str)
            result['reasons'] = reasons
        else:
            result['reasons'] = ['暂无原因分析']

        recommendation_pattern = r'"recommendation"\s*:\s*"(.*?)"'
        recommendation_match = re.search(recommendation_pattern, predict_json_str, re.DOTALL)
        if recommendation_match:
            result['recommendation'] = recommendation_match.group(1).strip()
        else:
            result['recommendation'] = '暂无建议'

        return result