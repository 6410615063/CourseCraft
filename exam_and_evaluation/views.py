from django.shortcuts import render, redirect, get_object_or_404
from course_generation.models import Course, Chapter, UserKnowledge, Question, Exercise, Exam
from django.contrib.auth.decorators import login_required
from exam_and_evaluation.evaluate_answer import *
from course_generation.generator import generate_extra_chapter, generate_course

# Create your views here.

def exam_view(request, course_id, is_final_str):
    """
    View to handle exam-related requests.

    GET: Display the exam page.
    POST: Handle exam submission and grading.
    """
    # Logic to handle exam generation, submission, etc.
    
    user = request.user

    is_final = False
    exam_type = "Pre"
    if is_final_str == "True":
        is_final = True
        exam_type = "Final"

    # get course
    course = Course.objects.filter(id=course_id).first()
    course_name = course.title

    # get exam
    exam = Exam.objects.filter(course_id=course_id, is_final=is_final).first()
    questions = exam.questions.all()

    # POST = submit answers
    if request.method == 'POST':
        # handle answers

        unknown_list_for_extra_chapter = []
        for question in questions:
            # get answers
            question_id = question.id
            user_answer = request.POST.get(f'answer_{question_id}')
            print(f"User answer for question #{question_id}: {user_answer}")
        
            # grade answers
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
            if not user_knowledge:
                user_knowledge = UserKnowledge.objects.create(
                    user=request.user,
                    knowledge_list=knowledge_list,
                    unknown_list=unknown_list
                )
            user_knowledge.knowledge_list.extend(knowledge_list)
            user_knowledge.unknown_list.extend(unknown_list)
            user_knowledge.save()
            update_user_knowledge(user_knowledge)

            # Determine if extra chapter is needed
            if score < 0.8:
                # add unknown to the list of unknown to based extra chapter on
                unknown_list_for_extra_chapter.extend(unknown_list)
            print("-------------------")

        if not is_final:
        # if pre-course:
        #     generate starting chapter
            print("Generating Starting Chapter")
            generate_course(user, course)
        else:
        # if final:
                # Check if extra chapter is needed
            if unknown_list_for_extra_chapter:
                # Generate extra chapter based on unknown_list

                print("Generating Extra Chapter")
                generate_extra_chapter(user, course, unknown_list_for_extra_chapter)
            else:
                print("No Extra Chapter required")

        # redirect to course_detail page
        return redirect('course_generation:course_detail', course_id=course.id)

    # GET = start exam
    context = {
        'course_name': course_name,
        'course_id': course_id,
        'exam_type': exam_type,
        'questions': questions
    }
    return render(request, 'exam_and_evaluation/exam.html', context)

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
            if not user_knowledge:
                user_knowledge = UserKnowledge.objects.create(
                    user=request.user,
                    knowledge_list=knowledge_list,
                    unknown_list=unknown_list
                )
            user_knowledge.knowledge_list.extend(knowledge_list)
            user_knowledge.unknown_list.extend(unknown_list)
            user_knowledge.save()
            update_user_knowledge(user_knowledge)

            # Determine if extra chapter is needed
            if score < 0.5:
                # add unknown to the list of unknown to based extra chapter on
                unknown_list_for_extra_chapter.extend(unknown_list)
            
            # Update that user has done the exercise
            exercise.is_done = True
            exercise.save()
            chapter.is_done = True
            chapter.save()

            print("-------------------")
        # Check if extra chapter is needed
        if unknown_list_for_extra_chapter:
            # Generate extra chapter based on unknown_list

            print("Generating Extra Chapter")

            # Get the course associated with the chapter
            course = chapter.course
            user = request.user

            # Generate extra chapter using the unknown_list
            generate_extra_chapter(user, course, unknown_list_for_extra_chapter)
        else:
            print("No Extra Chapter required")
    
        # redirect to the course detail page
        return redirect('course_generation:course_detail', course_id=chapter.course.id)

    # If GET request, display the exercise page
    context = {
        'chapter_name': chapter_name,
        'chapter_id': chapter_id,
        'questions': questions,
    }

    return render(request, 'exam_and_evaluation/exercise.html', context)