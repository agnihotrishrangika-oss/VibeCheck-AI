"""
Official YouTube Community Guidelines Policy Rules.
Sources:
- Hate Speech Policy: https://support.google.com/youtube/answer/2801939
- Harassment & Cyberbullying Policy: https://support.google.com/youtube/answer/2802268
- Violent Criminal Organizations & Threats Policy: https://support.google.com/youtube/answer/2801924
"""

from app.policy_engine.schemas import PolicyRule

YOUTUBE_RULES_V1 = {
    "hate_speech": PolicyRule(
        rule_id="YT-HATE-01",
        platform="YouTube",
        policy_category="Hate Speech",
        rule_description=(
            "Content that promotes violence or incites hatred against individuals or groups "
            "based on protected attributes (e.g., race, religion, caste, sexual orientation, disability)."
        ),
        protected_characteristics=[
            "Age", "Caste", "Disability", "Ethnicity", "Gender identity and expression",
            "Nationality", "Race", "Immigration status", "Religion", "Sex/Gender",
            "Sexual orientation", "Victims of a major violent event"
        ],
        context_exceptions=[
            "Educational, Documentary, Scientific, or Artistic (EDSA) context",
            "Direct counter-speech and quoting for condemnation",
            "Neutral news reporting or historical documentation"
        ],
        severity="High",
        recommended_action=(
            "Potential policy issue: Flag for human moderator review. "
            "If sustained, content removal and channel Community Guidelines strike (3-strike system)."
        ),
        source_url="https://support.google.com/youtube/answer/2801939",
        source_title="Hate speech policy - YouTube Help",
        retrieved_date="2026-05-15",
        policy_version="v1.2-standard",
        violation_threshold=0.68,
        review_threshold=0.48,
    ),
    "harassment": PolicyRule(
        rule_id="YT-HARASS-01",
        platform="YouTube",
        policy_category="Harassment & Cyberbullying",
        rule_description=(
            "Content that targets an individual with prolonged or malicious insults, "
            "severe derogatory slurs, non-consensual sexualization, or sustained humiliation."
        ),
        protected_characteristics=[
            "Individual persons", "Minors", "Protected classes under hate speech policy"
        ],
        context_exceptions=[
            "Lighthearted comedy and satire",
            "Public political debate regarding notable public figures (unless crossing into dehumanization or doxxing)",
            "Mutual playful banter"
        ],
        severity="Medium-High",
        recommended_action=(
            "Potential policy issue: Flag for contextual review. If targeted harassment is confirmed, "
            "video takedown and possible strikes or creator warning."
        ),
        source_url="https://support.google.com/youtube/answer/2802268",
        source_title="Harassment & cyberbullying policy - YouTube Help",
        retrieved_date="2026-05-15",
        policy_version="v1.2-standard",
        violation_threshold=0.65,
        review_threshold=0.45,
    ),
    "threat": PolicyRule(
        rule_id="YT-THREAT-01",
        platform="YouTube",
        policy_category="Violent Threats",
        rule_description=(
            "Content containing specific threats to inflict serious physical harm on a specific person or defined group."
        ),
        protected_characteristics=["All individuals and groups"],
        context_exceptions=["None for credible imminent threats"],
        severity="Critical",
        recommended_action="Immediate content removal, severe strike, law enforcement referral if imminent.",
        source_url="https://support.google.com/youtube/answer/2801924",
        source_title="Violent criminal organizations and threats policy - YouTube Help",
        retrieved_date="2026-05-15",
        policy_version="v1.2-standard",
        violation_threshold=0.60,
        review_threshold=0.40,
    ),
}

# Version 2.0 (Strict / Heightened Civic & Localized Safety Policy - for Experiment 2)
YOUTUBE_RULES_V2 = {
    "hate_speech": PolicyRule(
        rule_id="YT-HATE-02-STRICT",
        platform="YouTube",
        policy_category="Hate Speech (Heightened Monitoring)",
        rule_description=(
            "Heightened standard: Content with derogatory slurs or veiled communal hatred "
            "evaluated with lower tolerance during high-sensitivity events."
        ),
        protected_characteristics=YOUTUBE_RULES_V1["hate_speech"].protected_characteristics,
        context_exceptions=["Verified journalistic media credentials required for EDSA exemptions"],
        severity="High",
        recommended_action="Urgent human review queue; proactive reach dampening pending verification.",
        source_url="https://support.google.com/youtube/answer/2801939",
        source_title="Hate speech policy - YouTube Help (Civic Update)",
        retrieved_date="2026-09-01",
        policy_version="v2.0-strict",
        violation_threshold=0.52,  # Stricter threshold
        review_threshold=0.35,
    ),
    "harassment": PolicyRule(
        rule_id="YT-HARASS-02-STRICT",
        platform="YouTube",
        policy_category="Harassment & Cyberbullying (Heightened Monitoring)",
        rule_description=(
            "Heightened standard: Uncivil insults directed at individuals in regional / code-switched languages "
            "subject to immediate restriction."
        ),
        protected_characteristics=YOUTUBE_RULES_V1["harassment"].protected_characteristics,
        context_exceptions=["Explicit creator consent documentation"],
        severity="High",
        recommended_action="Demote in recommendations, require creator review, restrict comments.",
        source_url="https://support.google.com/youtube/answer/2802268",
        source_title="Harassment & cyberbullying policy - YouTube Help (Civic Update)",
        retrieved_date="2026-09-01",
        policy_version="v2.0-strict",
        violation_threshold=0.50,  # Stricter threshold
        review_threshold=0.32,
    ),
    "threat": PolicyRule(
        rule_id="YT-THREAT-02-STRICT",
        platform="YouTube",
        policy_category="Violent Threats",
        rule_description="Zero tolerance for violent threats or intimidation.",
        protected_characteristics=["All individuals and groups"],
        context_exceptions=["None"],
        severity="Critical",
        recommended_action="Immediate takedown and channel suspension.",
        source_url="https://support.google.com/youtube/answer/2801924",
        source_title="Violent criminal organizations and threats policy - YouTube Help",
        retrieved_date="2026-09-01",
        policy_version="v2.0-strict",
        violation_threshold=0.45,
        review_threshold=0.25,
    ),
}
