"""Configuration management for Asana simulation."""
import os
from datetime import datetime, date
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class Config:
    """Central configuration for the simulation."""
    
    # Organization size
    org_size: int = int(os.getenv("ORG_SIZE", "7500"))
    num_teams: int = int(os.getenv("NUM_TEAMS", "50"))
    project_count: int = int(os.getenv("PROJECT_COUNT", "300"))
    
    # Task generation multiplier (tasks per project on average)
    task_multiplier: int = int(os.getenv("TASK_MULTIPLIER", "15"))
    
    # Date range for historical data
    start_date: date = datetime.strptime(
        os.getenv("START_DATE", "2024-07-01"), "%Y-%m-%d"
    ).date()
    end_date: date = datetime.strptime(
        os.getenv("END_DATE", "2026-01-06"), "%Y-%m-%d"
    ).date()
    
    # Database
    db_path: str = os.getenv("DB_PATH", "output/asana_simulation.sqlite")
    schema_path: str = os.getenv("SCHEMA_PATH", "schema.sql")
    
    # API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Team size distributions (based on research)
    team_size_distribution = {
        "small": (3, 8, 0.3),      # (min, max, probability)
        "medium": (9, 15, 0.5),
        "large": (16, 30, 0.2)
    }
    
    # Department distribution for B2B SaaS
    department_distribution = {
        "Engineering": 0.35,
        "Sales": 0.20,
        "Marketing": 0.12,
        "Customer Success": 0.10,
        "Product": 0.08,
        "Design": 0.05,
        "Operations": 0.05,
        "Finance": 0.03,
        "HR": 0.02
    }
    
    # Project type distributions
    project_types = {
        "Sprint": 0.30,
        "Bug Tracking": 0.15,
        "Feature Development": 0.20,
        "Marketing Campaign": 0.10,
        "Ongoing": 0.15,
        "Research": 0.05,
        "Customer Onboarding": 0.05
    }
    
    # Task completion rates by project type (from Asana benchmarks)
    completion_rates = {
        "Sprint": (0.70, 0.85),              # (min, max)
        "Bug Tracking": (0.60, 0.70),
        "Feature Development": (0.65, 0.80),
        "Marketing Campaign": (0.75, 0.90),
        "Ongoing": (0.40, 0.50),
        "Research": (0.50, 0.65),
        "Customer Onboarding": (0.80, 0.95)
    }
    
    # Task description length distribution
    description_lengths = {
        "empty": 0.20,
        "short": 0.50,
        "medium": 0.20,
        "detailed": 0.10
    }
    
    # Subtask probability (20% of tasks have subtasks)
    subtask_probability: float = 0.20
    subtasks_per_task: tuple = (2, 5)  # min, max
    
    # Comment distribution
    comment_probability: float = 0.60  # 60% of tasks have comments
    comments_per_task: tuple = (1, 8)  # min, max
    
    # Tag usage
    tags_per_task_probability: float = 0.40
    tags_per_task: tuple = (1, 3)
    
    # Custom fields per project
    custom_fields_per_project: tuple = (2, 5)
    
    # Attachment probability
    attachment_probability: float = 0.25
    attachments_per_task: tuple = (1, 3)
    
    def __post_init__(self):
        """Validate configuration."""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment")
        
        if self.start_date >= self.end_date:
            raise ValueError("START_DATE must be before END_DATE")


# Global config instance
config = Config()