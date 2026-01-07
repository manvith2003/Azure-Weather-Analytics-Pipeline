"""Date and time generation utilities."""
from datetime import datetime, timedelta, date
import random
import numpy as np
from typing import Optional


def random_date_between(start_date: date, end_date: date) -> date:
    """Generate a random date between start and end dates."""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


def random_datetime_between(start_dt: datetime, end_dt: datetime) -> datetime:
    """Generate a random datetime between start and end."""
    delta = end_dt - start_dt
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_dt + timedelta(seconds=random_seconds)


def workday_datetime(start_dt: datetime, end_dt: datetime) -> datetime:
    """Generate a random datetime during work hours (9 AM - 6 PM, Mon-Fri)."""
    while True:
        dt = random_datetime_between(start_dt, end_dt)
        
        # Skip weekends
        if dt.weekday() >= 5:
            continue
            
        # Adjust to work hours (9 AM - 6 PM)
        hour = random.randint(9, 17)
        minute = random.randint(0, 59)
        
        dt = dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if start_dt <= dt <= end_dt:
            return dt


def workday_bias_datetime(start_dt: datetime, end_dt: datetime) -> datetime:
    """Generate datetime with bias toward Mon-Wed."""
    while True:
        dt = random_datetime_between(start_dt, end_dt)
        
        # Higher probability for Mon-Wed (0-2)
        weekday = dt.weekday()
        if weekday >= 5:  # Skip weekends
            continue
            
        # Accept with different probabilities
        if weekday <= 2:  # Mon-Wed
            accept_prob = 0.8
        elif weekday == 3:  # Thu
            accept_prob = 0.5
        else:  # Fri
            accept_prob = 0.3
            
        if random.random() < accept_prob:
            # Set to work hours
            hour = random.randint(9, 17)
            minute = random.randint(0, 59)
            dt = dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            if start_dt <= dt <= end_dt:
                return dt


def avoid_weekend_date(target_date: date) -> date:
    """Adjust date to avoid weekends (85% of the time)."""
    if random.random() > 0.85:
        return target_date  # Allow some weekend dates
        
    # If weekend, move to Friday or Monday
    if target_date.weekday() == 5:  # Saturday
        return target_date + timedelta(days=2)  # Move to Monday
    elif target_date.weekday() == 6:  # Sunday
        return target_date + timedelta(days=1)  # Move to Monday
        
    return target_date


def generate_due_date(created_at: datetime, base_date: date) -> Optional[date]:
    """
    Generate realistic due date based on research distributions.
    
    Distribution:
    - 25% within 1 week
    - 40% within 1 month  
    - 20% 1-3 months out
    - 10% no due date
    - 5% overdue (before creation)
    """
    rand = random.random()
    
    # 10% no due date
    if rand < 0.10:
        return None
        
    # 5% overdue
    if rand < 0.15:
        days_overdue = random.randint(1, 30)
        due = created_at.date() - timedelta(days=days_overdue)
        return avoid_weekend_date(due)
        
    # 25% within 1 week
    if rand < 0.40:
        days_ahead = random.randint(1, 7)
        due = created_at.date() + timedelta(days=days_ahead)
        return avoid_weekend_date(due)
        
    # 40% within 1 month
    if rand < 0.80:
        days_ahead = random.randint(8, 30)
        due = created_at.date() + timedelta(days=days_ahead)
        return avoid_weekend_date(due)
        
    # 20% 1-3 months out
    days_ahead = random.randint(31, 90)
    due = created_at.date() + timedelta(days=days_ahead)
    return avoid_weekend_date(due)


def generate_completion_time(created_at: datetime, now: datetime) -> Optional[datetime]:
    """
    Generate completion timestamp using log-normal distribution.
    
    Based on cycle time benchmarks: most tasks complete in 1-14 days.
    """
    # Log-normal distribution for cycle time (mean=5 days, std=3 days)
    mean_days = 5
    std_days = 3
    
    # Convert to log-normal parameters
    mu = np.log(mean_days**2 / np.sqrt(mean_days**2 + std_days**2))
    sigma = np.sqrt(np.log(1 + (std_days**2 / mean_days**2)))
    
    days_to_complete = np.random.lognormal(mu, sigma)
    days_to_complete = min(days_to_complete, 30)  # Cap at 30 days
    
    completed_at = created_at + timedelta(days=days_to_complete)
    
    # Must be before now
    if completed_at > now:
        return None
        
    # Set to work hours
    completed_at = completed_at.replace(
        hour=random.randint(9, 17),
        minute=random.randint(0, 59),
        second=0,
        microsecond=0
    )
    
    return completed_at


def sprint_boundary_date(base_date: date, sprint_length_weeks: int = 2) -> date:
    """Generate date aligned to sprint boundaries."""
    # Find next sprint boundary
    days_since_start = (base_date - date(2024, 1, 1)).days
    sprint_length_days = sprint_length_weeks * 7
    
    days_into_sprint = days_since_start % sprint_length_days
    days_to_boundary = sprint_length_days - days_into_sprint
    
    return base_date + timedelta(days=days_to_boundary)