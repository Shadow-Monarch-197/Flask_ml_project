# Assign marks based on similarity score
def assign_marks(similarity_score, max_marks=5):
    return round(similarity_score * max_marks, 2)

# Calculate marks for student answers based on similarity
def calculate_marks_for_student_answers(similarity_scores, max_marks=5):
    student_marks_results = []
    for scores in similarity_scores:
        best_match_score = max(scores)
        marks = assign_marks(best_match_score, max_marks)
        student_marks_results.append(marks)
    return student_marks_results
