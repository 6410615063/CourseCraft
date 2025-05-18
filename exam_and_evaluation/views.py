from django.shortcuts import render
from course_generation.models import Course, Chapter, UserKnowledge, Question, Exercise
from django.contrib.auth.decorators import login_required
from exam_and_evaluation.evaluate_answer import *

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
    
    # Fetch the exercise data based on chapter_id
    chapter = Chapter.objects.filter(id=chapter_id).first()
    if chapter:
        chapter_name = chapter.name if chapter else "Chapter not found"
        chapter_id = chapter.id
    else:
        chapter_name = "Chapter not found"
        chapter_id = None

    exercise = Exercise.objects.filter(chapter_id=chapter_id).first()
    if exercise:
        questions = exercise.questions.all()
    else:
        questions = []

    if request.method == 'POST':
        # Handle exercise submission

        for question in questions:
            question_id = question.id
            user_answer = request.POST.get(f'answer_{question_id}')

            print(f"User answer for question #{question_id}: {user_answer}")
            # Validate the answer
            if evaluate_answer(question, user_answer):
                # Correct answer logic
                print(f"Answered correctly.")
                pass
            else:
                # Incorrect answer logic
                print(f"Answered incorrectly.")
                pass
            score = evaluate_answer2(question, user_answer)
            print(f"Score: {score}")

            # determine user's knowledge
            knowledge_json = determine_knowledge(question, user_answer, score)
            knowledge_list = knowledge_json['knowledge']
            print(f"Knowledge: {knowledge_list}")
            unknown_list = knowledge_json['unknown']
            print(f"Unknown: {unknown_list}")

        # Validate and grade the exercise
        pass

    # Logic to display the exercise page

    context = {
        'chapter_name': chapter_name,
        'chapter_id': chapter_id,
        'questions': questions,
    }

    return render(request, 'exam_and_evaluation/exercise.html', context)