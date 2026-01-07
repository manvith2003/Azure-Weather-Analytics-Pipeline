"""Generate realistic comments on tasks."""
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CommentGenerator:
    """Generates realistic task comments and activity."""
    
    # Comment templates for different types
    COMMENT_TEMPLATES = {
        "update": [
            "Working on this now.",
            "Making good progress. Should be done by EOD.",
            "About 50% complete. Will update tomorrow.",
            "Started work on this. Running into some issues with {issue}.",
            "This is ready for review.",
            "Completed the initial implementation. Needs testing.",
            "Running final tests before marking as complete.",
        ],
        "question": [
            "Can someone clarify the requirements here?",
            "What's the priority on this?",
            "Do we have the designs for this yet?",
            "Should this be done before the other task?",
            "Who should review this?",
            "Is this blocked by anything?",
            "What's the expected timeline?",
        ],
        "blocker": [
            "Blocked by {dependency}.",
            "Need access to {resource} to proceed.",
            "Waiting on {person} for clarification.",
            "Can't proceed until {blocker} is resolved.",
            "Found a critical bug that needs to be fixed first.",
            "Needs approval from {stakeholder} before moving forward.",
        ],
        "review": [
            "LGTM! Approved.",
            "Left some comments on the implementation.",
            "Looks good overall. Minor suggestions in the code.",
            "Approved with minor changes requested.",
            "Please address the feedback and resubmit.",
            "This looks great! Shipping it.",
        ],
    }
    
    def __init__(self, llm_generator=None):
        self.llm = llm_generator
    
    def _select_comment_type(self, task: Dict) -> str:
        """Select comment type based on task state."""
        if task["completed"]:
            # Completed tasks more likely to have review comments
            return random.choices(
                ["update", "question", "blocker", "review"],
                weights=[0.3, 0.1, 0.1, 0.5]
            )[0]
        else:
            # In-progress tasks have more updates and questions
            return random.choices(
                ["update", "question", "blocker", "review"],
                weights=[0.5, 0.3, 0.15, 0.05]
            )[0]
    
    def _generate_simple_comment(self, comment_type: str) -> str:
        """Generate a simple comment from templates."""
        templates = self.COMMENT_TEMPLATES.get(comment_type, ["Comment"])
        template = random.choice(templates)
        
        # Fill in placeholders
        replacements = {
            "issue": random.choice(["dependencies", "API changes", "unclear requirements", "test failures"]),
            "dependency": random.choice(["another task", "external API", "infrastructure setup", "design review"]),
            "resource": random.choice(["production database", "staging environment", "API credentials", "test data"]),
            "person": random.choice(["the PM", "the team lead", "stakeholders", "the client"]),
            "blocker": random.choice(["the previous task", "a backend issue", "missing credentials", "design approval"]),
            "stakeholder": random.choice(["product", "engineering lead", "legal", "security team"]),
        }
        
        for key, value in replacements.items():
            template = template.replace(f"{{{key}}}", value)
        
        return template
    
    def _select_commenter(self, task: Dict, team_members: List[Dict]) -> Optional[Dict]:
        """Select who makes the comment."""
        # 60% chance assignee comments, 40% chance other team member
        if task["assignee_id"] and random.random() < 0.6:
            commenter = next((u for u in team_members if u["user_id"] == task["assignee_id"]), None)
            if commenter:
                return commenter
        
        # Otherwise, random team member
        return random.choice(team_members) if team_members else None
    
    def _generate_comment_time(self, task: Dict, is_first: bool) -> datetime:
        """Generate realistic comment timestamp."""
        task_created = datetime.fromisoformat(task["created_at"])
        
        if task["completed"]:
            task_completed = datetime.fromisoformat(task["completed_at"])
            # Comments spread between creation and completion
            if is_first:
                # First comment soon after creation
                hours_after = random.randint(1, 24)
                return task_created + timedelta(hours=hours_after)
            else:
                # Later comments spread throughout
                total_seconds = int((task_completed - task_created).total_seconds())
                # Ensure positive duration
                if total_seconds > 0:
                    return task_created + timedelta(seconds=random.randint(0, total_seconds))
                else:
                    # If task completed same time as created, add a few hours
                    return task_created + timedelta(hours=random.randint(1, 12))
        else:
            # For incomplete tasks, comments up to now
            now = datetime.now()
            max_seconds = int((now - task_created).total_seconds())
            
            if is_first:
                hours_after = random.randint(1, 48)
                comment_time = task_created + timedelta(hours=hours_after)
            else:
                comment_time = task_created + timedelta(seconds=random.randint(0, max_seconds))
            
            # Keep in work hours
            comment_time = comment_time.replace(
                hour=random.randint(9, 17),
                minute=random.randint(0, 59),
                second=0,
                microsecond=0
            )
            
            return comment_time
    
    def generate_comment(self, task: Dict, team_members: List[Dict], 
                        is_first: bool = False) -> Optional[Dict]:
        """Generate a single comment."""
        commenter = self._select_commenter(task, team_members)
        if not commenter:
            return None
        
        comment_type = self._select_comment_type(task)
        
        # Generate comment text
        if self.llm and random.random() > 0.7:  # 30% use LLM
            try:
                text = self.llm.generate_comment(
                    task["name"],
                    commenter["role"],
                    comment_type
                )
            except Exception as e:
                logger.warning(f"LLM comment generation failed: {e}")
                text = self._generate_simple_comment(comment_type)
        else:
            text = self._generate_simple_comment(comment_type)
        
        comment_time = self._generate_comment_time(task, is_first)
        
        return {
            "comment_id": str(uuid.uuid4()),
            "task_id": task["task_id"],
            "user_id": commenter["user_id"],
            "text": text,
            "created_at": comment_time.isoformat(),
        }
    
    def generate_comments_for_task(self, task: Dict, team_members: List[Dict],
                                   num_comments: int) -> List[Dict]:
        """Generate multiple comments for a task."""
        comments = []
        
        for i in range(num_comments):
            comment = self.generate_comment(task, team_members, is_first=(i == 0))
            if comment:
                comments.append(comment)
        
        # Sort by timestamp
        comments.sort(key=lambda c: c["created_at"])
        
        return comments