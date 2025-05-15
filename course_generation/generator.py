# have all functions relate to generating Chapters, Exam, and Exercise

from .models import Course, Chapter, UserKnowledge
from llm_integration.llm_caller_3 import LLMCaller
import json

def generate_course(user, course):
    """
    Generate personalized chapters for a user based on a course's content.
    The course object contains the base content, and this function will:
    1. Analyze user's knowledge level
    2. Filter and adapt the content
    3. Create personalized chapters

    Input:
    user: user object. to get knowledge & assign the chapters to
    course: course object. to get content from & assign chapters to
    """

    print("generate_course: 1")

    # Initialize LLM caller
    llm_caller = LLMCaller()

    # Get user's knowledge for the course topic
    user_knowledge = UserKnowledge.objects.filter(
        user=user,
        topic=course.title
    ).first()

    print("generate_course: 2")

    # Prepare the prompt for content filtering
    system_prompt = f"""You are an expert course creator. Analyze the course content and user's knowledge level to determine what content needs to be covered.
    User's current knowledge level: {user_knowledge.knowledge_level if user_knowledge else 'beginner'}"""

    messages = [
        {"role": "user", "content": f"Course content: {course.content}\nPlease analyze and return the content that needs to be covered."}
    ]

    # Get filtered content
    filtered_content = llm_caller.generate_response(messages, system_prompt)

    print("generate_course: 3")

    # Prepare prompt for chapter generation
    system_prompt = """You are an expert course creator. Split the course content into logical chapters.
    Return the response in the following JSON format:
    {
        "chapters": [
            {
                "name": "Chapter name",
                "content": "Chapter content"
            }
        ]
    }"""

    messages = [
        {"role": "user", "content": f"Please split this content into chapters: {filtered_content}"}
    ]

    # Get chapters structure
    chapters_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    print(f"generate_course: json: {chapters_json}")
    chapters_data = json.loads(chapters_json)

    print("generate_course: 4")

    # Generate each chapter
    for chapter_data in chapters_data['chapters']:
        generate_chapter(user, course, chapter_data['name'], chapter_data['content'])

    return course

def generate_chapter(user, course, name, content):
    """
    Goal:
        Generate a chapter object of a course, which include:
        pages of content
        exercise

    Input:
        user: user obj. chapter owner
        course: course obj. chapter owner
        name: string. chapter's name
        content: string.
    """
    # Create and save the Chapter object
    chapter = Chapter.objects.create(
        user=user,
        course=course,
        name=name,
        content=content
    )
    
    return chapter

def generate_exercise():
    return None