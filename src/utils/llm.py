"""LLM utilities for generating realistic text content."""
import os
import anthropic
import logging
from typing import List, Optional
import time

logger = logging.getLogger(__name__)


class LLMGenerator:
    """Wrapper for Claude API to generate realistic Asana content."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate text using Claude."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return ""
    
    def generate_batch(self, prompts: List[str], temperature: float = 0.7, 
                      delay: float = 0.5) -> List[str]:
        """Generate multiple texts with rate limiting."""
        results = []
        
        for i, prompt in enumerate(prompts):
            result = self.generate(prompt, temperature)
            results.append(result)
            
            # Rate limiting
            if i < len(prompts) - 1:
                time.sleep(delay)
                
        return results
    
    def generate_task_name(self, project_type: str, project_name: str, 
                          team_type: str, context: str = "") -> str:
        """Generate a realistic task name."""
        prompt = f"""Generate a single realistic task name for an Asana task.

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

Return ONLY the task name, nothing else."""

        return self.generate(prompt, temperature=0.8, max_tokens=100)
    
    def generate_task_description(self, task_name: str, project_type: str,
                                  length: str = "medium") -> str:
        """Generate a realistic task description."""
        
        if length == "empty":
            return ""
            
        prompt = f"""Generate a realistic task description for an Asana task.

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

Return ONLY the description text, no preamble."""

        max_tokens = {"short": 100, "medium": 200, "detailed": 400}[length]
        
        return self.generate(prompt, temperature=0.7, max_tokens=max_tokens)
    
    def generate_comment(self, task_name: str, user_role: str, 
                        comment_type: str = "update") -> str:
        """Generate a realistic comment/update on a task."""
        
        prompt = f"""Generate a realistic comment for an Asana task.

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

Return ONLY the comment text."""

        return self.generate(prompt, temperature=0.8, max_tokens=150)
    
    def generate_project_description(self, project_name: str, 
                                    project_type: str, team: str) -> str:
        """Generate a realistic project description."""
        
        prompt = f"""Generate a realistic project description for Asana.

Project Name: {project_name}
Project Type: {project_type}
Team: {team}

Requirements:
- 2-4 sentences describing the project goals and scope
- Professional business language
- Include key objectives or deliverables
- Realistic for a {team} team

Return ONLY the description text."""

        return self.generate(prompt, temperature=0.7, max_tokens=200)