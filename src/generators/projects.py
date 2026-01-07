"""Generate realistic projects and sections."""
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.date_helpers import random_datetime_between, workday_datetime
from utils.llm import LLMGenerator

logger = logging.getLogger(__name__)


class ProjectGenerator:
    """Generates realistic projects with proper structure."""
    
    # Project name patterns by type and department
    PROJECT_PATTERNS = {
        "Engineering": {
            "Sprint": [
                "Q{q} Sprint {n}",
                "{year} H{h} Sprint {n}",
                "Sprint {n} - {focus}",
            ],
            "Feature Development": [
                "{feature} Development",
                "Build {feature}",
                "{feature} Implementation",
            ],
            "Bug Tracking": [
                "Bug Tracking - {area}",
                "{area} Issues & Bugs",
                "Bug Fixes - {area}",
            ],
            "Ongoing": [
                "{area} Maintenance",
                "Tech Debt - {area}",
                "{area} Infrastructure",
            ],
        },
        "Product": {
            "Feature Development": [
                "{feature} Launch",
                "{feature} Product Development",
            ],
            "Research": [
                "User Research - {topic}",
                "{topic} Discovery",
            ],
        },
        "Marketing": {
            "Marketing Campaign": [
                "Q{q} {year} Campaign",
                "{campaign_name} Campaign",
                "{event} Marketing",
            ],
            "Ongoing": [
                "Content Calendar {year}",
                "Social Media - Q{q}",
            ],
        },
        "Sales": {
            "Ongoing": [
                "Q{q} {year} Sales Pipeline",
                "{segment} Sales",
            ],
        },
        "Customer Success": {
            "Customer Onboarding": [
                "{client} Onboarding",
                "Enterprise Onboarding - {month}",
            ],
            "Ongoing": [
                "Customer Health Monitoring",
                "Renewal Management Q{q}",
            ],
        },
    }
    
    # Section patterns by project type
    SECTION_PATTERNS = {
        "Sprint": ["Backlog", "To Do", "In Progress", "In Review", "Done"],
        "Bug Tracking": ["New", "Triaged", "In Progress", "Ready for QA", "Closed"],
        "Feature Development": ["Planning", "Design", "Development", "Testing", "Launch"],
        "Marketing Campaign": ["Planning", "Content Creation", "Review", "Scheduled", "Published"],
        "Customer Onboarding": ["Kickoff", "Setup", "Training", "Go Live", "Complete"],
        "Ongoing": ["To Do", "In Progress", "Done"],
        "Research": ["Questions", "In Progress", "Findings", "Recommendations"],
    }
    
    def __init__(self, llm_generator: Optional[LLMGenerator] = None):
        self.llm = llm_generator
        self.features = [
            "API Gateway", "User Dashboard", "Analytics Platform", "Mobile App",
            "Payment System", "Notification Service", "Search Functionality",
            "Admin Panel", "Reporting Engine", "Integration Hub", "AI Assistant",
            "Collaboration Tools", "Security Features", "Performance Optimization"
        ]
        self.areas = [
            "Frontend", "Backend", "API", "Database", "Infrastructure",
            "Mobile", "Security", "Performance", "Testing"
        ]
        self.campaigns = [
            "Product Launch", "Lead Generation", "Brand Awareness",
            "Webinar Series", "Content Marketing", "Conference"
        ]
    
    def _generate_project_name(self, team_name: str, project_type: str,
                              department: str, created_at: datetime) -> str:
        """Generate a realistic project name."""
        year = created_at.year
        quarter = (created_at.month - 1) // 3 + 1
        half = 1 if created_at.month <= 6 else 2
        month = created_at.strftime("%B")
        
        # Get patterns for this department and type
        dept_patterns = self.PROJECT_PATTERNS.get(department, {})
        type_patterns = dept_patterns.get(project_type, [f"{team_name} - {project_type}"])
        
        pattern = random.choice(type_patterns)
        
        # Fill in template variables
        name = pattern.format(
            q=quarter,
            year=year,
            h=half,
            n=random.randint(1, 20),
            focus=random.choice(["Performance", "Features", "Bugs", "Refactor"]),
            feature=random.choice(self.features),
            area=random.choice(self.areas),
            campaign_name=random.choice(self.campaigns),
            event=random.choice(["AWS Summit", "SaaStr", "Product Launch"]),
            topic=random.choice(["Onboarding", "Pricing", "Feature Usage"]),
            segment=random.choice(["Enterprise", "Mid-Market", "SMB"]),
            client=f"Client {random.randint(1, 100)}",
            month=month,
        )
        
        return name
    
    def _generate_sections(self, project_id: str, project_type: str,
                          created_at: datetime) -> List[Dict]:
        """Generate sections for a project."""
        section_names = self.SECTION_PATTERNS.get(
            project_type,
            ["To Do", "In Progress", "Done"]
        )
        
        sections = []
        for i, name in enumerate(section_names):
            section = {
                "section_id": str(uuid.uuid4()),
                "project_id": project_id,
                "name": name,
                "position": i,
                "created_at": created_at.isoformat(),
            }
            sections.append(section)
        
        return sections
    
    def generate_project(self, team: Dict, team_members: List[Dict],
                        project_type: str, created_at: datetime,
                        end_date: datetime) -> tuple[Dict, List[Dict]]:
        """Generate a single project with sections."""
        project_id = str(uuid.uuid4())
        
        # Extract department from team context
        department = team_members[0]["department"] if team_members else "General"
        
        # Generate project name
        project_name = self._generate_project_name(
            team["name"], project_type, department, created_at
        )
        
        # Generate description using LLM if available
        description = ""
        if self.llm and random.random() > 0.3:  # 70% have descriptions
            try:
                description = self.llm.generate_project_description(
                    project_name, project_type, team["name"]
                )
            except Exception as e:
                logger.warning(f"LLM description generation failed: {e}")
        
        # Select project owner (team lead or senior member)
        owner = None
        if team_members:
            # Prefer managers or senior roles
            senior_members = [
                m for m in team_members 
                if any(title in m["role"].lower() for title in ["manager", "vp", "director", "senior", "lead"])
            ]
            owner = random.choice(senior_members if senior_members else team_members)
        
        # Determine if project has due date (80% do)
        due_date = None
        if random.random() > 0.2:
            # Projects typically span 2 weeks to 3 months
            days_duration = random.randint(14, 90)
            due_date = (created_at + timedelta(days=days_duration)).date()
        
        project = {
            "project_id": project_id,
            "team_id": team["team_id"],
            "name": project_name,
            "description": description,
            "project_type": project_type,
            "created_at": created_at.isoformat(),
            "due_date": due_date.isoformat() if due_date else None,
            "archived": 0,
            "owner_id": owner["user_id"] if owner else None,
        }
        
        # Generate sections
        sections = self._generate_sections(project_id, project_type, created_at)
        
        return project, sections
    
    def generate_projects_for_team(self, team: Dict, team_members: List[Dict],
                                  project_types: Dict[str, float],
                                  num_projects: int,
                                  start_date: datetime,
                                  end_date: datetime) -> tuple[List[Dict], List[Dict]]:
        """Generate multiple projects for a team."""
        all_projects = []
        all_sections = []
        
        # Select project types based on distribution
        types = list(project_types.keys())
        weights = list(project_types.values())
        
        for _ in range(num_projects):
            project_type = random.choices(types, weights=weights)[0]
            
            # Generate creation time
            created_at = workday_datetime(start_date, end_date)
            
            project, sections = self.generate_project(
                team, team_members, project_type, created_at, end_date
            )
            
            all_projects.append(project)
            all_sections.extend(sections)
        
        return all_projects, all_sections