# have all functions relate to generating Chapters, Exam, and Exercise

from .models import Course, Chapter, UserKnowledge, Question, Exercise
from django.contrib.auth.models import User
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
    # skipped until user knowledge is fixed
    # system_prompt = f"""You are an expert course creator. Analyze the course content and user's knowledge level to determine what content needs to be covered.
    # User's current knowledge level: {user_knowledge.knowledge_level if user_knowledge else 'beginner'}"""

    # messages = [
    #     {"role": "user", "content": f"Course content: {course.content}\nPlease analyze and return the content that needs to be covered."}
    # ]

    # # Get filtered content
    # filtered_content = llm_caller.generate_response(messages, system_prompt)
    filtered_content = course.content

    print("generate_course: 3")

    # Prepare prompt for chapter generation
    system_prompt = """
<role>
You are an expert course creator. 
Split the course content into logical chapters.
Each chapter must cover a different part of the course's content.
</role>

Return the response in the following JSON format:
{
    "chapters": [
        {
            "name": "Chapter name",
            "content": "A short list of the content of this Chapter. Just enough that an expert at this subject will understand what this chapter is about."
        }
    ]
}
"""
# "content": "A short summary of the content of this Chapter. Just enough that an expert at this subject will understand what this chapter is about."
    messages = [
        {"role": "user", "content": f"Please split this content into chapters: {filtered_content}"}
    ]

    # Get chapters structure
    chapters_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    # slice output to remove '''json and '''
    # print(f"generate_course: json: {chapters_json}")
    chapters_data = json.loads(chapters_json)

    print("generate_course: 4")

    # Generate each chapter
    chapters = chapters_data['chapters']
    chapter_count = len(chapters)
    for index, chapter_data in enumerate(chapters, start=1):
        # index = index inside chapters[]+1

        chapter_name = chapter_data['name']
        chapter_summary = chapter_data['content']
        
        # check if the next chapter exist
        has_next_chapter = index < chapter_count
        system_prompt_prev_chapter = ""
        system_prompt_next_chapter = ""
        message_prev_chapter = ""
        message_next_chapter = ""
        if has_next_chapter:
            next_chapter = chapters[index]
            next_chapter_summary = next_chapter['content']
            system_prompt_next_chapter = "- Summary of the next chapter, inside the <next_summary> tags"
            message_next_chapter = f"<next_summary>{next_chapter_summary}</next_summary>"

        # check if the prev chapter exist
        has_prev_chapter = index > 0
        if has_prev_chapter:
            prev_chapter = chapters[index - 2]
            prev_chapter_summary = prev_chapter['content']
            system_prompt_prev_chapter = "- Summary of the previous chapter, inside the <prev_summary> tags"
            message_prev_chapter = f"<prev_summary>{prev_chapter_summary}</prev_summary>"

        output_format = """
{
    "content": "the entire text content of the chapter"
}
"""

# <role>
# You are an expert course creator.
# Your job is to create a chapter of a course.
# The chapter must be short, concise, while still cover everything in the chapter's summary
# Each chapter must cover a different part of the course's content.
# </role>

# You will be given the following as input:
# <input>
# - The entire text content of the course, inside to <full_content> tags
# - Name of the chapter, inside the <name> tags
# - Summary of the chapter, inside the <summary> tags
# {system_prompt_prev_chapter}
# {system_prompt_next_chapter}
# </input>

        system_prompt_2 = f"""
<role>
You are an expert course creator.
Your job is to create a chapter of a course.
The chapter must be short, concise, while still cover everything in the chapter's summary
Each chapter must cover a different part of the course's content.
Decorate the content using HTML tags only
</role>

You will be given the following as input:
<input>
- Name of the chapter, inside the <name> tags
- Summary of the chapter, inside the <summary> tags
{system_prompt_prev_chapter}
{system_prompt_next_chapter}
</input>

You must output the text content of the chapter
Return the response in the following JSON format:
{output_format}
"""

# """
# <full_content>{filtered_content}</full_content>
# <name>{chapter_name}</name>
# <summary>{chapter_summary}</summary>
# {message_prev_chapter}
# {message_next_chapter}
# """

        messages_2 = [
            {
                "role": "user", "content": f"""
<name>{chapter_name}</name>
<summary>{chapter_summary}</summary>
{message_prev_chapter}
{message_next_chapter}
"""
            }
        ]

        chapter_json = llm_caller.generate_response(messages_2, system_prompt_2)[7:-3]
        chapter_data_2 = json.loads(chapter_json)

        generate_chapter(user, course, chapter_name, chapter_data_2['content'])

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

    print("generate_chapter: 1")

    # Create and save the Chapter object
    chapter = Chapter.objects.create(
        user=user,
        course=course,
        name=name,
        content=content
    )

    print("generate_chapter: 2")
    
    # create exercise for the chapter
    generate_exercise(chapter)

    print("generate_chapter: done")
    print(f"content: {content}")
    
    return chapter

def generate_question(text, golden_answer, type):
    """
    Generate a question object of an exam/exercise, which include:
        text: the question text
        golden answer
        question type: exam or exercise
    """

    # Create Question object
    question = Question.objects.create(
        text=text,
        golden_answer=golden_answer,
        question_type=type
    )

    return question

def generate_exercise(chapter):
    """
    Generate an exercise object of a chapter, which include:
        questions
        golden answers
    """

    # Initialize LLM caller
    llm_caller = LLMCaller()

    # get chapter's name & content
    chapter_name = chapter.name
    chapter_content = chapter.content

    # Generate questions and answers using LLM
    system_prompt_3 = """"
<role>
You are an expert course creator.
Your job is to create a set of questions and answers for a chapter of a course.
Each question is an open question, and the answer is a short text.
The questions must be related to the chapter's content.
The combination of questions must cover the entire content of the chapter.
</role>

You will be given the following as input:
<input>
- Name of the chapter, inside the <name> tags
- The entire text content of the chapter, inside the <content> tags
</input>

Return the response in the following JSON format:
{
    "questions": [
        {
            "question_text": "The text of the question",
            "golden_answer": "The best answer to the question"
        }
    ]
}
"""

    messages_3 = [
        {
            "role": "user", "content": f"""
<name>{chapter_name}</name>
<content>{chapter_content}</content>
"""
        }
    ]

    # Get questions and answers
    exercise_json = llm_caller.generate_response(messages_3, system_prompt_3)[7:-3]
    exercise_data = json.loads(exercise_json)

    # Create the Exercise object
    exercise = Exercise.objects.create(
        chapter=chapter
    )

    questions = exercise_data['questions']
    # Create and save each Question object
    for question_data in questions:
        question_text = question_data['question_text']
        golden_answer = question_data['golden_answer']

        # Create Question object
        question = generate_question(
            text=question_text,
            golden_answer=golden_answer,
            type='EXERCISE'
        )
        question.save()

        # Add the question to the Exercise object
        exercise.questions.add(question)

    # Save the Exercise object
    exercise.save()
    return None