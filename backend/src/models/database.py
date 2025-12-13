from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean # type: ignore
from sqlalchemy.types import Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import os

Base = declarative_base()

class BookModuleDB(Base):
    __tablename__ = 'book_modules'
    
    id = Column(String, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)  # 1-4 for the 4 modules
    learning_objectives = Column(Text)  # JSON string
    summary = Column(Text)
    checklist = Column(Text)  # JSON string
    word_count = Column(Integer)  # 2000-3750 for each module
    
    # Relationship
    chapters = relationship("ChapterDB", back_populates="module")

class ChapterDB(Base):
    __tablename__ = 'chapters'
    
    id = Column(String, primary_key=True)
    module_id = Column(String, ForeignKey('book_modules.id'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text)
    order = Column(Integer, nullable=False)  # sequence number within module
    learning_objectives = Column(Text)  # JSON string
    summary = Column(Text)
    checklist = Column(Text)  # JSON string
    word_count = Column(Integer)
    
    # Relationships
    module = relationship("BookModuleDB", back_populates="chapters")
    code_examples = relationship("CodeExampleDB", back_populates="chapter")
    exercises = relationship("ExerciseDB", back_populates="chapter")

class UserDB(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(50), unique=True)
    password_hash = Column(String, nullable=False)  # This would typically be a hashed password
    role = Column(String(20))  # student, developer, educator, admin
    background = Column(String(20))  # beginner, intermediate, advanced
    hardware_level = Column(String(30))  # simulator-only, basic-hardware, advanced-hardware
    preferred_language = Column(String(5), default="en")  # Also supports "ur" for Urdu
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    questions = relationship("QuestionDB", back_populates="user")
    personalization_settings = relationship("PersonalizationSettingsDB", back_populates="user")
    chat_logs = relationship("ChatLogDB", back_populates="user")

class QuestionDB(Base):
    __tablename__ = 'questions'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))  # Optional for anonymous questions
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)  # general, selected_text
    selected_text = Column(Text)  # Required if question type is "selected_text"
    book_section_id = Column(String)  # To track which section user was reading
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("UserDB", back_populates="questions")
    answer = relationship("AnswerDB", back_populates="question", uselist=False)

class AnswerDB(Base):
    __tablename__ = 'answers'
    
    id = Column(String, primary_key=True)
    question_id = Column(String, ForeignKey('questions.id'), nullable=False)
    answer_text = Column(Text, nullable=False)
    source_chunks = Column(Text)  # JSON string of IDs of content chunks used
    confidence_score = Column(Float)  # 0.0-1.0
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    question = relationship("QuestionDB", back_populates="answer")

class CodeExampleDB(Base):
    __tablename__ = 'code_examples'
    
    id = Column(String, primary_key=True)
    chapter_id = Column(String, ForeignKey('chapters.id'), nullable=False)
    title = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(50))  # e.g., "python", "bash", "yaml", "xml"
    version_requirements = Column(String)  # e.g., "ROS 2 Humble", "Python 3.8+"
    execution_notes = Column(Text)
    expected_output = Column(Text)
    
    # Relationships
    chapter = relationship("ChapterDB", back_populates="code_examples")

class ExerciseDB(Base):
    __tablename__ = 'exercises'
    
    id = Column(String, primary_key=True)
    chapter_id = Column(String, ForeignKey('chapters.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20))  # beginner, intermediate, advanced
    instructions = Column(Text, nullable=False)
    solution = Column(Text)
    hints = Column(Text)  # JSON string
    
    # Relationships
    chapter = relationship("ChapterDB", back_populates="exercises")

class ChatLogDB(Base):
    __tablename__ = 'chat_logs'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))  # Optional for anonymous
    question_id = Column(String, ForeignKey('questions.id'), nullable=False)
    answer_id = Column(String, ForeignKey('answers.id'), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    session_id = Column(String)  # To group related questions
    
    # Relationships
    user = relationship("UserDB", back_populates="chat_logs")
    question = relationship("QuestionDB")
    answer = relationship("AnswerDB")

class PersonalizationSettingsDB(Base):
    __tablename__ = 'personalization_settings'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    preferred_hardware_examples = Column(String(20))  # simulator, real_hardware, both
    experience_level = Column(String(20))  # beginner, intermediate, advanced
    favorite_topics = Column(Text)  # JSON string
    learning_pace = Column(String(10))  # slow, normal, fast
    notification_preferences = Column(Text)  # JSON string (email, push, etc.)
    
    # Relationships
    user = relationship("UserDB", back_populates="personalization_settings")

class ImageMediaDB(Base):
    __tablename__ = 'image_media'
    
    id = Column(String, primary_key=True)
    chapter_id = Column(String, ForeignKey('chapters.id'), nullable=False)
    filename = Column(String, nullable=False)
    title = Column(String, nullable=False)
    alt_text = Column(String)
    attribution = Column(String, nullable=False)  # Source information
    license = Column(String, nullable=False)  # e.g., "CC BY", "AI-generated", etc.
    usage_notes = Column(Text)  # Where and how the image should be used

# Function to create the database engine
def get_db_engine():
    database_url = os.getenv("DATABASE_URL", "sqlite:///./physical_ai_book.db")
    return create_engine(database_url)

# Function to create all tables
def create_tables():
    engine = get_db_engine()
    Base.metadata.create_all(engine)