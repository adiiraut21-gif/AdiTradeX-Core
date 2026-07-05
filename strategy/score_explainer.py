def explain_score(institutional_score, grade, evidence, decision_matrix):
    positive_count = len(evidence.get("positive", []))
    negative_count = len(evidence.get("negative", []))

    strongest = None
    weakest = None

    if decision_matrix:
        strongest = max(decision_matrix, key=lambda x: x.get("score", 50))
        weakest = min(decision_matrix, key=lambda x: x.get("score", 50))

    summary = (
        f"Institutional score is {institutional_score}/100 with grade {grade}. "
        f"The engine found {positive_count} positive evidence factors and "
        f"{negative_count} negative evidence factors."
    )

    if strongest:
        summary += f" Strongest component is {strongest['component']} with score {strongest['score']}."

    if weakest:
        summary += f" Weakest component is {weakest['component']} with score {weakest['score']}."

    return {
        "summary": summary,
        "positive_evidence_count": positive_count,
        "negative_evidence_count": negative_count,
        "strongest_component": strongest,
        "weakest_component": weakest
    }
