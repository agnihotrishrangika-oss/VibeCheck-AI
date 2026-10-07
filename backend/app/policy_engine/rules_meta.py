"""
Official Meta / Instagram Community Standards Policy Rules.
Sources:
- Hate Speech (Standard 13): https://transparency.meta.com/policies/community-standards/hate-speech/
- Bullying and Harassment (Standard 14): https://transparency.meta.com/policies/community-standards/bullying-harassment/
- Violence and Incitement (Standard 1): https://transparency.meta.com/policies/community-standards/violence-incitement/
"""

from app.policy_engine.schemas import PolicyRule

META_RULES_V1 = {
    "hate_speech": PolicyRule(
        rule_id="META-HATE-01",
        platform="Instagram / Meta",
        policy_category="Hate Speech (Standard 13)",
        rule_description=(
            "Direct attacks against people based on protected characteristics categorized across 3 tiers "
            "(Tier 1: violent/dehumanizing speech, animal/disease comparisons; Tier 2: statements of contempt/disgust; "
            "Tier 3: calls for exclusion or segregation)."
        ),
        protected_characteristics=[
            "Race", "Ethnicity", "National origin", "Disability", "Religious affiliation",
            "Caste", "Sexual orientation", "Sex", "Gender identity", "Serious disease"
        ],
        context_exceptions=[
            "Shared with clear condemning intent or raising awareness",
            "Humorous intent / playful banter between mutual connections",
            "Self-referential or reclaimed terms by protected groups"
        ],
        severity="High",
        recommended_action=(
            "Potential policy violation: Content removal under Meta Community Standard 13. "
            "Temporary feature restriction on creator account and reach throttling."
        ),
        source_url="https://transparency.meta.com/policies/community-standards/hate-speech/",
        source_title="Meta Community Standards: Hate Speech",
        retrieved_date="2026-05-15",
        policy_version="v2026.1-standard",
        violation_threshold=0.66,
        review_threshold=0.46,
    ),
    "harassment": PolicyRule(
        rule_id="META-BULLY-01",
        platform="Instagram / Meta",
        policy_category="Bullying and Harassment (Standard 14)",
        rule_description=(
            "Abusive attacks targeting individuals. Meta explicitly provides heightened protections for "
            "private individuals compared to public figures, prohibiting unwanted contact, severe derogatory claims, "
            "and coordinated brigading."
        ),
        protected_characteristics=[
            "Private individuals", "Minors", "Individuals targeted by mass harassment"
        ],
        context_exceptions=[
            "Discourse around public figures (unless severe sexualized bullying or doxxing)",
            "Mutual friendly banter between consenting accounts",
            "Self-defense commentary"
        ],
        severity="Medium-High",
        recommended_action=(
            "Potential policy issue: Hide or remove reel, prompt warning to commenter, "
            "offer anti-bullying tools to targeted account."
        ),
        source_url="https://transparency.meta.com/policies/community-standards/bullying-harassment/",
        source_title="Meta Community Standards: Bullying and Harassment",
        retrieved_date="2026-05-15",
        policy_version="v2026.1-standard",
        violation_threshold=0.62,
        review_threshold=0.42,
    ),
    "threat": PolicyRule(
        rule_id="META-VIOL-01",
        platform="Instagram / Meta",
        policy_category="Violence and Incitement (Standard 1)",
        rule_description=(
            "Statements of intent to commit violence or calls for physical harm against individuals or groups."
        ),
        protected_characteristics=["All persons and community members"],
        context_exceptions=["Hyperbolic colloquialisms with clear benign intent"],
        severity="Critical",
        recommended_action="Immediate content deletion, account safety flag, law enforcement referral if credible threat.",
        source_url="https://transparency.meta.com/policies/community-standards/violence-incitement/",
        source_title="Meta Community Standards: Violence and Incitement",
        retrieved_date="2026-05-15",
        policy_version="v2026.1-standard",
        violation_threshold=0.58,
        review_threshold=0.38,
    ),
}

# Version 2.0 (Strict / Heightened Regional Safety Policy - for Experiment 2)
META_RULES_V2 = {
    "hate_speech": PolicyRule(
        rule_id="META-HATE-02-STRICT",
        platform="Instagram / Meta",
        policy_category="Hate Speech (Heightened Regional Standard)",
        rule_description=(
            "Zero tolerance for regional code-mixed slurs and targeted caste/communal dog-whistles."
        ),
        protected_characteristics=META_RULES_V1["hate_speech"].protected_characteristics,
        context_exceptions=["Strict journalistic verification required"],
        severity="Critical",
        recommended_action="Immediate automatic downranking and expedited human audit queue.",
        source_url="https://transparency.meta.com/policies/community-standards/hate-speech/",
        source_title="Meta Community Standards: Hate Speech (Regional Safety Update)",
        retrieved_date="2026-09-01",
        policy_version="v2026.2-strict",
        violation_threshold=0.50,  # Stricter threshold
        review_threshold=0.30,
    ),
    "harassment": PolicyRule(
        rule_id="META-BULLY-02-STRICT",
        platform="Instagram / Meta",
        policy_category="Bullying and Harassment (Heightened Regional Standard)",
        rule_description=(
            "Strict anti-abuse enforcement: Deploys proactive detection for Hinglish insults and abusive targeting."
        ),
        protected_characteristics=META_RULES_V1["harassment"].protected_characteristics,
        context_exceptions=["None for unverified accounts"],
        severity="High",
        recommended_action="Prompt creator for content review, hide from explore page.",
        source_url="https://transparency.meta.com/policies/community-standards/bullying-harassment/",
        source_title="Meta Community Standards: Bullying and Harassment (Regional Safety Update)",
        retrieved_date="2026-09-01",
        policy_version="v2026.2-strict",
        violation_threshold=0.48,  # Stricter threshold
        review_threshold=0.28,
    ),
    "threat": PolicyRule(
        rule_id="META-VIOL-02-STRICT",
        platform="Instagram / Meta",
        policy_category="Violence and Incitement",
        rule_description="Zero tolerance for violent statements or intimidation.",
        protected_characteristics=["All persons and community members"],
        context_exceptions=["None"],
        severity="Critical",
        recommended_action="Immediate content deletion and account suspension.",
        source_url="https://transparency.meta.com/policies/community-standards/violence-incitement/",
        source_title="Meta Community Standards: Violence and Incitement",
        retrieved_date="2026-09-01",
        policy_version="v2026.2-strict",
        violation_threshold=0.42,
        review_threshold=0.22,
    ),
}
