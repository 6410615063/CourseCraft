from django.shortcuts import render
from course_generation.models import Course, Chapter, UserKnowledge, Question, Exercise
from django.contrib.auth.decorators import login_required

# Create your views here.

def exam_view(request, course_id, is_final):
    """
    View to handle exam-related requests.

    GET: Display the exam page.
    POST: Handle exam submission and grading.
    """
    # Logic to handle exam generation, submission, etc.
    return render(request, 'exam.html')

def exercise_view(request, chapter_id):
    """
    View to handle exercise-related requests.
    
    GET: Display the exercise page.
    POST: Handle exercise submission and grading.
    """
    # Logic to handle exercise generation, submission, etc.
    if request.method == 'POST':
        # Handle exercise submission
        # Validate and grade the exercise
        pass

    # Logic to display the exercise page
    # Fetch the exercise data based on chapter_id
    chapter = Chapter.objects.filter(id=chapter_id).first()
    chapter_name = chapter.name if chapter else "Chapter not found"
    
    exercise = Exercise.objects.filter(chapter_id=chapter_id).first()
    if exercise:
        questions = exercise.questions.all()
    else:
        questions = []

    context = {
        'chapter_name': chapter_name,
        'questions': questions,
    }

    return render(request, 'exam_and_evaluation/exercise.html', context)