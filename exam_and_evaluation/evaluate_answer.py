import json
from course_generation.models import Question, Exercise
from llm_integration.llm_caller_3 import LLMCaller

def evaluate_answer(question, answer):
    """
    Evaluate the answer provided by the user against the golden answer of the question.
    
    Args:
        question (Question): The question object containing the golden answer.
        answer (str): The user's answer to the question.
    
    Returns:
        bool: True if the answer is correct, False otherwise.
    """
    # Normalize both answers for comparison
    normalized_golden_answer = question.golden_answer.strip().lower()
    normalized_user_answer = answer.strip().lower()
    
    return normalized_golden_answer == normalized_user_answer

# same as above, but use LLM for evaluation
def evaluate_answer2(question, answer):
    """
    Evaluate the answer provided by the user against the golden answer of the question.
    
    Args:
        question (Question): The question object containing the golden answer.
        answer (str): The user's answer to the question.
    
    Returns:
        bool: True if the answer is correct, False otherwise.
    """
    # Normalize both answers for comparison
    normalized_golden_answer = question.golden_answer.strip().lower()
    normalized_user_answer = answer.strip().lower()

    # initialize LLM caller
    llm_caller = LLMCaller()

    # Prepare the prompt for the LLM
    system_prompt = """
<role>
You are an expert evaluator.
You job is to evaluate the user's answer to the question.
</role>

You will be given the following as input:
<input>
- The question, inside the <question> tags
- The best answer to the question, inside the <golden_answer> tags
- The user's answer to the question, inside the <user_answer> tags
</input>

Return the response in the following JSON format:
{
    "score": "a decimal number between 0 and 10",
    "explanation": "a short string of why you give this score"
}

Use the following criteria to determine the score:
<criteria>
- The answer is correct and complete: 10
- The answer is partially correct: 5
- The answer is incorrect: 0
</criteria>
"""

    messages = [
        {
            "role": "user", "content": f"""
<question>{question.text}</question>
<golden_answer>{question.golden_answer}</golden_answer>
<user_answer>{answer}</user_answer>
"""
        }
    ]

    # Generate evaluation using LLM
    score_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    score_data = json.loads(score_json)

    # Parse the response to get the score
    try:
        score = float(score_data['score'])
    except ValueError:
        raise ValueError("Invalid response from LLM. Unable to parse score.")

    # print the explanation
    explanation = score_data.get('explanation', '')
    if explanation:
        print(f"LLM Explanation: {explanation}")
    
    return score

def determine_knowledge(question, answer, score):
    """
    Determine the knowledge level of the user based on the score.
    
    Args:
        question (Question): The Question object,  containing the question text and the golden answer.
        answer (str): The user's answer to the question.
        score (float): The score given by the LLM.
    
    Returns:
        json: a group of strings of what the user knows or not.
    """
    # Initialize LLM caller
    llm_caller = LLMCaller()

    # Prepare the prompt for the LLM
    system_prompt = """
<role>
You are an expert evaluator.
You job is to determine what the user know or not know based on how well they answered the question.
</role>

You will be given the following as input:
<input>
- The question, inside the <question> tags
- The best answer to the question, inside the <golden_answer> tags
- The user's answer to the question, inside the <user_answer> tags
- The score given by the LLM, represent how good the user's answer is, inside the <score> tags
</input>

Return the response in the following JSON format:
{
    "knowledge": [
        "a short string of what the user knows or not"
    ],
    "unknown": [
        "a short string of what the user doesn't know"
    ]
}

Both knowledge and unknown could be empty.
"""

    messages = [
        {
            "role": "user", "content": f"""
<question>{question.text}</question>
<golden_answer>{question.golden_answer}</golden_answer>
<user_answer>{answer}</user_answer>
<score>{score}</score>
"""
        }
    ]

    # Generate evaluation using LLM
    knowledge_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    knowledge_data = json.loads(knowledge_json)

    # Parse the response to get the knowledge and unknown
    try:
        knowledge = knowledge_data['knowledge']
        unknown = knowledge_data['unknown']
    except KeyError:
        raise ValueError("Invalid response from LLM. Unable to parse knowledge.")

    return {
        "knowledge": knowledge,
        "unknown": unknown
    }