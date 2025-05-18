import json
from course_generation.models import Question, Exercise, UserKnowledge
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
        # print(f"LLM Explanation: {explanation}")
        pass
    
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

def update_user_knowledge(user_knowledge):
    """
    Update the user's knowledge list after adding new knowledge & unknown.
    
    Args:
        user_knowledge (UserKnowledge): The user's knowledge, has the knowledge_list and unknown_list.
    
    Returns:
        None
    """

    knowledge_list = user_knowledge.knowledge_list
    unknown_list = user_knowledge.unknown_list

    # do it manually first to reduce amount of LLM input
    # remove duplicates
    knowledge_list = list(set(knowledge_list))
    unknown_list = list(set(unknown_list))
    # remove empty strings
    knowledge_list = [k for k in knowledge_list if k]
    unknown_list = [u for u in unknown_list if u]
    # remove unknown that is already in knowledge
    unknown_list = [u for u in unknown_list if u not in knowledge_list]

    # now do it with LLM
    # initialize LLM caller
    llm_caller = LLMCaller()

    # Turn the lists into strings
    knowledge_list_str = ', '.join(knowledge_list)
    unknown_list_str = ', '.join(unknown_list)

    # Prepare the prompt for the LLM
    system_prompt = """
<role>
You are an expert evaluator.
Your job is to simplify the user's knowledge list and unknown list.
</role>

You will be given the following as input:
<input>
- The user's knowledge list, inside the <knowledge_list> tags
- The user's unknown list, inside the <unknown_list> tags
</input>

Return the response in the following JSON format:
{
    "knowledge_list": [
        "a short string of what the user knows"
    ],
    "unknown_list": [
        "a short string of what the user doesn't know"
    ]
}

Here are the criteria to determine the knowledge and unknown:
<criteria>
- neither list should have duplicates or empty strings
- if something is in both lists, it should be removed from the unknown list
- if any items in the knowledge list are too similar, they should be merged into one
- if any items in the unknown list are too similar, they should be merged into one
</criteria>
"""

    messages = [
        {
            "role": "user", "content": f"""
<knowledge_list>{knowledge_list_str}</knowledge_list>
<unknown_list>{unknown_list_str}</unknown_list>
"""
        }
    ]

    # Generate evaluation using LLM
    knowledge_json = llm_caller.generate_response(messages, system_prompt)[7:-3]
    knowledge_data = json.loads(knowledge_json)

    # Parse the response to get the knowledge and unknown
    try:
        knowledge_list = knowledge_data['knowledge_list']
        unknown_list = knowledge_data['unknown_list']
    except KeyError:
        raise ValueError("Invalid response from LLM. Unable to parse knowledge.")

    # update the user_knowledge object
    user_knowledge.knowledge_list = knowledge_list
    user_knowledge.unknown_list = unknown_list
    user_knowledge.save()