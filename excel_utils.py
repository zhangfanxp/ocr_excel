import pandas as pd
import json
import tempfile
import os
import re

def extract_json(text: str) -> dict:
    """
    从 OCR 模型输出中提取合法 JSON。
    自动处理：
    - ```json ``` 包裹
    - 前后多余文字
    - 返回空字符串或解析失败时抛错
    """
    if not text or not text.strip():
        raise ValueError("OCR 返回内容为空")

    text = text.strip()

    # 去掉 ```json 或 ``` 包裹
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^```$", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试提取第一个 {...} 结构
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise ValueError("无法从 OCR 结果中提取 JSON")

def json_to_excel(json_text: str) -> str:
    """
    将 OCR 输出的 JSON 字符串转换成 Excel 文件。
    自动处理：
    - 如果 JSON 内有 'rows' 字段，取其值作为数据
    - dict/list 都支持
    - 临时目录保存 Excel，并返回路径
    """
    data = extract_json(json_text)

    # 如果有 rows 字段，取其值
    if isinstance(data, dict) and 'rows' in data:
        df = pd.DataFrame(data['rows'])
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        # 兜底，把整个 dict 当作一行
        df = pd.DataFrame([data])

    # 可选：固定列顺序（根据 OCR 输出字段自行修改）
    # columns_order = ["ID","日期","销售","客户名称","客户性质","业务员","规格","单价","批号",
    #                  "生产企业名称","生产日期","有效期","金额"]
    # df = df.reindex(columns=columns_order)

    tmp_dir = tempfile.mkdtemp()
    file_path = os.path.join(tmp_dir, "ocr_result.xlsx")

    df.to_excel(file_path, index=False)
    return file_path

