"""Generate realistic tags for cross-project labeling."""
import uuid
import random
from datetime import datetime
from typing import List, Dict, Tuple


class TagGenerator:
    """Generates realistic organizational tags."""
    
    # Common tag categories and examples
    TAG_CATEGORIES = {
        "Priority": [
            ("urgent", "#FF0000"),
            ("high-priority", "#FF6B00"),
            ("low-priority", "#00AA00"),
        ],
        "Type": [
            ("bug", "#E74C3C"),
            ("feature", "#3498DB"),
            ("enhancement", "#9B59B6"),
            ("documentation", "#95A5A6"),
            ("refactoring", "#34495E"),
        ],
        "Area": [
            ("frontend", "#1ABC9C"),
            ("backend", "#16A085"),
            ("mobile", "#2ECC71"),
            ("api", "#27AE60"),
            ("database", "#F39C12"),
            ("infrastructure", "#E67E22"),
        ],
        "Status": [
            ("needs-review", "#3498DB"),
            ("blocked", "#E74C3C"),
            ("waiting", "#F39C12"),
            ("approved", "#2ECC71"),
        ],
        "Customer": [
            ("customer-request", "#9B59B6"),
            ("support-escalation", "#E74C3C"),
            ("feedback", "#3498DB"),
        ],
        "Release": [
            ("v1.0", "#34495E"),
            ("v2.0", "#2C3E50"),
            ("q1-release", "#16A085"),
            ("q2-release", "#27AE60"),
            ("q3-release", "#2980B9"),
            ("q4-release", "#8E44AD"),
        ],
        "Team": [
            ("cross-team", "#95A5A6"),
            ("engineering", "#3498DB"),
            ("product", "#9B59B6"),
            ("design", "#E91E63"),
        ],
        "Effort": [
            ("quick-win", "#2ECC71"),
            ("complex", "#E74C3C"),
        ],
    }
    
    # Colors for tags (if not specified)
    DEFAULT_COLORS = [
        "#E74C3C", "#3498DB", "#2ECC71", "#F39C12", "#9B59B6",
        "#1ABC9C", "#34495E", "#E67E22", "#95A5A6", "#27AE60",
    ]
    
    def generate_tags_for_org(self, org_id: str, created_at: datetime) -> List[Dict]:
        """Generate a set of organization-wide tags."""
        tags = []
        
        # Select tags from each category
        for category, tag_list in self.TAG_CATEGORIES.items():
            # Not all orgs use all categories
            if random.random() > 0.3:  # 70% include this category
                # Select 1-3 tags from each category
                num_tags = random.randint(1, min(3, len(tag_list)))
                selected = random.sample(tag_list, num_tags)
                
                for tag_name, color in selected:
                    tag = {
                        "tag_id": str(uuid.uuid4()),
                        "org_id": org_id,
                        "name": tag_name,
                        "color": color,
                        "created_at": created_at.isoformat(),
                    }
                    tags.append(tag)
        
        # Add some custom tags
        custom_tag_names = [
            "tech-debt",
            "security",
            "performance",
            "accessibility",
            "analytics",
            "mvp",
            "nice-to-have",
            "breaking-change",
            "dependencies",
        ]
        
        num_custom = random.randint(3, 6)
        for tag_name in random.sample(custom_tag_names, num_custom):
            tag = {
                "tag_id": str(uuid.uuid4()),
                "org_id": org_id,
                "name": tag_name,
                "color": random.choice(self.DEFAULT_COLORS),
                "created_at": created_at.isoformat(),
            }
            tags.append(tag)
        
        return tags
    
    def assign_tags_to_tasks(self, tasks: List[Dict], tags: List[Dict],
                           tag_probability: float,
                           tags_per_task: Tuple[int, int]) -> List[Dict]:
        """Assign tags to tasks based on probability."""
        task_tags = []
        
        for task in tasks:
            # Determine if this task gets tags
            if random.random() < tag_probability:
                # Select number of tags
                num_tags = random.randint(*tags_per_task)
                selected_tags = random.sample(tags, min(num_tags, len(tags)))
                
                for tag in selected_tags:
                    task_tag = {
                        "task_id": task["task_id"],
                        "tag_id": tag["tag_id"],
                        "created_at": task["created_at"],
                    }
                    task_tags.append(task_tag)
        
        return task_tags