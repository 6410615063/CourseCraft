from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Course, UserKnowledge
from llm_integration.llm_caller_3 import LLMCaller
import json

# Create your views here.

@login_required
def generate_course(request):
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
            # print(f"generate_course: {request.user}")
            # print(f"generate_course: {topic.title()}")
            # print(f"generate_course: {topic}")
            # print(f"generate_course: {json.loads(course_content)}")
            # print(f"generate_course: {knowledge_level}")

            # Create new course
            course = Course.objects.create(
                user=request.user,
                title=f"{topic.title()} Course",
                description=f"Personalized course on {topic}",
                # content=json.loads(course_content),
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
    courses = Course.objects.filter(user=request.user)
    return render(request, 'course_generation/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = Course.objects.get(id=course_id, user=request.user)
    return render(request, 'course_generation/course_detail.html', {'course': course})
