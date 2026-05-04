"""WEI signal classification prompts for SLM."""

CLASSIFICATION_PROMPT = """You are a WEI (Women's Empowerment Index) signal classifier.

Classify this news article into JSON. Be concise and accurate.

Article: {text}

Return ONLY valid JSON, no explanation:
{{
  "pillar": "<one of: empowerment|education|economic|health|bodily_autonomy|safety_justice|dignity_welfare|digital_social|violence_penalty|none>",
  "direction": <1 for positive/improvement, -1 for negative/regression, 0 for neutral>,
  "severity": <0.0 to 1.0 — 0.1=single incident, 0.5=local policy, 0.8=national policy, 1.0=constitutional change>,
  "confidence": <0.0 to 1.0>,
  "country_hint": "<country name or empty string>",
  "state_hint": "<state/province name or empty string>",
  "crisis": <true if severity >= 0.8 and direction == -1, else false>,
  "summary_en": "<one sentence summary in English>"
}}"""

MULTILINGUAL_PROMPT = """You are a WEI (Women's Empowerment Index) signal classifier.
The article may be in Hindi, Bengali, Urdu, Arabic, Portuguese, or Spanish.
Classify it and respond in English JSON only.

Article: {text}

Return ONLY valid JSON:
{{
  "pillar": "<empowerment|education|economic|health|bodily_autonomy|safety_justice|dignity_welfare|digital_social|violence_penalty|none>",
  "direction": <1 or -1 or 0>,
  "severity": <0.0 to 1.0>,
  "confidence": <0.0 to 1.0>,
  "country_hint": "<country name or empty>",
  "state_hint": "<state name or empty>",
  "crisis": <true or false>,
  "summary_en": "<one English sentence summary>"
}}"""
