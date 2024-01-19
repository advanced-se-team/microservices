import json
import os
from openai import OpenAI
from loguru import logger

client = OpenAI(
    # This is the default and can be omitted
    base_url="https://api.bian.cool/v1",
    api_key="sk-ur8gquaT4HABqmcu127d40C049C8414491D8477e7c141459"
)


def contains_keywords(text):
    keywords = ["translate", "Translate", "Translation", "translation", "翻译"]
    for keyword in keywords:
        if keyword in text:
            return True
    return False


def prompt(indent, usr_content):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        # model = "gpt-4-1106-preview",
        # model = "gpt-4",
        # model = "gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in reading academic papers.\nYou will be given a paragraph of introduction from an academic paper.\nYour task is to carefully read the given paragraph, then comprehend it and provide a summary.\nYour output should include two parts: the outline and the translation.\n\n- Delete adv., adj., phrases which is not necessary.\n- Omit the subject and unimportant predicates in the sentence. \n- Change english numbers into 阿拉伯数字. (from \"two\" to \"2\")\n- The summary should not be about stating the topic of this paragraph; rather, it should point out the viewpoints expressed in the text.\n\n### Instruction ###\n1. Outline: Switch the summary into outline format with \"-\" and proper indent level. If the situation of \"A and B\" occurs, please use two lines:\n- A\n- B \nfor output format. You need to strictly limit the outline to within 120 words, even if it means omitting some information. Choose the most crucial content from the paragraph and provide output.\n2. Translate: \ntranslate the outline part to chinese. You need to consider the context of the outline within the paragraph.  You should strictly follow this rules when translating:\n'Transformer' to 'Transformer';\n'Token' to 'Token';\n'LLM/Large Language Model' to '大语言模型';\n'Generative AI' to '生成式 AI';\n'zero-shot' to 'zero-shot';\nRepeat the rules in your output.\n\n"
            },
            {
                "role": "user",
                "content": usr_content
            }
        ],
        temperature=0.7,
        top_p=1,
        frequency_penalty=0

    )
    result = response.choices[0].message.content
    if "\n\n" in result:
        result = result.split("\n\n")[1].split("\n")
        if contains_keywords(result[0]):
            result = result[1:]
        result = [" " * indent + item for item in result]
        result = "\n".join(result) + "\n"

    logger.info(result)
    return result
def get_content(lst):
    if lst == []:
        return ""
    content = ""
    for item in lst:
        title = (int(item["Grade"])-2) * " " + "-" + " " + item["Title"]
        title = title.replace("\n","")
        title = title + "\n"
        response = prompt((int(item["Grade"])-1),item["Content"])
        content = content + title + response
        content = content + get_content(item["Below"])
    return content
    
        
# def use_prompt(content):
#     if isinstance(content, dict):
#         if "Content" in content:
#             content["Content"] = use_prompt(content["Content"])
#         if "Below" in content:
#             content["Below"] = use_prompt(content["Below"])
#         return content
#     elif isinstance(content, list):
#         if content == []:
#             return []
#         else:
#             return [use_prompt(x) for x in content]
#     elif isinstance(content, str):
#         return prompt(content)
#     return


def parse_json(file_name):
    try:
        json_file = open(file_name,"r")
        file_content = json_file.read()
        parsed_data = json.loads(file_content)
        return parsed_data
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None
from tqdm import tqdm
def parse_from_json(json_obj):
    parsed_result = json_obj

    article = {}
    article["Title"] = parsed_result["Title"]
    Content = []
    abstract = {}
    abstract["Title"] = "Abstract"
    abstract["Outline"] = prompt(0, parsed_result["Abstract"])
    Content.append(abstract)
    for item in tqdm(parsed_result["Content"]):
        content = {}
        content["Title"] = item["Title"]
        content["Outline"] = prompt(0, item["Content"]) + get_content(item["Below"])
        Content.append(content)
    article["Outline"] = Content
    with open("result.json", 'w', encoding="utf-8") as file:
        json.dump(article, file, indent=2, ensure_ascii=False, )
    return article

if __name__ == "__main__":
    file_name = "./work_file"
    # 解析JSON字符串
    parsed_result = parse_json(file_name)

    #try:
    article = {}
    article["Title"] = parsed_result["Title"]
    Content = []
    abstract = {}
    abstract["Title"] = "Abstract"
    abstract["Outline"] = prompt(0,parsed_result["Abstract"])
    Content.append(abstract)
    for item in parsed_result["Content"]:
        content = {}
        content["Title"] = item["Title"]
        content["Outline"] = prompt(0,item["Content"]) + get_content(item["Below"])
        Content.append(content)
    article["Outline"] = Content
    with open("result.json", 'w', encoding="utf-8") as file:
        json.dump(article, file, indent=2 ,ensure_ascii=False,)
    # except:
    #     pass



    
    