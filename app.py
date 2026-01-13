import gradio as gr
import json
from ocr import ocr_image
from excel_utils import json_to_excel

def process_image(image):
    json_text = ocr_image(image)
    return json_text

def generate_excel(json_text):
    file_path = json_to_excel(json_text)
    return file_path

with gr.Blocks(title="OCR 图片识别 → Excel") as demo:
    gr.Markdown("## 📷 图片文字识别并导出 Excel")

    with gr.Row():
        image_input = gr.Image(type="filepath", label="上传图片")
        json_output = gr.Textbox(label="识别结果（JSON）", lines=15)

    recognize_btn = gr.Button("🔍 开始识别")
    recognize_btn.click(
        fn=process_image,
        inputs=image_input,
        outputs=json_output
    )

    excel_btn = gr.Button("📊 生成 Excel")
    file_output = gr.File(label="下载 Excel")

    excel_btn.click(
        fn=generate_excel,
        inputs=json_output,
        outputs=file_output
    )

demo.launch(server_name="127.0.0.1", server_port=7860)

