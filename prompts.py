SYSTEM_INSTRUCTIONS = (
    "You are a meticulous recruiter. Adhere to the rubric. Return STRICT JSON only."
)

# Scores should be integers 0-5 for each dimension. Overall.score is 0-100.
RUBRIC = {
    "dimensions": {
        "Alignment": {
            "definition": "How well the candidate fits the role responsibilities and domain.",
            "guidance": [
                "5: Direct experience with most responsibilities and domain",
                "3: Partial alignment; adjacent domain or less scope",
                "1: Poor alignment"
            ]
        },
        "Skills Match": {
            "definition": "Match to required/desired technical skills and tools.",
            "guidance": [
                "5: Most key skills present with evidence",
                "3: Some key skills present; gaps remain",
                "1: Few/no key skills"
            ]
        },
        "Experience Level": {
            "definition": "Years/level vs. role seniority (intern/junior/mid).",
            "guidance": [
                "5: Level exactly matches",
                "3: Slightly under/over",
                "1: Mismatch"
            ]
        },
        "Keywords": {
            "definition": "Presence of critical keywords from the JD.",
            "guidance": [
                "5: Contains most critical keywords",
                "3: Some appear",
                "1: Few appear"
            ]
        },
        "Clarity": {
            "definition": "Resume clarity, structure, and quantification of impact.",
            "guidance": [
                "5: Clear, well-structured, quantified",
                "3: Mixed",
                "1: Unclear"
            ]
        }
    }
}
