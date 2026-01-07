"""Main script to generate Asana simulation database."""
import logging
import sys
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
import uuid
import random



# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import config
from utils.database import Database
from utils.llm import LLMGenerator
from scrapers.companies import CompanyScraper
from generators.users import UserGenerator
from generators.teams import TeamGenerator
from generators.projects import ProjectGenerator
from generators.tasks import TaskGenerator
from generators.custom_fields import CustomFieldGenerator
from generators.comments import CommentGenerator
from generators.tags import TagGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main generation pipeline."""
    logger.info("="*80)
    logger.info("Starting Asana Simulation Data Generation")
    logger.info("="*80)
    logger.info(f"Configuration:")
    logger.info(f"  Organization Size: {config.org_size} employees")
    logger.info(f"  Number of Teams: {config.num_teams}")
    logger.info(f"  Number of Projects: {config.project_count}")
    logger.info(f"  Date Range: {config.start_date} to {config.end_date}")
    logger.info("="*80)
    
    # Initialize components
    logger.info("Initializing components...")
    db = Database(config.db_path)
    db.connect()
    
    # Check if database already exists with data
    if db.table_exists("organizations"):
        logger.warning("Database already contains data. Dropping existing tables...")
        db.initialize_schema(config.schema_path, drop_existing=True)
    else:
        db.initialize_schema(config.schema_path)
    
    llm = LLMGenerator(config.anthropic_api_key)
    company_scraper = CompanyScraper()
    
    # Step 1: Create Organization
    logger.info("\n[1/9] Creating organization...")
    company = company_scraper.select_company()
    org_id = str(uuid.uuid4())
    
    organization = {
        "org_id": org_id,
        "name": company["name"],
        "domain": company["domain"],
        "created_at": config.start_date.isoformat(),
        "is_organization": 1,
        "employee_count": config.org_size,
    }
    db.insert_one("organizations", organization)
    logger.info(f"  Created organization: {company['name']}")
    
    # Step 2: Generate Users
    logger.info("\n[2/9] Generating users...")
    user_gen = UserGenerator(company["domain"])
    users = user_gen.generate_users_for_org(
        org_id,
        config.org_size,
        config.department_distribution,
        datetime.combine(config.start_date, datetime.min.time()),
        datetime.combine(config.end_date, datetime.min.time())
    )
    
    logger.info(f"  Inserting {len(users)} users...")
    db.insert_batch("users", users)
    logger.info(f"  ✓ {len(users)} users created")
    
    # Step 3: Generate Teams
    logger.info("\n[3/9] Generating teams...")
    team_gen = TeamGenerator(config.team_size_distribution)
    teams, memberships = team_gen.generate_all_teams(
        org_id,
        users,
        datetime.combine(config.start_date, datetime.min.time())
    )
    
    logger.info(f"  Inserting {len(teams)} teams...")
    db.insert_batch("teams", teams)
    logger.info(f"  Inserting {len(memberships)} team memberships...")
    db.insert_batch("team_memberships", memberships)
    logger.info(f"  ✓ {len(teams)} teams with {len(memberships)} memberships")
    
    # Step 4: Generate Projects
    logger.info("\n[4/9] Generating projects...")
    project_gen = ProjectGenerator(llm)
    
    all_projects = []
    all_sections = []
    
    # Distribute projects across teams
    projects_per_team = config.project_count // len(teams)
    
    for team in tqdm(teams, desc="  Creating projects"):
        # Get team members
        team_member_ids = [m["user_id"] for m in memberships if m["team_id"] == team["team_id"]]
        team_members = [u for u in users if u["user_id"] in team_member_ids]
        
        if not team_members:
            continue
        
        projects, sections = project_gen.generate_projects_for_team(
            team,
            team_members,
            config.project_types,
            projects_per_team,
            datetime.combine(config.start_date, datetime.min.time()),
            datetime.combine(config.end_date, datetime.min.time())
        )
        
        all_projects.extend(projects)
        all_sections.extend(sections)
    
    logger.info(f"  Inserting {len(all_projects)} projects...")
    db.insert_batch("projects", all_projects)
    logger.info(f"  Inserting {len(all_sections)} sections...")
    db.insert_batch("sections", all_sections)
    logger.info(f"  ✓ {len(all_projects)} projects with {len(all_sections)} sections")
    
    # Step 5: Generate Tasks
    logger.info("\n[5/9] Generating tasks...")
    task_gen = TaskGenerator(llm)
    
    all_tasks = []
    now = datetime.combine(config.end_date, datetime.min.time())
    
    for project in tqdm(all_projects, desc="  Creating tasks"):
        # Get project sections
        project_sections = [s for s in all_sections if s["project_id"] == project["project_id"]]
        
        # Get team members
        team = next(t for t in teams if t["team_id"] == project["team_id"])
        team_member_ids = [m["user_id"] for m in memberships if m["team_id"] == team["team_id"]]
        team_members = [u for u in users if u["user_id"] in team_member_ids]
        
        if not team_members or not project_sections:
            continue
        
        # Generate tasks
        num_tasks = config.task_multiplier + random.randint(-5, 5)
        tasks = task_gen.generate_tasks_for_project(
            project,
            project_sections,
            team_members,
            num_tasks,
            datetime.combine(config.start_date, datetime.min.time()),
            datetime.combine(config.end_date, datetime.min.time()),
            now,
            config.subtask_probability
        )
        
        all_tasks.extend(tasks)
        
        # Batch insert every 1000 tasks to manage memory
        if len(all_tasks) >= 1000:
            db.insert_batch("tasks", all_tasks)
            all_tasks = []
    
    # Insert remaining tasks
    if all_tasks:
        db.insert_batch("tasks", all_tasks)
    
    total_tasks = db.get_count("tasks")
    logger.info(f"  ✓ {total_tasks} tasks created")
    
    # Step 6: Generate Comments
    logger.info("\n[6/9] Generating comments...")
    comment_gen = CommentGenerator(llm)
    
    # Fetch all tasks for comment generation
    all_tasks_from_db = db.query("SELECT * FROM tasks")
    
    all_comments = []
    for task in tqdm(all_tasks_from_db, desc="  Creating comments"):
        if random.random() < config.comment_probability:
            # Get task creator
            creator = next((u for u in users if u["user_id"] == task["created_by"]), None)
            team = next((t for t in teams if any(
                p["project_id"] == task["project_id"] for p in all_projects if p["team_id"] == t["team_id"]
            )), None)
            
            if creator and team:
                team_member_ids = [m["user_id"] for m in memberships if m["team_id"] == team["team_id"]]
                team_members = [u for u in users if u["user_id"] in team_member_ids]
                
                comments = comment_gen.generate_comments_for_task(
                    dict(task),
                    team_members,
                    random.randint(*config.comments_per_task)
                )
                all_comments.extend(comments)
                
                # Batch insert
                if len(all_comments) >= 1000:
                    db.insert_batch("comments", all_comments)
                    all_comments = []
    
    if all_comments:
        db.insert_batch("comments", all_comments)
    
    total_comments = db.get_count("comments")
    logger.info(f"  ✓ {total_comments} comments created")
    
    # Step 7: Generate Custom Fields
    logger.info("\n[7/9] Generating custom fields...")
    custom_field_gen = CustomFieldGenerator()
    
    all_field_defs = []
    all_field_options = []
    all_field_values = []
    
    for project in tqdm(all_projects, desc="  Creating custom fields"):
        num_fields = random.randint(*config.custom_fields_per_project)
        field_defs, field_options = custom_field_gen.generate_custom_fields_for_project(
            project,
            num_fields
        )
        
        all_field_defs.extend(field_defs)
        all_field_options.extend(field_options)
        
        # Generate values for tasks in this project
        project_tasks = [t for t in all_tasks_from_db if t["project_id"] == project["project_id"]]
        field_values = custom_field_gen.generate_field_values_for_tasks(
            project_tasks,
            field_defs,
            field_options
        )
        all_field_values.extend(field_values)
    
    logger.info(f"  Inserting custom field data...")
    db.insert_batch("custom_field_definitions", all_field_defs)
    db.insert_batch("custom_field_options", all_field_options)
    db.insert_batch("custom_field_values", all_field_values)
    logger.info(f"  ✓ {len(all_field_defs)} custom fields with {len(all_field_values)} values")
    
    # Step 8: Generate Tags
    logger.info("\n[8/9] Generating tags...")
    tag_gen = TagGenerator()
    
    tags = tag_gen.generate_tags_for_org(
        org_id,
        datetime.combine(config.start_date, datetime.min.time())
    )
    db.insert_batch("tags", tags)
    
    # Tag assignments
    task_tags = tag_gen.assign_tags_to_tasks(
        all_tasks_from_db,
        tags,
        config.tags_per_task_probability,
        config.tags_per_task
    )
    db.insert_batch("task_tags", task_tags)
    logger.info(f"  ✓ {len(tags)} tags with {len(task_tags)} assignments")
    
    # Step 9: Generate Attachments
    logger.info("\n[9/9] Generating attachments...")
    from generators.attachments import AttachmentGenerator
    attachment_gen = AttachmentGenerator()
    
    attachments = attachment_gen.generate_attachments_for_tasks(
        all_tasks_from_db,
        users,
        config.attachment_probability,
        config.attachments_per_task
    )
    db.insert_batch("attachments", attachments)
    logger.info(f"  ✓ {len(attachments)} attachments created")
    
    # Final summary
    logger.info("\n" + "="*80)
    logger.info("Generation Complete!")
    logger.info("="*80)
    logger.info(f"Database: {config.db_path}")
    logger.info(f"\nFinal Statistics:")
    logger.info(f"  Organizations: {db.get_count('organizations')}")
    logger.info(f"  Users: {db.get_count('users')}")
    logger.info(f"  Teams: {db.get_count('teams')}")
    logger.info(f"  Projects: {db.get_count('projects')}")
    logger.info(f"  Tasks: {db.get_count('tasks')}")
    logger.info(f"  Comments: {db.get_count('comments')}")
    logger.info(f"  Custom Fields: {db.get_count('custom_field_definitions')}")
    logger.info(f"  Tags: {db.get_count('tags')}")
    logger.info(f"  Attachments: {db.get_count('attachments')}")
    logger.info("="*80)
    
    db.close()


if __name__ == "__main__":
    import uuid
    import random
    main()