from django.db.models import Sum
from .models import Response, Result, Field

def calculate_result(session):
    """
    Calculate total points per field for a given assessment session,
    determine the suggested field, and save the result.
    """
    # Aggregate scores by field
    scores = (
        Response.objects.filter(session=session)
        .values("field")
        .annotate(total=Sum("points"))
    )

    score_map = {row["field"]: row["total"] for row in scores}

    if not score_map:
        # Handle case: no responses found
        return None, {}

    # Pick field with maximum score
    suggested_field = max(score_map, key=score_map.get)

    # If result already exists, update it, else create new
    result, created = Result.objects.update_or_create(
        session=session,
        defaults={
            "suggested_field": suggested_field,
            "scores": score_map,
        },
    )

    return suggested_field, score_map
