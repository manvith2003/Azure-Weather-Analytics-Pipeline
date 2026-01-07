"""Generate realistic users with proper demographic distribution."""
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker
import logging

logger = logging.getLogger(__name__)

# Initialize Faker with US locale for realistic names
fake = Faker('en_US')


class UserGenerator:
    """Generates realistic user data based on census demographics."""
    
    # Role distributions for B2B SaaS (based on typical org charts)
    ROLE_BY_DEPARTMENT = {
        "Engineering": [
            ("Software Engineer", 0.50),
            ("Senior Software Engineer", 0.25),
            ("Staff Engineer", 0.10),
            ("Engineering Manager", 0.10),
            ("VP Engineering", 0.03),
            ("CTO", 0.02),
        ],
        "Product": [
            ("Product Manager", 0.60),
            ("Senior Product Manager", 0.25),
            ("Principal Product Manager", 0.10),
            ("VP Product", 0.05),
        ],
        "Design": [
            ("Product Designer", 0.60),
            ("Senior Designer", 0.25),
            ("Design Manager", 0.10),
            ("VP Design", 0.05),
        ],
        "Sales": [
            ("Account Executive", 0.50),
            ("Senior AE", 0.20),
            ("Sales Manager", 0.15),
            ("VP Sales", 0.10),
            ("Chief Revenue Officer", 0.05),
        ],
        "Marketing": [
            ("Marketing Manager", 0.40),
            ("Content Manager", 0.20),
            ("Demand Gen Manager", 0.15),
            ("Marketing Director", 0.15),
            ("VP Marketing", 0.10),
        ],
        "Customer Success": [
            ("Customer Success Manager", 0.60),
            ("Senior CSM", 0.20),
            ("CS Manager", 0.15),
            ("VP Customer Success", 0.05),
        ],
        "Operations": [
            ("Operations Manager", 0.50),
            ("Business Analyst", 0.30),
            ("VP Operations", 0.10),
            ("COO", 0.10),
        ],
        "Finance": [
            ("Financial Analyst", 0.40),
            ("Accountant", 0.30),
            ("Finance Manager", 0.20),
            ("CFO", 0.10),
        ],
        "HR": [
            ("Recruiter", 0.40),
            ("HR Manager", 0.30),
            ("People Operations", 0.20),
            ("VP HR", 0.10),
        ],
    }
    
    def __init__(self, org_domain: str):
        self.org_domain = org_domain
        self.generated_emails = set()
    
    def _select_role(self, department: str) -> str:
        """Select a role based on department distribution."""
        roles = self.ROLE_BY_DEPARTMENT.get(department, [("Employee", 1.0)])
        roles_list, weights = zip(*roles)
        return random.choices(roles_list, weights=weights)[0]
    
    def _generate_email(self, name: str) -> str:
        """Generate unique email address."""
        # Convert name to email format
        parts = name.lower().split()
        
        # Try different formats until we get a unique one
        formats = [
            f"{parts[0]}.{parts[-1]}@{self.org_domain}",
            f"{parts[0][0]}{parts[-1]}@{self.org_domain}",
            f"{parts[0]}.{parts[-1]}{random.randint(1, 99)}@{self.org_domain}",
        ]
        
        for email in formats:
            if email not in self.generated_emails:
                self.generated_emails.add(email)
                return email
        
        # Fallback with UUID
        email = f"{parts[0]}.{parts[-1]}.{uuid.uuid4().hex[:6]}@{self.org_domain}"
        self.generated_emails.add(email)
        return email
    
    def generate_user(self, org_id: str, department: str, 
                     created_at: datetime) -> Dict:
        """Generate a single realistic user."""
        name = fake.name()
        role = self._select_role(department)
        email = self._generate_email(name)
        
        return {
            "user_id": str(uuid.uuid4()),
            "org_id": org_id,
            "email": email,
            "name": name,
            "role": role,
            "department": department,
            "created_at": created_at.isoformat(),
            "is_active": 1 if random.random() > 0.02 else 0,  # 2% inactive
        }
    
    def generate_users_for_org(self, org_id: str, org_size: int,
                              department_distribution: Dict[str, float],
                              start_date: datetime, end_date: datetime) -> List[Dict]:
        """Generate all users for an organization."""
        users = []
        
        # Calculate users per department
        for department, proportion in department_distribution.items():
            dept_size = int(org_size * proportion)
            
            for i in range(dept_size):
                # Spread user creation over time (most hired early)
                # Using beta distribution for realistic hiring curve
                alpha, beta = 2, 5  # More hiring early on
                time_proportion = random.betavariate(alpha, beta)
                
                days_diff = (end_date - start_date).days
                days_offset = int(days_diff * time_proportion)
                created_at = start_date + timedelta(days=days_offset)
                
                # Set to work hours
                created_at = created_at.replace(
                    hour=random.randint(9, 17),
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0
                )
                
                user = self.generate_user(org_id, department, created_at)
                users.append(user)
        
        logger.info(f"Generated {len(users)} users across {len(department_distribution)} departments")
        
        return users
    
    def get_users_by_department(self, users: List[Dict], 
                               department: str) -> List[Dict]:
        """Filter users by department."""
        return [u for u in users if u["department"] == department]
    
    def get_active_users(self, users: List[Dict]) -> List[Dict]:
        """Get only active users."""
        return [u for u in users if u["is_active"] == 1]