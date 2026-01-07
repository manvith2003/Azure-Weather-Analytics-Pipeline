"""Generate realistic tasks with proper distributions."""
import uuid
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.date_helpers import (
    generate_due_date, 
    generate_completion_time,
    sprint_boundary_date,
    workday_bias_datetime
)
from utils.llm import LLMGenerator

logger = logging.getLogger(__name__)


class TaskGenerator:
    """Generates realistic tasks with proper distributions."""
    
    def __init__(self, llm_generator: Optional[LLMGenerator] = None):
        self.llm = llm_generator
        self.priorities = ["High", "Medium", "Low", None]
        self.priority_weights = [0.15, 0.40, 0.25, 0.20]  # 20% no priority
    
    def _select_assignee(self, team_members: List[Dict], 
                        existing_tasks: List[Dict]) -> Optional[str]:
        """
        Select task assignee with realistic workload distribution.
        15% unassigned, rest distributed by seniority.
        """
        # 15% unassigned
        if random.random() < 0.15:
            return None
        
        if not team_members:
            return None
        
        # Calculate current workload
        workload = {member["user_id"]: 0 for member in team_members}
        for task in existing_tasks:
            if task["assignee_id"] in workload:
                workload[task["assignee_id"]] += 1
        
        # Weight by inverse workload and seniority
        weights = []
        for member in team_members:
            base_weight = 1.0
            
            # Senior members get slightly more tasks
            if any(title in member["role"].lower() 
                   for title in ["senior", "staff", "principal"]):
                base_weight *= 1.3
            elif any(title in member["role"].lower()
                    for title in ["manager", "director", "vp"]):
                base_weight *= 0.7  # Managers get fewer individual tasks
            
            # Reduce weight based on current workload
            current_load = workload[member["user_id"]]
            workload_penalty = 1.0 / (1.0 + current_load * 0.1)
            
            weights.append(base_weight * workload_penalty)
        
        selected = random.choices(team_members, weights=weights)[0]
        return selected["user_id"]
    
    def _generate_task_name(self, project: Dict, section_name: str,
                           team_members: List[Dict]) -> str:
        """Generate realistic task name."""
        if not self.llm:
            return self._generate_simple_task_name(project, section_name)
        
        try:
            team_type = team_members[0]["department"] if team_members else "General"
            context = f"Section: {section_name}"
            
            name = self.llm.generate_task_name(
                project["project_type"],
                project["name"],
                team_type,
                context
            )
            
            return name if name else self._generate_simple_task_name(project, section_name)
            
        except Exception as e:
            logger.warning(f"LLM task name generation failed: {e}")
            return self._generate_simple_task_name(project, section_name)
    
    def _generate_simple_task_name(self, project: Dict, section_name: str) -> str:
        """Fallback task name generation."""
        verbs = ["Implement", "Fix", "Update", "Review", "Test", "Deploy", 
                "Design", "Create", "Refactor", "Optimize"]
        objects = ["feature", "bug", "API", "UI", "database", "endpoint",
                  "component", "module", "integration", "documentation"]
        
        return f"{random.choice(verbs)} {random.choice(objects)}"
    
    def _generate_description(self, task_name: str, project: Dict,
                            length: str) -> str:
        """Generate task description."""
        if length == "empty":
            return ""
        
        if not self.llm:
            return self._generate_simple_description(length)
        
        try:
            return self.llm.generate_task_description(
                task_name,
                project["project_type"],
                length
            )
        except Exception as e:
            logger.warning(f"LLM description generation failed: {e}")
            return self._generate_simple_description(length)
    
    def _generate_simple_description(self, length: str) -> str:
        """Fallback description generation."""
        if length == "empty":
            return ""
        elif length == "short":
            return "Task description needed."
        elif length == "medium":
            return "Task description with details. This needs to be completed as part of the current sprint."
        else:
            return """Detailed task description.

Requirements:
- Requirement 1
- Requirement 2
- Requirement 3

Acceptance Criteria:
- Criteria 1
- Criteria 2"""
    
    def _determine_completion(self, project: Dict, created_at: datetime,
                            due_date: Optional[datetime], now: datetime) -> bool:
        """Determine if task should be completed based on project type and age."""
        # Get completion rate range for project type
        completion_ranges = {
            "Sprint": (0.70, 0.85),
            "Bug Tracking": (0.60, 0.70),
            "Feature Development": (0.65, 0.80),
            "Marketing Campaign": (0.75, 0.90),
            "Ongoing": (0.40, 0.50),
            "Research": (0.50, 0.65),
            "Customer Onboarding": (0.80, 0.95),
        }
        
        min_rate, max_rate = completion_ranges.get(
            project["project_type"],
            (0.50, 0.70)
        )
        
        completion_rate = random.uniform(min_rate, max_rate)
        
        # Older tasks more likely to be completed
        age_days = (now - created_at).days
        age_factor = min(age_days / 30.0, 1.0)  # Cap at 30 days
        
        adjusted_rate = completion_rate * (0.5 + 0.5 * age_factor)
        
        return random.random() < adjusted_rate
    
    def generate_task(self, project: Dict, section: Dict,
                     team_members: List[Dict], created_by: Dict,
                     existing_tasks: List[Dict],
                     start_date: datetime, end_date: datetime,
                     now: datetime) -> Dict:
        """Generate a single realistic task."""
        task_id = str(uuid.uuid4())
        
        # Generate creation time
        project_created = datetime.fromisoformat(project["created_at"])
        created_at = workday_bias_datetime(project_created, end_date)
        
        # Generate task name
        task_name = self._generate_task_name(project, section["name"], team_members)
        
        # Select description length
        length_options = ["empty", "short", "medium", "detailed"]
        length_weights = [0.20, 0.50, 0.20, 0.10]
        length = random.choices(length_options, weights=length_weights)[0]
        
        # Generate description
        description = self._generate_description(task_name, project, length)
        
        # Assign task
        assignee_id = self._select_assignee(team_members, existing_tasks)
        
        # Generate due date
        due_date = generate_due_date(created_at, end_date.date())
        
        # Sprint projects: align some tasks to sprint boundaries
        if project["project_type"] == "Sprint" and due_date and random.random() > 0.5:
            due_date = sprint_boundary_date(due_date, sprint_length_weeks=2)
        
        # Determine priority
        priority = random.choices(self.priorities, weights=self.priority_weights)[0]
        
        # Determine completion
        completed = self._determine_completion(project, created_at, due_date, now)
        completed_at = None
        
        if completed:
            completed_at = generate_completion_time(created_at, now)
            if not completed_at:
                completed = False
        
        task = {
            "task_id": task_id,
            "project_id": project["project_id"],
            "section_id": section["section_id"],
            "parent_task_id": None,  # Top-level task
            "name": task_name,
            "description": description,
            "assignee_id": assignee_id,
            "created_by": created_by["user_id"],
            "created_at": created_at.isoformat(),
            "due_date": due_date.isoformat() if due_date else None,
            "start_date": None,  # Could add start dates for some tasks
            "completed": 1 if completed else 0,
            "completed_at": completed_at.isoformat() if completed_at else None,
            "priority": priority,
        }
        
        return task
    
    def generate_subtasks(self, parent_task: Dict, team_members: List[Dict],
                         num_subtasks: int, now: datetime) -> List[Dict]:
        """Generate subtasks for a parent task."""
        subtasks = []
        parent_created = datetime.fromisoformat(parent_task["created_at"])
        
        subtask_names = [
            "Subtask: {action}".format(action=action)
            for action in [
                "Implementation", "Testing", "Documentation",
                "Code review", "QA verification", "Deployment"
            ]
        ]
        
        for i in range(num_subtasks):
            subtask_id = str(uuid.uuid4())
            
            # Subtasks created shortly after parent
            created_at = parent_created + timedelta(hours=random.randint(1, 48))
            
            # Subtasks often inherit parent assignee or go to same team
            if random.random() > 0.3 and parent_task["assignee_id"]:
                assignee_id = parent_task["assignee_id"]
            else:
                assignee_id = self._select_assignee(team_members, [])
            
            # Most subtasks have no description
            description = "" if random.random() > 0.3 else "Subtask details"
            
            # Subtasks inherit parent due date or are slightly earlier
            due_date = None
            if parent_task["due_date"]:
                parent_due = datetime.fromisoformat(parent_task["due_date"])
                days_before = random.randint(0, 3)
                due_date = (parent_due - timedelta(days=days_before)).date()
            
            # Subtask completion based on parent
            completed = parent_task["completed"]
            completed_at = None
            if completed:
                parent_completed = datetime.fromisoformat(parent_task["completed_at"])
                # Subtasks complete before or with parent
                completed_at = parent_completed - timedelta(hours=random.randint(0, 24))
            
            subtask = {
                "task_id": subtask_id,
                "project_id": parent_task["project_id"],
                "section_id": parent_task["section_id"],
                "parent_task_id": parent_task["task_id"],
                "name": random.choice(subtask_names) if i < len(subtask_names) else f"Subtask {i+1}",
                "description": description,
                "assignee_id": assignee_id,
                "created_by": parent_task["created_by"],
                "created_at": created_at.isoformat(),
                "due_date": due_date.isoformat() if due_date else None,
                "start_date": None,
                "completed": completed,
                "completed_at": completed_at.isoformat() if completed_at else None,
                "priority": parent_task["priority"],
            }
            
            subtasks.append(subtask)
        
        return subtasks
    
    def generate_tasks_for_project(self, project: Dict, sections: List[Dict],
                                   team_members: List[Dict],
                                   num_tasks: int,
                                   start_date: datetime, end_date: datetime,
                                   now: datetime,
                                   subtask_probability: float = 0.20) -> List[Dict]:
        """Generate all tasks for a project."""
        all_tasks = []
        
        # Distribute tasks across sections (bias toward early sections)
        section_weights = [1.0 / (i + 1) for i in range(len(sections))]
        section_weights = [w / sum(section_weights) for w in section_weights]
        
        for _ in range(num_tasks):
            section = random.choices(sections, weights=section_weights)[0]
            
            # Select random team member as creator
            created_by = random.choice(team_members) if team_members else None
            if not created_by:
                continue
            
            task = self.generate_task(
                project, section, team_members, created_by,
                all_tasks, start_date, end_date, now
            )
            
            all_tasks.append(task)
            
            # Generate subtasks?
            if random.random() < subtask_probability:
                num_subtasks = random.randint(2, 5)
                subtasks = self.generate_subtasks(task, team_members, num_subtasks, now)
                all_tasks.extend(subtasks)
        
        logger.info(f"Generated {len(all_tasks)} tasks for project '{project['name']}'")
        
        return all_tasks


from datetime import timedelta