"""Generate custom fields for projects."""
import uuid
import random
from datetime import datetime
from typing import List, Dict, Tuple

class CustomFieldGenerator:
    """Generates custom fields and their values."""
    
    FIELD_TEMPLATES = {
        "Priority": {
            "type": "enum",
            "options": [
                ("Critical", "#FF0000"),
                ("High", "#FF6B00"),
                ("Medium", "#FFA500"),
                ("Low", "#00AA00"),
            ]
        },
        "Status": {
            "type": "enum",
            "options": [
                ("Not Started", "#CCCCCC"),
                ("In Progress", "#4A90E2"),
                ("Blocked", "#FF0000"),
                ("Complete", "#7ED321"),
            ]
        },
        "Effort": {
            "type": "enum",
            "options": [
                ("XS", "#E3E3E3"),
                ("S", "#C2C2C2"),
                ("M", "#A1A1A1"),
                ("L", "#808080"),
                ("XL", "#5F5F5F"),
            ]
        },
        "Sprint": {
            "type": "text",
        },
        "Story Points": {
            "type": "number",
        },
        "Target Release": {
            "type": "date",
        },
    }
    
    def generate_custom_fields_for_project(self, project: Dict,
                                          num_fields: int) -> Tuple[List[Dict], List[Dict]]:
        """Generate custom fields for a project."""
        field_defs = []
        field_options = []
        
        # Select fields based on project type
        available_fields = list(self.FIELD_TEMPLATES.keys())
        selected_fields = random.sample(available_fields, min(num_fields, len(available_fields)))
        
        for field_name in selected_fields:
            field_id = str(uuid.uuid4())
            template = self.FIELD_TEMPLATES[field_name]
            
            field_def = {
                "field_id": field_id,
                "project_id": project["project_id"],
                "name": field_name,
                "field_type": template["type"],
                "description": "",
                "created_at": project["created_at"],
            }
            field_defs.append(field_def)
            
            # Add options for enum fields
            if template["type"] == "enum":
                for i, (value, color) in enumerate(template["options"]):
                    option = {
                        "option_id": str(uuid.uuid4()),
                        "field_id": field_id,
                        "value": value,
                        "color": color,
                        "position": i,
                    }
                    field_options.append(option)
        
        return field_defs, field_options
    
    def generate_field_values_for_tasks(self, tasks: List[Dict],
                                       field_defs: List[Dict],
                                       field_options: List[Dict]) -> List[Dict]:
        """Generate custom field values for tasks."""
        values = []
        
        for task in tasks:
            # 70% of tasks have custom field values
            if random.random() > 0.3:
                for field_def in field_defs:
                    if field_def["project_id"] != task["project_id"]:
                        continue
                    
                    value_id = str(uuid.uuid4())
                    
                    if field_def["field_type"] == "enum":
                        # Select a random option
                        options = [o for o in field_options if o["field_id"] == field_def["field_id"]]
                        if options:
                            selected_option = random.choice(options)
                            values.append({
                                "value_id": value_id,
                                "task_id": task["task_id"],
                                "field_id": field_def["field_id"],
                                "text_value": None,
                                "number_value": None,
                                "date_value": None,
                                "option_id": selected_option["option_id"],
                            })
                    
                    elif field_def["field_type"] == "number":
                        values.append({
                            "value_id": value_id,
                            "task_id": task["task_id"],
                            "field_id": field_def["field_id"],
                            "text_value": None,
                            "number_value": random.choice([1, 2, 3, 5, 8, 13]),
                            "date_value": None,
                            "option_id": None,
                        })
                    
                    elif field_def["field_type"] == "text":
                        values.append({
                            "value_id": value_id,
                            "task_id": task["task_id"],
                            "field_id": field_def["field_id"],
                            "text_value": f"Sprint {random.randint(1, 20)}",
                            "number_value": None,
                            "date_value": None,
                            "option_id": None,
                        })
        
        return values