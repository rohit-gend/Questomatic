import os
import fitz
from flask import Flask, render_template, request
import re
import random
from indicnlp.tokenize import indic_tokenize
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_pdf(file_path):
    text = ''
    with fitz.open(file_path) as doc:
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
    return text

def read_file(file_path):
    if file_path.lower().endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_path.lower().endswith('.pdf'):
        return read_pdf(file_path)
    else:
        raise ValueError('Unsupported file format')

def generate_questions_english(text, num_questions):
    questions = []
    sections = re.split(r'\n[A-Z][a-zA-Z\s]+\n', text)
    for section in sections:
        section_title = ''
        if not section.strip():
            continue
        title_match = re.match(r'\n([A-Z][a-zA-Z\s]+)\n', section)
        if title_match:
            section_title = title_match.group(1)
        key_points = re.findall(r'\n(\w+(?:\s+\w+)*):\s*([^:]+)', section)
        for point in key_points:
            question_templates = [
                f"What is {point[0]}  {section_title.lower()}?",
                f"Explain the application of {point[0]}.",
                f"What does the term {point[0]} refer to?",
                f"What are the key points related to {point[0]}?",
                f"What are the advantages of {point[0]}?",
                f"What are the disadvantages of {point[0]}?",
                f"Discuss examples of {point[0]}.",
                f"Explain in detail the significance of {point[0]}.",
                f"Define {point[0]}.",
                f"Explain {point[0]} in the context of {section_title.lower()}.",
                f"How does {point[0]} relate to {section_title.lower()}?",
                f"Discuss {point[0]} as mentioned in the {section_title.lower()} .",
                f"Provide an example of {point[0]} {section_title.lower()} .",
                f"Explain {point[0]} in detail with examples.",
                f"Write a short note on {point[0]}.",
                f"Explain {point[0]} in simple terms.",
                f"Explain {point[0]} in simple terms with examples.",
                f"Explain in brief {point[0]}.",
                f"What are the significance of {point[0]}?",
            ]
            
            random.shuffle(question_templates)
            
            selected_question_templates = question_templates[:4]
            
            questions.extend(selected_question_templates)
    
    return questions[:num_questions]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        if 'num_questions' not in request.form:
            return render_template('index.html', error='Number of questions not provided')
        if 'language' not in request.form:
            return render_template('index.html', error='Language not provided')
        num_questions = int(request.form['num_questions'])
        language = request.form['language']
        if file and allowed_file(file.filename):
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                text_from_file = read_file(file_path)
                if language == 'english':
                    generated_questions = generate_questions_english(text_from_file, num_questions)
                else:
                    return render_template('index.html', error='Unsupported language')
                os.remove(file_path)
                return render_template('index.html', questions=generated_questions)
            except Exception as e:
                print("An error occurred:", str(e))  # Debugging
                return render_template('index.html', error='Error processing the file')
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
