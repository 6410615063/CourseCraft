from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Course, Chapter, UserKnowledge
from .generator import generate_course
from .forms import UserKnowledgeForm
from llm_integration.llm_caller_3 import LLMCaller
import json

# Create your views here.

@login_required
def generate_course_view(request):
    if request.method == 'POST':
        print("generate_course: form filled")

        try:
            data = json.loads(request.body)
            topic = data.get('topic')
            knowledge_level = data.get('knowledge_level')
            
            print("generate_course: 1")

            # Get user's knowledge level for the topic
            user_knowledge = UserKnowledge.objects.filter(
                user=request.user,
                topic=topic
            ).first()
            
            print("generate_course: 2")

            # Prepare the prompt for the LLM
            llm_caller = LLMCaller()
            system_prompt = f"""You are an expert course creator. Create a personalized course for {request.user.username} 
            on the topic of {topic}. The user's current knowledge level is {user_knowledge.knowledge_level if user_knowledge else 'beginner'}.
            The target knowledge level is {knowledge_level}."""
            
            messages = [
                {"role": "user", "content": f"Please create a comprehensive course on {topic}."}
            ]
            
            # Generate course content (currently as a str, might turn into json later)
            course_content = llm_caller.generate_response(messages, system_prompt)
            
            print("generate_course: 3")

            # Create new course
            course = Course.objects.create(
                user=request.user,
                title=f"{topic.title()} Course",
                description=f"Personalized course on {topic}",
                content=course_content,
                knowledge_level=knowledge_level
            )
            
            print("generate_course: 4")

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
    
    if request.method == 'POST':
        # Start course generation
        generate_course(user, course)
        messages.success(request, 'Course generation started!')
        return redirect('course_generation:course_detail', course_id=course.id)
    
    return render(request, 'course_generation/course_detail.html', {
        'course': course,
        'chapters': user_chapters
    })

@login_required
def chapter_detail(request, chapter_id):
    """Display chapter content"""
    chapter = get_object_or_404(Chapter, id=chapter_id, user=request.user)
    return render(request, 'course_generation/chapter_detail.html', {'chapter': chapter})

@login_required
def update_knowledge(request):
    """Update user's knowledge level for a topic"""
    if request.method == 'POST':
        form = UserKnowledgeForm(request.POST)
        if form.is_valid():
            knowledge = form.save(commit=False)
            knowledge.user = request.user
            knowledge.save()
            messages.success(request, 'Knowledge level updated successfully!')
            return redirect('course_list')
    else:
        form = UserKnowledgeForm()
    
    return render(request, 'course_generation/update_knowledge.html', {'form': form})
