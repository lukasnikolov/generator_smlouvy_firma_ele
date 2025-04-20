
from flask import Flask, request, send_file, jsonify
from docx import Document
from docx.shared import Pt
import io
from datetime import datetime

app = Flask(__name__)

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
    except Exception:
        return date_str or ""

@app.route("/api/generate", methods=["POST"])
def generate_document():
    data = request.get_json()

    template = Document("smlouva.docx")
    for paragraph in template.paragraphs:
        for key, value in data.items():
            if f"{{{{{key}}}}}" in paragraph.text:
                inline = paragraph.runs
                for i in range(len(inline)):
                    if f"{{{{{key}}}}}" in inline[i].text:
                        text = value or ""
                        inline[i].text = inline[i].text.replace(f"{{{{{key}}}}}", text)
                        inline[i].font.name = 'Arial'
                        inline[i].font.size = Pt(11)

    buffer = io.BytesIO()
    template.save(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="smlouva.docx", mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API běží. Použijte POST na /api/generate."})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
