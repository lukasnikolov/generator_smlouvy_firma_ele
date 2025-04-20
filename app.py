
from flask import Flask, request, send_file, jsonify
from docx import Document
from docx.shared import Pt
import io
import os
from datetime import datetime

app = Flask(__name__)

def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
    except Exception:
        return date_str or ""

@app.route("/api/generate", methods=["POST"])
def generate_document():
    try:
        data = request.get_json()
        print("📥 Přijatá data:", data)

        doc_path = "smlouva.docx"
        if not os.path.exists(doc_path):
            print("❌ Šablona smlouvy nebyla nalezena:", doc_path)
            return jsonify({"error": "Soubor smlouva.docx nebyl nalezen na serveru."}), 500

        template = Document(doc_path)
        for paragraph in template.paragraphs:
            for key, value in data.items():
                placeholder = f"{{{{{key}}}}}"
                if placeholder in paragraph.text:
                    inline = paragraph.runs
                    for i in range(len(inline)):
                        if placeholder in inline[i].text:
                            inline[i].text = inline[i].text.replace(placeholder, value or "")
                            inline[i].font.name = 'Arial'
                            inline[i].font.size = Pt(11)

        buffer = io.BytesIO()
        template.save(buffer)
        buffer.seek(0)

        print("✅ Dokument vygenerován, odesílám ke stažení...")
        return send_file(buffer, as_attachment=True, download_name="smlouva.docx", mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    except Exception as e:
        print("❌ Chyba při generování dokumentu:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Aplikace běží. Odesílejte POST na /api/generate."})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
