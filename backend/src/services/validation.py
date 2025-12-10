from typing import Dict, Any, List
from datetime import datetime
import re

def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate user data and return any errors found
    """
    errors = []
    
    # Validate email
    if not user_data.get('email'):
        errors.append("Email is required")
    elif not validate_email(user_data['email']):
        errors.append("Email format is invalid")
    
    # Validate password
    if not user_data.get('password_hash'):
        errors.append("Password is required")
    elif len(user_data['password_hash']) < 8:
        errors.append("Password must be at least 8 characters long")
    
    # Validate role
    valid_roles = ["student", "developer", "educator", "admin"]
    if user_data.get('role') and user_data['role'] not in valid_roles:
        errors.append(f"Role must be one of: {', '.join(valid_roles)}")
    
    # Validate background
    valid_backgrounds = ["beginner", "intermediate", "advanced"]
    if user_data.get('background') and user_data['background'] not in valid_backgrounds:
        errors.append(f"Background must be one of: {', '.join(valid_backgrounds)}")
    
    return {"errors": errors}

def validate_book_module_data(module_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate book module data and return any errors found
    """
    errors = []
    
    # Validate required fields
    if not module_data.get('id'):
        errors.append("Module ID is required")
    
    if not module_data.get('title'):
        errors.append("Module title is required")
    elif len(module_data['title']) < 5 or len(module_data['title']) > 100:
        errors.append("Module title must be between 5 and 100 characters")
    
    if 'order' not in module_data:
        errors.append("Module order is required")
    elif not (1 <= module_data['order'] <= 4):
        errors.append("Module order must be between 1 and 4")
    
    if 'learning_objectives' not in module_data or not module_data['learning_objectives']:
        errors.append("Learning objectives must be present and not empty")
    
    if 'checklist' not in module_data or not module_data['checklist']:
        errors.append("Checklist must be present and not empty")
    
    if 'word_count' not in module_data:
        errors.append("Word count is required")
    elif not (2000 <= module_data['word_count'] <= 3750):
        errors.append("Word count must be between 2000 and 3750")
    
    return {"errors": errors}

def validate_chapter_data(chapter_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate chapter data and return any errors found
    """
    errors = []
    
    # Validate required fields
    if not chapter_data.get('id'):
        errors.append("Chapter ID is required")
    
    if not chapter_data.get('module_id'):
        errors.append("Module ID is required")
    
    if not chapter_data.get('title'):
        errors.append("Chapter title is required")
    
    if not chapter_data.get('content'):
        errors.append("Chapter content is required")
    
    if 'order' not in chapter_data:
        errors.append("Chapter order is required")
    elif chapter_data['order'] <= 0:
        errors.append("Chapter order must be positive")
    
    if 'learning_objectives' not in chapter_data:
        errors.append("Learning objectives are required")
    
    if 'summary' not in chapter_data:
        errors.append("Summary is required")
    
    if 'checklist' not in chapter_data:
        errors.append("Checklist is required")
    
    return {"errors": errors}

def validate_question_data(question_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate question data and return any errors found
    """
    errors = []
    
    # Validate required fields
    if not question_data.get('id'):
        errors.append("Question ID is required")
    
    if not question_data.get('question_text'):
        errors.append("Question text is required")
    elif len(question_data['question_text']) < 5 or len(question_data['question_text']) > 1000:
        errors.append("Question text must be between 5 and 1000 characters")
    
    # Validate question type
    valid_types = ["general", "selected_text"]
    if question_data.get('question_type') not in valid_types:
        errors.append(f"Question type must be one of: {', '.join(valid_types)}")
    
    # Check if selected_text is provided when required
    if question_data.get('question_type') == "selected_text" and not question_data.get('selected_text'):
        errors.append("Selected text is required for selected_text type questions")
    
    return {"errors": errors}

def validate_answer_data(answer_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate answer data and return any errors found
    """
    errors = []
    
    # Validate required fields
    if not answer_data.get('id'):
        errors.append("Answer ID is required")
    
    if not answer_data.get('question_id'):
        errors.append("Question ID is required")
    
    if not answer_data.get('answer_text'):
        errors.append("Answer text is required")
    
    if 'confidence_score' not in answer_data:
        errors.append("Confidence score is required")
    elif not (0.0 <= answer_data['confidence_score'] <= 1.0):
        errors.append("Confidence score must be between 0.0 and 1.0")
    
    if 'source_chunks' not in answer_data:
        errors.append("Source chunks are required")
    
    return {"errors": errors}

def validate_code_example_data(code_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate code example data and return any errors found
    """
    errors = []
    
    # Validate required fields
    if not code_data.get('id'):
        errors.append("Code example ID is required")
    
    if not code_data.get('chapter_id'):
        errors.append("Chapter ID is required")
    
    if not code_data.get('title'):
        errors.append("Title is required")
    
    if not code_data.get('code'):
        errors.append("Code content is required")
    
    return {"errors": errors}

def validate_exercise_data(exercise_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate exercise data and return any errors found
    """
    errors = []
    
    # Validate required fields
    if not exercise_data.get('id'):
        errors.append("Exercise ID is required")
    
    if not exercise_data.get('chapter_id'):
        errors.append("Chapter ID is required")
    
    if not exercise_data.get('title'):
        errors.append("Title is required")
    
    if not exercise_data.get('description'):
        errors.append("Description is required")
    
    if not exercise_data.get('instructions'):
        errors.append("Instructions are required")
    
    # Validate difficulty
    valid_difficulties = ["beginner", "intermediate", "advanced"]
    if exercise_data.get('difficulty') not in valid_difficulties:
        errors.append(f"Difficulty must be one of: {', '.join(valid_difficulties)}")
    
    return {"errors": errors}