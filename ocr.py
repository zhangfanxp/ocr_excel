import os
import base64
from openai import OpenAI

# 优化后的提示词：明确要求表格结构
PROMPT = """
你是一个专业的 OCR 表格识别专家。请识别图片中的表格内容，并严格按照以下 JSON 格式返回：

{
  "rows": [
    {"列名1": "内容", "列名2": "内容", ...},
    {"列名1": "内容", "列名2": "内容", ...}
  ]
}

要求：
1. 识别图片中所有的表格行，每一行作为一个 dict 放入 rows 列表中。
2. 保持原有的列标题。如果图片中没有明确标题，请根据内容推断合适的列名。
3. 确保数值、日期和金额的准确性。模糊无法识别的文字用 "?"。
4. 严格只返回 JSON 内容，不要包含任何解释、Markdown 代码块标识或多余文字。
5. 保证 JSON 格式合法且可解析。
"""

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def image_to_data_url(image_path: str) -> str:
    """
    将本地图片转成 base64 格式
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    # 自动识别图片后缀（简单处理）
    ext = os.path.splitext(image_path)[1].replace(".", "") or "png"
    base64_str = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/{ext};base64,{base64_str}"

def ocr_image(image_path: str) -> str:
    image_data_url = image_to_data_url(image_path)

    # 使用流式输出或固定响应格式（如果模型支持）
    completion = client.chat.completions.create(
        model="qwen-vl-ocr-latest",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_data_url}
                    }
                ]
            }
        ],
        # 增加采样温度控制，降低随机性，使输出更稳定
        temperature=0.01, 
        top_p=0.1
    )

    return completion.choices[0].message.content
