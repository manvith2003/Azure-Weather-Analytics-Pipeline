# LLM Prompts Used in Generation

This document contains all LLM prompts used to generate realistic content.

## Task Name Generation

**Prompt Template:**
```
Generate a single realistic task name for an Asana task.

Project Type: {project_type}
Project Name: {project_name}
Team: {team_type}
Context: {context}

Requirements:
- For Engineering: Use pattern "[Component] - [Action] - [Detail]" (e.g., "API - Implement - Rate limiting endpoint")
- For Marketing: Use pattern "[Campaign] - [Deliverable]" (e.g., "Q4 Launch - Email template design")
- For Design: Use pattern "[Feature/Asset] - [Action]" (e.g., "Mobile Nav - Create high-fidelity mockups")
- Be specific and realistic
- Keep it under 80 characters
- No quotes or extra formatting

Return ONLY the task name, nothing else.
```

**Temperature:** 0.8  
**Max Tokens:** 100

## Task Description Generation

**Prompt Template:**
```
Generate a realistic task description for an Asana task.

Task Name: {task_name}
Project Type: {project_type}
Length: {length}

Requirements:
- For "short": 1-2 sentences
- For "medium": 2-4 sentences, may include a simple bullet list
- For "detailed": Full description with context, acceptance criteria, bullet points
- Use realistic business language
- Include relevant details (requirements, context, links, etc.)
- Format naturally (may use markdown-style bullets if needed)

Return ONLY the description text, no preamble.
```

**Temperature:** 0.7  
**Max Tokens:** 100-400 (varies by length)

## Comment Generation

**Prompt Template:**
```
Generate a realistic comment for an Asana task.

Task: {task_name}
User Role: {user_role}
Comment Type: {comment_type}

Types:
- "update": Status update or progress note
- "question": Question about the task
- "blocker": Reporting a blocker or issue
- "review": Review feedback or approval

Requirements:
- Keep it natural and conversational (1-3 sentences)
- Use realistic business communication style
- No excessive formality
- Don't use emojis

Return ONLY the comment text.
```

**Temperature:** 0.8  
**Max Tokens:** 150

## Project Description Generation

**Prompt Template:**
```
Generate a realistic project description for Asana.

Project Name: {project_name}
Project Type: {project_type}
Team: {team}

Requirements:
- 2-4 sentences describing the project goals and scope
- Professional business language
- Include key objectives or deliverables
- Realistic for a {team} team

Return ONLY the description text.
```

**Temperature:** 0.7  
**Max Tokens:** 200

## Design Rationale

### Why LLM for Content Generation?

1. **Variety**: Templates create repetitive patterns; LLMs provide natural variation
2. **Context-Awareness**: LLMs adapt content to project type and team context
3. **Realism**: Generated text mimics actual business communication
4. **Scalability**: Can generate thousands of unique items without manual writing

### Temperature Settings

- **0.7 for descriptions/projects**: Balanced creativity with consistency
- **0.8 for names/comments**: Higher creativity for more variety

### Fallback Strategy

All generators have template-based fallbacks if LLM fails:
- Network issues
- API rate limits
- Missing API key

This ensures generation always completes successfully.