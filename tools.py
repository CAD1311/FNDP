import re
import json
from baidusearch.baidusearch import search



def My_search(
    keyword: str ,
             ):
    return search(keyword=keyword)


def generation_text(
    is_having_image: bool = False,
    title: str = "未知标题",
    content: str = "未知正文",
    category: str = "未知类别",
    date: str = "未知日期",
    platform: str = "未知平台"
) -> str:
    if is_having_image:
        text=f"这是一个在{date}{platform}发布的新闻。标题是{title}，正文是{content}，是属于{category}。<image>请你告诉我是否是谣言。"
    else:
        text = f"这是一个在{date}{platform}发布的新闻。标题是{title}，正文是{content}，是属于{category}。请你告诉我是否是谣言。"
    return text




def IsRumours(
    isNewsTrue: int
    )-> None:
    if isNewsTrue==0:
        print("事实")
    elif isNewsTrue==1:
        print("尚未定论")
    elif isNewsTrue==2:
        print("谣言")


def reasons(
    reasons:list,
    isNewsTrue:int
)->None:
    if isNewsTrue==0:
        print("事实")
    elif isNewsTrue==1:
        print("尚未定论")
    elif isNewsTrue==2:
        print("谣言")
    for a in reasons:
        print(a)



def try_parse_tool_calls(text):
    """尝试解析工具调用，返回解析后的消息"""
    print(f"尝试解析文本: {text}")
    
    # 先尝试直接从<tool_call>标签解析
    pattern = r'<tool_call>\s*(.*?)\s*</tool_call>'
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        try:
            tool_content = match.group(1).strip()
            print(f"找到tool_call内容: {tool_content}")
            tool_json = json.loads(tool_content)
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": f"call_{tool_json['name']}",
                        "type": "function",
                        "function": {
                            "name": tool_json["name"],
                            "arguments": json.dumps(tool_json["arguments"])
                        }
                    }
                ]
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"解析<tool_call>标签内容失败: {e}")
    else:
        print("未找到<tool_call>标签")
    
    # 如果上面失败，尝试从markdown代码块解析
    json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', text, re.DOTALL)
    if json_match:
        try:
            json_content = json_match.group(1).strip()
            print(f"找到markdown代码块JSON内容: {json_content}")
            json_obj = json.loads(json_content)
            
            # 判断是IsRumours还是search
            if "isNewsTrue" in json_obj:
                tool_name = "IsRumours"
                tool_args = {"isNewsTrue": json_obj["isNewsTrue"]}
            elif "keyword" in json_obj and "num" in json_obj:
                tool_name = "search"
                tool_args = {"keyword": json_obj["keyword"], "num": json_obj["num"]}
            else:
                print(f"无法确定工具类型，JSON内容: {json_content}")
                return {"role": "assistant", "content": text}
                
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": f"call_{tool_name}",
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(tool_args)
                        }
                    }
                ]
            }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"解析markdown代码块内容失败: {e}")
    else:
        print("未找到markdown代码块")
    
    # 最后，尝试将整个文本直接解析为JSON
    try:
        print("尝试直接将文本解析为JSON")
        json_obj = json.loads(text)
        print(f"成功解析为JSON: {json_obj}")
        
        # 检查JSON是否包含工具调用所需的字段
        if "name" in json_obj and "arguments" in json_obj:
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": f"call_{json_obj['name']}",
                        "type": "function",
                        "function": {
                            "name": json_obj["name"],
                            "arguments": json.dumps(json_obj["arguments"])
                        }
                    }
                ]
            }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"直接解析JSON失败: {e}")
    
    # 如果所有尝试都失败，返回普通消息
    print("所有解析尝试失败，返回原始文本作为内容")
    return {"role": "assistant", "content": text}


def function_calling(messages):
    if tool_calls := messages[-1].get("tool_calls", None):
        for tool_call in tool_calls:
            if fn_call := tool_call.get("function"):
                fn_name: str = fn_call["name"]
            # 添加函数存在性检查
                if fn_name not in function_map:
                    raise ValueError(f"Function {fn_name} not registered")
            
            # 解析参数（支持字符串和字典两种格式）
                try:
                    fn_args = json.loads(fn_call["arguments"]) if isinstance(fn_call["arguments"], str) else fn_call["arguments"]
                # 调用实际函数
                    fn_res = function_map[fn_name](**fn_args)
                except Exception as e:
                    print(f"调用函数{fn_name}失败: {str(e)}")
                    continue

                messages.append({
                    "role": "tool",
                    "name": fn_name,
                    "content": json.dumps(fn_res),
                })



function_map = {
    "IsRumours": IsRumours,
    "search": My_search,
    "reasons":reasons

}
