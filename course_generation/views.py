from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Course, Chapter, UserKnowledge
from .generator import generate_course, generate_exam, describe
# from .forms import UserKnowledgeForm
from llm_integration.llm_caller_3 import LLMCaller
import json

# Create your views here.

@login_required
def generate_course_view(request):
    if request.method == 'POST':
        print("generate_course: form filled")

        try:
            # get course name(topic) and content(content)
            data = json.loads(request.body)
            topic = data.get('topic')
            content = data.get('content')

            print("generate_course: generating description")
            description = describe(content)

            # make a course object with name and content
            course = Course.objects.create(
                title=topic,
                description=description,
                content=content
            )

            try:
                print("generate_course: generating pre exam")
                generate_exam(course, False)
                print("generate_course: generating final exam")
                generate_exam(course, True)
            except Exception as e:
                # if there is error when creating any exam, delete the course
                course.delete()
                raise

            # redirect to course_list page (for AJAX, return JSON with course_id)
            return JsonResponse({
                'status': 'success',
                'course_id': course.id,
                'message': 'Course generated successfully'
            })

        except Exception as e:
            print("generate_course: error")

            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

    print("generate_course: entering page")

    return render(request, 'course_generation/generate_course.html')

@login_required
def course_list(request):
    """Display list of available courses"""
    courses = Course.objects.all()
    return render(request, 'course_generation/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    """Display course details and allow user to start course generation"""
    course = get_object_or_404(Course, id=course_id)
    user = request.user
    user_chapters = Chapter.objects.filter(user=request.user, course=course)
    
    # TODO: this should get removed once chapter is created after pre exam
    # if request.method == 'POST':
    #     # Start chapter generation
    #     generate_course(user, course)
    #     messages.success(request, 'Course generation started!')
    #     return redirect('course_generation:course_detail', course_id=course.id)
    
    return render(request, 'course_generation/course_detail.html', {
        'course': course,
        'chapters': user_chapters
    })

@login_required
def chapter_detail(request, chapter_id):
    """Display chapter content"""
    chapter = get_object_or_404(Chapter, id=chapter_id, user=request.user)
    return render(request, 'course_generation/chapter_detail.html', {'chapter': chapter})

# @login_required
# def update_knowledge(request):
#     """Update user's knowledge level for a topic"""
#     if request.method == 'POST':
#         form = UserKnowledgeForm(request.POST)
#         if form.is_valid():
#             knowledge = form.save(commit=False)
#             knowledge.user = request.user
#             knowledge.save()
#             messages.success(request, 'Knowledge level updated successfully!')
#             return redirect('course_list')
#     else:
#         form = UserKnowledgeForm()
    
#     return render(request, 'course_generation/update_knowledge.html', {'form': form})
