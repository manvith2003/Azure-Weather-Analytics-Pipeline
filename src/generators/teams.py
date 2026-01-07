"""Generate realistic teams and team memberships."""
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class TeamGenerator:
    """Generates realistic team structures."""
    
    # Team name patterns by department
    TEAM_PATTERNS = {
        "Engineering": [
            "Platform",
            "API",
            "Frontend",
            "Backend",
            "Mobile",
            "Infrastructure",
            "DevOps",
            "Security",
            "Data Engineering",
            "ML/AI",
            "Core Services",
            "Growth Engineering",
            "Integrations",
        ],
        "Product": [
            "Core Product",
            "Growth",
            "Platform",
            "Enterprise",
            "Analytics",
            "Mobile Product",
        ],
        "Design": [
            "Product Design",
            "Brand Design",
            "Design Systems",
            "Research",
        ],
        "Sales": [
            "Enterprise Sales",
            "Mid-Market Sales",
            "SMB Sales",
            "Sales Development",
            "Account Management",
            "Sales Operations",
        ],
        "Marketing": [
            "Demand Generation",
            "Content Marketing",
            "Product Marketing",
            "Brand Marketing",
            "Growth Marketing",
            "Marketing Operations",
        ],
        "Customer Success": [
            "Enterprise CS",
            "Mid-Market CS",
            "Onboarding",
            "Support",
            "CS Operations",
        ],
        "Operations": [
            "Business Operations",
            "IT",
            "Legal",
            "Facilities",
        ],
        "Finance": [
            "Financial Planning",
            "Accounting",
            "Revenue Operations",
        ],
        "HR": [
            "Recruiting",
            "People Operations",
            "Learning & Development",
        ],
    }
    
    def __init__(self, team_size_distribution: Dict[str, Tuple[int, int, float]]):
        """
        Initialize team generator.
        
        team_size_distribution: dict of {size_category: (min, max, probability)}
        """
        self.size_distribution = team_size_distribution
    
    def _select_team_size(self) -> int:
        """Select team size based on distribution."""
        categories = list(self.size_distribution.keys())
        probabilities = [self.size_distribution[cat][2] for cat in categories]
        
        category = random.choices(categories, weights=probabilities)[0]
        min_size, max_size, _ = self.size_distribution[category]
        
        return random.randint(min_size, max_size)
    
    def _generate_team_name(self, department: str, index: int) -> str:
        """Generate a realistic team name."""
        patterns = self.TEAM_PATTERNS.get(department, [f"{department}"])
        
        if index < len(patterns):
            return patterns[index]
        else:
            # Generate numbered teams for overflow
            return f"{department} Team {index - len(patterns) + 1}"
    
    def generate_teams_for_department(self, org_id: str, department: str,
                                     dept_users: List[Dict],
                                     created_at: datetime) -> Tuple[List[Dict], List[Dict]]:
        """
        Generate teams for a department and assign users.
        
        Returns: (teams, team_memberships)
        """
        if not dept_users:
            return [], []
        
        teams = []
        memberships = []
        
        # Determine number of teams needed
        total_users = len(dept_users)
        avg_team_size = sum(
            (min_s + max_s) / 2 * prob 
            for min_s, max_s, prob in self.size_distribution.values()
        )
        
        num_teams = max(1, int(total_users / avg_team_size))
        
        # Create teams
        for i in range(num_teams):
            team_id = str(uuid.uuid4())
            team_name = self._generate_team_name(department, i)
            
            # Add some variety to team descriptions
            descriptions = [
                f"Responsible for {team_name.lower()} initiatives and projects",
                f"Cross-functional team focused on {team_name.lower()}",
                f"Team dedicated to {team_name.lower()} development and operations",
                "",  # Some teams have no description
            ]
            
            team = {
                "team_id": team_id,
                "org_id": org_id,
                "name": team_name,
                "description": random.choice(descriptions),
                "created_at": created_at.isoformat(),
            }
            teams.append(team)
        
        # Assign users to teams
        # Sort users by created_at to respect hiring timeline
        sorted_users = sorted(dept_users, key=lambda u: u["created_at"])
        
        for user in sorted_users:
            # Select a random team (some randomness in assignment)
            team = random.choice(teams)
            
            # User joins team shortly after being created
            user_created = datetime.fromisoformat(user["created_at"])
            join_delay = timedelta(days=random.randint(0, 7))
            joined_at = user_created + join_delay
            
            membership = {
                "membership_id": str(uuid.uuid4()),
                "team_id": team["team_id"],
                "user_id": user["user_id"],
                "joined_at": joined_at.isoformat(),
            }
            memberships.append(membership)
        
        logger.info(f"Created {len(teams)} teams for {department} with {len(memberships)} memberships")
        
        return teams, memberships
    
    def generate_all_teams(self, org_id: str, users: List[Dict],
                          created_at: datetime) -> Tuple[List[Dict], List[Dict]]:
        """Generate all teams and memberships for an organization."""
        all_teams = []
        all_memberships = []
        
        # Group users by department
        users_by_dept = {}
        for user in users:
            dept = user["department"]
            if dept not in users_by_dept:
                users_by_dept[dept] = []
            users_by_dept[dept].append(user)
        
        # Generate teams for each department
        for department, dept_users in users_by_dept.items():
            teams, memberships = self.generate_teams_for_department(
                org_id, department, dept_users, created_at
            )
            all_teams.extend(teams)
            all_memberships.extend(memberships)
        
        logger.info(f"Generated {len(all_teams)} total teams with {len(all_memberships)} memberships")
        
        return all_teams, all_memberships
    
    def get_team_members(self, team_id: str, memberships: List[Dict],
                        users: List[Dict]) -> List[Dict]:
        """Get all users in a team."""
        member_ids = [m["user_id"] for m in memberships if m["team_id"] == team_id]
        return [u for u in users if u["user_id"] in member_ids]