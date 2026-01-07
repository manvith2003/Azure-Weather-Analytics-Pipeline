"""Generate realistic file attachments for tasks."""
import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class AttachmentGenerator:
    """Generates realistic file attachments."""
    
    # File types by category
    FILE_TYPES = {
        "images": [
            ("screenshot.png", "image/png", (50_000, 500_000)),
            ("mockup.png", "image/png", (100_000, 1_000_000)),
            ("diagram.jpg", "image/jpeg", (80_000, 400_000)),
            ("wireframe.png", "image/png", (60_000, 300_000)),
        ],
        "documents": [
            ("requirements.pdf", "application/pdf", (100_000, 2_000_000)),
            ("spec.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", (50_000, 500_000)),
            ("notes.txt", "text/plain", (5_000, 50_000)),
            ("proposal.pdf", "application/pdf", (200_000, 3_000_000)),
        ],
        "spreadsheets": [
            ("data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", (50_000, 1_000_000)),
            ("analysis.csv", "text/csv", (10_000, 500_000)),
            ("metrics.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", (100_000, 2_000_000)),
        ],
        "code": [
            ("implementation.zip", "application/zip", (10_000, 5_000_000)),
            ("patch.diff", "text/plain", (5_000, 100_000)),
            ("config.json", "application/json", (1_000, 50_000)),
            ("script.py", "text/x-python", (2_000, 100_000)),
        ],
        "presentations": [
            ("slides.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", (500_000, 10_000_000)),
            ("demo.pdf", "application/pdf", (1_000_000, 5_000_000)),
        ],
        "design": [
            ("design.fig", "application/octet-stream", (1_000_000, 50_000_000)),
            ("mockup.sketch", "application/octet-stream", (500_000, 20_000_000)),
            ("assets.zip", "application/zip", (1_000_000, 100_000_000)),
        ],
    }
    
    def _select_file_type(self, task: Dict) -> Tuple[str, str, int]:
        """Select appropriate file type based on task context."""
        # Determine likely file category from task name/description
        task_text = (task["name"] + " " + (task["description"] or "")).lower()
        
        # Weight file types based on task content
        if any(word in task_text for word in ["design", "mockup", "ui", "ux"]):
            category = random.choices(
                ["images", "design", "documents"],
                weights=[0.5, 0.3, 0.2]
            )[0]
        elif any(word in task_text for word in ["code", "implement", "bug", "fix"]):
            category = random.choices(
                ["code", "images", "documents"],
                weights=[0.5, 0.3, 0.2]
            )[0]
        elif any(word in task_text for word in ["data", "analysis", "metrics"]):
            category = random.choices(
                ["spreadsheets", "documents", "images"],
                weights=[0.6, 0.3, 0.1]
            )[0]
        elif any(word in task_text for word in ["presentation", "demo", "pitch"]):
            category = random.choices(
                ["presentations", "documents", "images"],
                weights=[0.6, 0.2, 0.2]
            )[0]
        else:
            # Default distribution
            category = random.choices(
                list(self.FILE_TYPES.keys()),
                weights=[0.3, 0.3, 0.1, 0.1, 0.1, 0.1]
            )[0]
        
        # Select file from category
        filename, mime_type, size_range = random.choice(self.FILE_TYPES[category])
        
        # Add some variety to filenames
        prefix = random.choice([
            "", "final_", "updated_", "v2_", "draft_", "revised_",
        ])
        filename = prefix + filename
        
        # Generate file size
        file_size = random.randint(*size_range)
        
        return filename, mime_type, file_size
    
    def _generate_upload_time(self, task: Dict) -> datetime:
        """Generate realistic upload timestamp."""
        task_created = datetime.fromisoformat(task["created_at"])
        
        if task["completed"]:
            task_completed = datetime.fromisoformat(task["completed_at"])
            # Uploaded during task lifecycle
            max_seconds = int((task_completed - task_created).total_seconds())
        else:
            # Uploaded since creation
            now = datetime.now()
            max_seconds = int((now - task_created).total_seconds())
        
        # Most attachments uploaded early in task lifecycle
        # Use beta distribution for realistic pattern
        time_proportion = random.betavariate(2, 5)  # Skewed toward early
        
        upload_time = task_created + timedelta(seconds=int(max_seconds * time_proportion))
        
        # Set to work hours
        upload_time = upload_time.replace(
            hour=random.randint(9, 17),
            minute=random.randint(0, 59),
            second=0,
            microsecond=0
        )
        
        return upload_time
    
    def _select_uploader(self, task: Dict, users: List[Dict]) -> str:
        """Select who uploaded the file."""
        # 70% assignee, 20% creator, 10% other
        rand = random.random()
        
        if rand < 0.7 and task["assignee_id"]:
            return task["assignee_id"]
        elif rand < 0.9:
            return task["created_by"]
        else:
            # Random user (could be reviewer, stakeholder, etc.)
            return random.choice(users)["user_id"]
    
    def generate_attachment(self, task: Dict, users: List[Dict]) -> Dict:
        """Generate a single attachment."""
        filename, file_type, file_size = self._select_file_type(task)
        uploaded_by = self._select_uploader(task, users)
        uploaded_at = self._generate_upload_time(task)
        
        # Generate simulated URL
        url = f"https://s3.amazonaws.com/asana-attachments/{uuid.uuid4()}/{filename}"
        
        return {
            "attachment_id": str(uuid.uuid4()),
            "task_id": task["task_id"],
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "uploaded_by": uploaded_by,
            "uploaded_at": uploaded_at.isoformat(),
            "url": url,
        }
    
    def generate_attachments_for_tasks(self, tasks: List[Dict], users: List[Dict],
                                      attachment_probability: float,
                                      attachments_per_task: Tuple[int, int]) -> List[Dict]:
        """Generate attachments for multiple tasks."""
        attachments = []
        
        for task in tasks:
            # Determine if task has attachments
            if random.random() < attachment_probability:
                num_attachments = random.randint(*attachments_per_task)
                
                for _ in range(num_attachments):
                    attachment = self.generate_attachment(task, users)
                    attachments.append(attachment)
        
        return attachments