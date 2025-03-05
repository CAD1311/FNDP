import re
import json
from baidusearch.baidusearch import search






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



def try_parse_tool_calls(content: str):
    """Try parse the tool calls."""
    tool_calls = []
    offset = 0
    for i, m in enumerate(re.finditer(r"<tool_call>\n(.+)?\n</tool_call>", content)):
        if i == 0:
            offset = m.start()
        try:
            func = json.loads(m.group(1))
            tool_calls.append({"type": "function", "function": func})
            if isinstance(func["arguments"], str):
                func["arguments"] = json.loads(func["arguments"])
        except json.JSONDecodeError as e:
            print(f"Failed to parse tool calls: the content is {m.group(1)} and {e}")
            pass
    if tool_calls:
        if offset > 0 and content[:offset].strip():
            c = content[:offset]
        else: 
            c = ""
        return {"role": "assistant", "content": c, "tool_calls": tool_calls}
    return {"role": "assistant", "content": re.sub(r"<\|im_end\|>$", "", content)}


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
    "search": search

}
