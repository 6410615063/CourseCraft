# have all functions relate to generating Chapters, Exam, and Exercise

from .models import Course, Chapter, UserKnowledge, Question, Exercise, Exam
from django.contrib.auth.models import User
from llm_integration.llm_caller_3 import LLMCaller
import json

def describe(content):
    """
    Describe the given content.

    Input:
    content: string. The entire text of the content
    """

    # Initialize LLM caller
    llm_caller = LLMCaller()

    # Prepare the prompt for summarization
    system_prompt = """
    <role>
    You are an expert summarizer.
    Your job is to create a description of what's in a course.
    The description should be short and concise.
    </role>

    You will be given the following as input:
    <input>
    - The entire text content of the course, inside the <full_content> tags
    </input>

    Return the response in the following JSON format:
{
    description": "the description of the course"
}
    """

    messages = [
        {"role": "user", "content": f"""
    <full_content>{content}</full_content>
    """
        }
    ]

    # Get description
    description_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    print(f"describe: json = {description_json}")
    description_data = json.loads(description_json)
    description = description_data['description']
    
    return description

def summarize(content):
    """
    Summarize the given content.
    This function will:
    1. Analyze the course content
    2. Generate a summary
    3. Return the summary

    Input:
    content: string. The entire text of the content
    """

    # Initialize LLM caller
    llm_caller = LLMCaller()

    # Prepare the prompt for summarization
    system_prompt = """
    <role>
    You are an expert summarizer.
    Your job is to summarize the given text content.
    The summary should not be too long, while still cover everything in the content.
    </role>

    You will be given the following as input:
    <input>
    - The entire text content, inside the <full_content> tags
    </input>

    Return the response in the following JSON format:
{
    "summary": "the summary of the content"
}
    """

    messages = [
        {"role": "user", "content": f"""
    <full_content>{content}</full_content>
    """
        }
    ]

    # Get summary
    summary_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    summary_data = json.loads(summary_json)
    summary = summary_data['summary']
    
    return summary

def filter_knowledge(summary, knowledge_list):
    """
    Filter the course summary based on the user's knowledge list.
    This function will:
    1. Analyze the course summary
    2. Remove the content that is already known by the user
    3. Return the filtered summary

    Input:
    summary: string. The entire text of the course summary
    knowledge_list: list of strings. The user's knowledge list
    """

    # Turn the list of knowledge into a string
    knowledge_list_str = ', '.join(knowledge_list)

    # Initialize LLM caller
    llm_caller = LLMCaller()

    # Prepare the prompt for filtering
    system_prompt = """
    <role>
    You are an expert course filter.
    Your job is to filter the course summary based on the user's knowledge list.
    The filtered summary should not include the content that is already known by the user.
    </role>

    You will be given the following as input:
    <input>
    - The entire text content of the course summary, inside the <full_content> tags
    - The user's knowledge list, inside the <knowledge_list> tags
    </input>

    Return the response in the following JSON format:
{
    "filtered_summary": "the filtered summary of the course"
}
    """

    messages = [
        {"role": "user", "content": f"""
    <full_content>{summary}</full_content>
    <knowledge_list>{knowledge_list_str}</knowledge_list>
    """
        }
    ]

    # Get filtered summary
    filtered_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    filtered_data = json.loads(filtered_json)
    filtered_summary = filtered_data['filtered_summary']
    
    return filtered_summary

def filter_unknown(summary, unknown_list):
    """
    Filter the course summary based on the user's unknown list.
    This function will:
    1. Analyze the course summary
    2. Keep only the content that is related to the unknown list
    3. Return the filtered summary

    Input:
    summary: string. The entire text of the course summary
    unknown_list: list of strings. The user's unknown list
    """

    # Turn the list of unknown into a string
    unknown_list_str = ', '.join(unknown_list)

    # Initialize LLM caller
    llm_caller = LLMCaller()

    # Prepare the prompt for filtering
    system_prompt = """
    <role>
    You are an expert course filter.
    Your job is to filter the course summary based on the user's unknown list.
    The filtered summary should only include the content that is related to the unknown list.
    </role>

    You will be given the following as input:
    <input>
    - The entire text content of the course summary, inside the <full_content> tags
    - The user's unknown list, inside the <unknown_list> tags
    </input>

    Return the response in the following JSON format:
{
    "filtered_summary": "the filtered summary of the course"
}
    """

    messages = [
        {"role": "user", "content": f"""
    <full_content>{summary}</full_content>
    <unknown_list>{unknown_list_str}</unknown_list>
    """
        }
    ]

    # Get filtered summary
    filtered_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    filtered_data = json.loads(filtered_json)
    filtered_summary = filtered_data['filtered_summary']
    return filtered_summary

def split_into_chapters(content):
    """
    Split the course content into chapters.
    This function will:
    1. Analyze the content
    2. Split it into logical chapters
    3. Return the chapters structure

    Input:
    content: string. The entire text content of the course

    Output:
    chapters: list of dictionaries. Each dictionary contains:
        - name: string. The name of the chapter
        - content: string. The content of the chapter
    """

    # Initialize LLM caller
    llm_caller = LLMCaller()

    # Prepare the prompt for chapter generation
    system_prompt = """
    <role>
    You are an expert course creator. 
    Split the course content into logical chapters.
    Each chapter must cover a different part of the course's content.
    </role>

    You will be given the following as input:
    <input>
    - The entire text content of the course, inside the <full_content> tags
    </input>

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

    messages = [
        {"role": "user", "content": f"""
    <full_content>{content}</full_content>
    """
        }
    ]

    # Get chapters structure
    chapters_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    # slice output to remove '''json and '''
    # print(f"generate_course: json: {chapters_json}")
    chapters_data = json.loads(chapters_json)
    chapters = chapters_data['chapters']
    return chapters

def generate_chapter(name, summary):
    """
    Generate content of a chapter.

    Input:
    name: string. The name of the chapter
    summary: string. The summary of the chapter
    """

    # Initialize LLM caller
    llm_caller = LLMCaller()

    # Prepare the prompt for chapter generation
    system_prompt = """
    <role>
    You are an expert course creator.
    Your job is to create a chapter of a course.
    The chapter should be short and cocise
    The chapter must cover everything in the chapter's summary
    Decorate the content using HTML tags only
    </role>

    You will be given the following as input:
    <input>
    - Name of the chapter, inside the <name> tags
    - Summary of the chapter, inside the <summary> tags
    </input>

    Return the response in the following JSON format:
{
    "content": "the entire text content of the chapter"
}
    """
    
    messages = [
        {"role": "user", "content": f"""
    <name>{name}</name>
    <summary>{summary}</summary>
    """
        }
    ]

    # Get chapter content
    chapter_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    chapter_data = json.loads(chapter_json)
    chapter_content = chapter_data['content']
    
    return chapter_content

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

    # summarize the course content
    course_content = course.content
    course_summary = summarize(course_content)

    print("generate_course: 1")

    # filter the course content based on the user's knowledge
    user_knowledge = UserKnowledge.objects.filter(user=user).first()
    filtered_summary = filter_knowledge(course_summary, user_knowledge.knowledge_list if user_knowledge else [])
    print(f"filtered summary: {filtered_summary}")

    print("generate_course: 2")

    # split the course content into chapters
    chapters = split_into_chapters(filtered_summary)

    print("generate_course: 3")

    # Generate each chapter
    for chapter_data in chapters:

        chapter_name = chapter_data['name']
        chapter_summary = chapter_data['content']
        
        # Generate chapter content
        chapter_content = generate_chapter(chapter_name, chapter_summary)

        # Create and save the Chapter object
        create_chapter(user, course, chapter_name, chapter_content)

def create_chapter(user, course, name, content):
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

def generate_extra_chapter(user, course, target_unknown):
    """
    Goal:
        Generate chapter object(s) of a course, which include:
        pages of content
        exercise

    Input:
        user: user obj. chapter owner
        course: course obj. chapter owner
        target_unknown: list of unknowns to cover in the extra chapter
    """

    # plan
    # 1. get the course content
    # 2. cut it down to the unknowns
    # 3. split it into chapters
    # 4. generate each chapter

    # summarize the course content
    course_content = course.content
    course_summary = summarize(course_content)

    print("generate_extra: 1")
    print(f"target unknown = {target_unknown}")
    print(f"course_summary = {course_summary}")

    # filter the course content based on the user's knowledge and unknowns
    user_knowledge = UserKnowledge.objects.filter(user=user).first()
    filtered_summary = filter_knowledge(course_summary, user_knowledge.knowledge_list if user_knowledge else [])

    print(f"filtered(knowledge) = {filtered_summary}")

    filtered_summary = filter_unknown(filtered_summary, target_unknown)

    print(f"filtered(unknown) = {filtered_summary}")

    print("generate_extra: 2")

    # split the course content into chapters
    chapters = split_into_chapters(filtered_summary)

    print(f"chapters_list = {chapters}")

    print("generate_extra: 3")

    # Generate each chapter
    for chapter_data in chapters:

        chapter_name = f"Extra: {chapter_data['name']}"
        chapter_summary = chapter_data['content']
        
        # Generate chapter content
        chapter_content = generate_chapter(chapter_name, chapter_summary)

        # Create and save the Chapter object
        create_chapter(user, course, chapter_name, chapter_content)

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
    system_prompt = """"
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

    messages = [
        {
            "role": "user", "content": f"""
    <name>{chapter_name}</name>
    <content>{chapter_content}</content>
    """
        }
    ]

    # Get questions and answers
    exercise_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
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

def generate_exam(course, is_final):
    """
    Generate an exercise object of a chapter, which include:
        questions
        golden answers
    """

    # Initialize LLM caller
    llm_caller = LLMCaller()

    # Get course content
    course_content = course.content
    course_name = course.title

    # prepare parts of system prompt
    if is_final:
        before_or_after = "after"
    else:
        before_or_after = "before"
    response_format = {
        "questions": [
            {
                "question_text": "The text of the question",
                "golden_answer": "The best answer to the question"
            }
        ]
    }

    # prepare system prompt
    system_prompt = f"""
    <role>
    You are an expert course creator.
    Your job is to create a set of questions and answers for a course.
    Each question is an open question, and the answer is a short text.
    The questions must be related to the course's content.
    The combination of questions must cover the entire content of the course.
    The question will be given to the user {before_or_after} they study the course.
    The exam must have no more than 10 questions
    </role>

    You will be given the following as input:
    <input>
    - Name of the course, inside the <name> tags
    - The entire text content of the course, inside the <content> tags
    </input>

    Return the response in the following JSON format:
    {response_format}
    """

    messages = [
        {
            "role": "user", "content": f"""
    <name>{course_name}</name>
    <content>{course_content}</content>
    """
        }
    ]
    
    # Get questions and answers
    exam_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    print(f"generate_exam: json = {exam_json}")
    exam_data = json.loads(exam_json)

    # Create the Exam object
    exam = Exam.objects.create(
        course=course,
        is_final=is_final
    )

    questions = exam_data['questions']
    # Create and save each Question object
    for question_data in questions:
        question_text = question_data['question_text']
        golden_answer = question_data['golden_answer']

        # Create Question object
        question = generate_question(
            text=question_text,
            golden_answer=golden_answer,
            type='EXAM'
        )
        question.save()

        # Add the question to the Exam object
        exam.questions.add(question)

    # Save the Exam object
    exam.save()
    return None