"""
Scoring formula function for spending
"""

categories = ["Housing", "Transportation/Travel", "Entertainment/Hobbies/Shopping", "Health", "Travel/Vacations", "Food/Groceries", "Debt/Obligation"]

weights = { category: weight for (category, weight) in zip(categories, [0.3, 0.1, 0.1, 0.05, 0.10, 0.15, 0.20]) }

def calculate_spending_score(spending_data):
    """
    Composite score based on actual vs target percentages

    spending_data should be a dictionary. For example:
    {
        "Housing": {'actual': 32, 'target': 30, 'weight': 0.3},
        'Food / Groceries': {'actual': 14, 'target': 15, 'weight: 0.125}
    }
    """
    print("spending data", spending_data)
    total_score = 0
    total_weight = 0

    for category, val in spending_data.items():
        actual = val['actual']
        target = val['target']
        weight = weights[category]

        if target == 0:
            # If no target is set, skip this category from scoring
            # This prevents penalizing users who haven't set targets yet
            continue
        else:
            diff = max(0, actual - target)
            deviation = max(0, 1 - diff / target)
            total_score += weight * deviation # higher score better
            total_weight += weight

    # Normalize the score based on the total weight of categories with targets
    if total_weight > 0:
        final_score = (total_score / total_weight) * 100
    else:
        # If no targets are set at all, return 0
        final_score = 0

    return round(final_score)

