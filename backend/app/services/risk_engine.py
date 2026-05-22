def calculate_risk_score(category: str, severity: str) -> float:
    severity_scores = {
        "low": 25,
        "medium": 45,
        "high": 70,
        "critical": 90,
    }

    category_boost = {
        "traffic": 8,
        "transit": 10,
        "weather": 12,
        "crowd": 15,
        "emergency": 20,
    }

    base = severity_scores.get(severity.lower(), 30)
    boost = category_boost.get(category.lower(), 5)

    return min(base + boost, 100)