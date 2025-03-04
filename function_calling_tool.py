from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import re
import json
from baidusearch.baidusearch import search
import time



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


model_name_or_path = "qwen"

tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    model_name_or_path,
    torch_dtype="auto",
    device_map="auto",

)

tools = [
  {
        "type": "function",
        "function": {
            "name": "IsRumours",
            "description": "当需要输出最终谣言判定结论时调用此函数，参数只能从0/1/2中选择。调用后用户将直接看到判定结果。",
            "parameters": {
                "type": "object",
                "properties": {
                    "isNewsTrue": {
                        "type": "integer",
                        "enum": [0, 1, 2],
                        "description": "谣言判定结果：0=事实，1=尚未定论，2=谣言"
                    }
                },
                "required": ["isNewsTrue"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "可以利用这个搜索函数进行搜索，搜索结果将帮助确定新闻的真实与否",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "用于搜索的关键字"
                    },
                    "numOfResult":{
                        "type": "integer",
                        "description": "搜索结果的数量，最好为3个"
                    }
                },
                "required": ["keyword","numOfResult"]
            }
        }
    }
]




start = time.perf_counter()


messages = [
   {"role": "system", "content": "你是千问，帮助用户分析新闻是否是谣言，只能说是或者不是谣言，并且要调用适当的函数，还有给用户提供合理的分析，得到结果后调用IsRumours告诉用户是否是谣言"},
   {"role": "user", "content": "这是一个在2020/1/1网易发布的新闻。标题是教皇方济各纪念新教改革500周年，正文是2020年11月15日 · 教皇方济各陷入“丑闻”，他为性感模特点了个赞，掀起网络狂潮."}
]

text = tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
inputs = tokenizer(text, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512)
output_text = tokenizer.batch_decode(outputs)[0][len(text):]
print(output_text)

messages.append(try_parse_tool_calls(output_text))



function_calling(messages)

text = tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
inputs = tokenizer(text, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512)
output_text = tokenizer.batch_decode(outputs)[0][len(text):]


messages.append(
    {"role": "user", "content": "好的 得到判别结果后请调用IsRumours函数告诉我结果"}
)

text = tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
inputs = tokenizer(text, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512)
output_text = tokenizer.batch_decode(outputs)[0][len(text):]

messages.append(try_parse_tool_calls(output_text))



function_calling(messages)
end = time.perf_counter()

print(f"耗时: {end - start:.3f}秒")
