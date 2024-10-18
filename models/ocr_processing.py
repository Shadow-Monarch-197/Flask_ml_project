import cv2
import pytesseract
from pytesseract import Output
import re

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    return binary

def extract_text_and_bounding_boxes(image_path):
    img = preprocess_image(image_path)
    d = pytesseract.image_to_data(img, output_type=Output.DICT)
    n_boxes = len(d['level'])
    text_blocks = []
    
    for i in range(n_boxes):
        text = preprocess_text(d['text'][i])
        if text.strip():
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            text_blocks.append({'text': text, 'box': (x, y, w, h)})
    
    return text_blocks

def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def segment_combined_text_by_question(combined_text):
    segmented_answers = []
    current_answer = []
    
    lines = combined_text.split('\n')
    for line in lines:
        text = preprocess_text(line)
        
        if re.match(r'^Q\.\d+', text):
            if current_answer:
                segmented_answers.append(' '.join(current_answer))
                current_answer = []
        
        current_answer.append(text)
    
    if current_answer:
        segmented_answers.append(' '.join(current_answer))
    
    return segmented_answers

def process_and_store_student_answers(image_paths):
    combined_text = ""
    for image_path in image_paths:
        text_blocks = extract_text_and_bounding_boxes(image_path)
        for block in text_blocks:
            combined_text += block['text'] + "\n"
    
    segmented_answers = segment_combined_text_by_question(combined_text)
    return segmented_answers
