import os
from openai import OpenAI

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


def prompt(usr_content):
    response = client.chat.completions.create(
        # model = "gpt-3.5-turbo-16k",
        model="gpt-4-1106-preview",
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
        result = "\n".join(result) + "\n"
    return result