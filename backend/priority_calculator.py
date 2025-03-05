def calculate_priority(days_left, assigned_by):
    days_score = max(0, 34 - (days_left * 1.5))
    assigned_score = assigned_by
    return min(100, days_score + assigned_score)
