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
        unknown_list_for_extra_chapter = []
        # Handle exercise submission
        for question in questions:
            question_id = question.id
            user_answer = request.POST.get(f'answer_{question_id}')

            print(f"User answer for question #{question_id}: {user_answer}")
            # Validate the answer
            score = evaluate_answer2(question, user_answer)
            print(f"Score: {score}")

            # determine user's knowledge
            knowledge_json = determine_knowledge(question, user_answer, score)
            knowledge_list = knowledge_json['knowledge']
            print(f"Knowledge: {knowledge_list}")
            unknown_list = knowledge_json['unknown']
            print(f"Unknown: {unknown_list}")

            # Update user knowledge
            user_knowledge = UserKnowledge.objects.filter(user=request.user).first()
            if user_knowledge:
                user_knowledge.knowledge_list.extend(knowledge_list)
                user_knowledge.unknown_list.extend(unknown_list)
                user_knowledge.save()
            else:
                UserKnowledge.objects.create(
                    user=request.user,
                    knowledge_list=knowledge_list,
                    unknown_list=unknown_list
                )
            update_user_knowledge(user_knowledge)

            # Determine if extra chapter is needed
            if score < 0.5:
                # add unknown to the list of unknown to based extra chapter on
                unknown_list_for_extra_chapter.extend(unknown_list)
            print("-------------------")
        # Check if extra chapter is needed
        if unknown_list_for_extra_chapter:
            # Generate extra chapter based on unknown_list
            # extra_chapter = generate_extra_chapter(request.user, unknown_list_for_extra_chapter)
            pass
    # Logic to display the exercise page

    context = {
        'chapter_name': chapter_name,
        'chapter_id': chapter_id,
        'questions': questions,
    }

    return render(request, 'exam_and_evaluation/exercise.html', context)