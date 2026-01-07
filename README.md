# Asana RL Environment - Seed Data Generator

This project generates realistic seed data for an Asana reinforcement learning environment, simulating a B2B SaaS company workspace with 5,000-10,000 employees.

## Overview

The generator creates a complete SQLite database representing a realistic Asana workspace including:
- Organizations and teams
- Users with realistic demographic distributions
- Projects with appropriate team assignments
- Tasks with proper temporal and relational consistency
- Comments, custom fields, tags, and attachments

## Features

- ✅ **Realistic Data Distribution**: Based on industry research and Asana benchmarks
- ✅ **Temporal Consistency**: All timestamps respect logical ordering
- ✅ **LLM-Generated Content**: Uses Claude API for natural task names and descriptions
- ✅ **Configurable Scale**: Adjust organization size, project count, and date ranges
- ✅ **Complete Schema**: Full relational database with proper foreign keys

## Requirements

- Python 3.9+
- Anthropic API key (for LLM content generation)
- ~500MB disk space for generated database

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd asana-rl-seed-data
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

To get an API key:
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key

## Usage

### Quick Start

Generate the database with default settings:

```bash
python src/main.py
```

This will create `output/asana_simulation.sqlite` with approximately:
- 7,500 users
- 50 teams
- 300 projects
- 4,500+ tasks
- Comments, custom fields, tags, and attachments

### Configuration

Edit `.env` to customize the generation:

```bash
# Organization size
ORG_SIZE=7500

# Number of teams and projects
NUM_TEAMS=50
PROJECT_COUNT=300

# Tasks per project (average)
TASK_MULTIPLIER=15

# Date range for historical data
START_DATE=2024-07-01
END_DATE=2026-01-06

# Database output path
DB_PATH=output/asana_simulation.sqlite
```

### Generation Time

- Small dataset (1,000 users): ~5 minutes
- Default dataset (7,500 users): ~20-30 minutes
- Large dataset (10,000 users): ~45 minutes

*Note: LLM API calls add time. Disable LLM generation for faster runs (tasks will use templates).*

## Project Structure

```
asana-rl-seed-data/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── schema.sql               # Database schema
├── .env.example             # Environment template
├── src/
│   ├── main.py              # Entry point
│   ├── scrapers/
│   │   └── companies.py     # Company name generation
│   ├── generators/
│   │   ├── users.py         # User generation
│   │   ├── teams.py         # Team structure
│   │   ├── projects.py      # Project generation
│   │   ├── tasks.py         # Task generation
│   │   ├── comments.py      # Comment generation
│   │   ├── custom_fields.py # Custom field generation
│   │   ├── tags.py          # Tag generation
│   │   └── attachments.py   # Attachment generation
│   └── utils/
│       ├── config.py        # Configuration management
│       ├── database.py      # Database utilities
│       ├── llm.py           # LLM API wrapper
│       └── date_helpers.py  # Date generation utilities
├── prompts/                 # LLM prompt templates (if any)
└── output/
    └── asana_simulation.sqlite  # Generated database
```

## Database Schema

The generated database includes the following tables:

### Core Entities
- `organizations` - Top-level workspace
- `teams` - Departmental teams
- `users` - Employees/members
- `team_memberships` - User-team associations

### Work Items
- `projects` - Collections of tasks
- `sections` - Project subdivisions
- `tasks` - Fundamental work units
- `comments` - Task discussions

### Metadata
- `custom_field_definitions` - Project-specific fields
- `custom_field_options` - Enum field values
- `custom_field_values` - Custom field data on tasks
- `tags` - Cross-project labels
- `task_tags` - Task-tag associations
- `attachments` - File attachments

See `schema.sql` for complete DDL.

## Data Generation Methodology

### Users
- Names generated using Faker library (US demographic distribution)
- Roles distributed by department and seniority
- Email addresses follow realistic patterns
- Hiring spread over time using beta distribution

### Teams
- Size distribution: 30% small (3-8), 50% medium (9-15), 20% large (16-30)
- Named according to department patterns
- Users assigned based on department and timing

### Projects
- Types distributed by department (Sprint, Feature Development, Bug Tracking, etc.)
- Names generated using LLM with project-type-specific patterns
- Due dates set for 80% of projects (2 weeks to 3 months)
- Sections vary by project type

### Tasks
- 15 tasks per project on average (±5 variance)
- Assignees selected with workload balancing
- Due dates: 25% within 1 week, 40% within 1 month, 20% 1-3 months, 10% no due date, 5% overdue
- Completion rates vary by project type (40-95%)
- 20% of tasks have subtasks (2-5 each)
- Descriptions: 20% empty, 50% short, 20% medium, 10% detailed

### Comments
- 60% of tasks have comments (1-8 per task)
- Types: updates, questions, blockers, reviews
- Timestamps spread throughout task lifecycle
- 30% generated via LLM, 70% template-based

### Custom Fields
- 2-5 per project
- Types: enum (Priority, Status), number (Story Points), text (Sprint), date (Release)
- 70% of tasks have values set

### Tags
- Organization-wide labels (priority, type, area, etc.)
- 40% of tasks tagged with 1-3 tags

### Attachments
- 25% of tasks have attachments (1-3 each)
- Types vary by task context (images, documents, code, etc.)
- File sizes and types realistic for content type

## Verification

Query the database to verify data quality:

```bash
sqlite3 output/asana_simulation.sqlite
```

```sql
-- Count records
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL SELECT 'teams', COUNT(*) FROM teams
UNION ALL SELECT 'projects', COUNT(*) FROM projects
UNION ALL SELECT 'tasks', COUNT(*) FROM tasks;

-- Check temporal consistency
SELECT COUNT(*) as invalid_completions 
FROM tasks 
WHERE completed = 1 
  AND completed_at < created_at;

-- Verify no orphaned tasks
SELECT COUNT(*) as orphaned_tasks
FROM tasks t
LEFT JOIN projects p ON t.project_id = p.project_id
WHERE p.project_id IS NULL;
```

## Troubleshooting

### API Key Issues
```
ValueError: ANTHROPIC_API_KEY not found in environment
```
**Solution**: Ensure `.env` file exists and contains valid API key.

### Memory Issues
```
MemoryError: Unable to allocate array
```
**Solution**: Reduce `ORG_SIZE` or `PROJECT_COUNT` in `.env`.

### Slow Generation
**Solution**: 
- Reduce LLM usage by modifying `llm_generator=None` in generators
- Decrease `TASK_MULTIPLIER` or `PROJECT_COUNT`

## Data Quality Checks

The generator ensures:
- ✅ No temporal paradoxes (completed_at > created_at)
- ✅ Referential integrity (all foreign keys valid)
- ✅ Realistic distributions (task completion rates, due dates)
- ✅ Workload balancing (assignee distributions)
- ✅ Business logic consistency (subtasks complete with parents)

## Contributing

This is a take-home assignment submission. For questions or improvements, please contact the repository owner.

## License

This project is created for educational and evaluation purposes.

## Acknowledgments

- Anthropic Claude API for content generation
- Faker library for realistic name generation
- Research sources: Asana "Anatomy of Work" reports, industry benchmarks

## Contact

For questions about this implementation, please reach out via the submission form.