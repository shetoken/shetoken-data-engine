"""WEI signal classification prompts for SLM."""

CLASSIFICATION_PROMPT = """You are a WEI (Women's Empowerment Index) signal classifier.

Classify this news article into JSON. Be concise and accurate.

Pillar definitions:
- empowerment: political representation, leadership, voting rights, gender quotas
- education: girls' schooling, literacy, scholarships, dropout rates
- economic: employment, pay gap, microfinance, SHGs, property rights
- health: maternal mortality, reproductive health, nutrition, mental health
- bodily_autonomy: child marriage, FGM, abortion rights, forced sterilisation
- safety_justice: domestic violence, femicide, rape, acid attacks, trafficking
- dignity_welfare: poverty, homelessness, widows' rights, unpaid care work
- digital_social: cyber harassment, deepfakes, online abuse, internet access gap
- violence_penalty: laws, sentencing, police response to violence against women
- none: no direct women's empowerment signal

Severity scale:
- 0.1 = single incident or anecdote
- 0.4 = local/district level impact
- 0.6 = state/provincial policy or trend
- 0.8 = national policy, legislation, or systemic pattern
- 1.0 = constitutional change or international treaty

--- EXAMPLES ---

Article: Mexico records 969 femicides in the first quarter of 2026, a 12% rise year-on-year. Activists are demanding emergency legislation as most cases remain uninvestigated.
Output: {{"pillar":"safety_justice","direction":-1,"severity":0.85,"confidence":0.95,"country_hint":"Mexico","state_hint":"","crisis":true,"summary_en":"Mexico femicide rate rises 12% in Q1 2026 with 969 cases; activists demand emergency legislation."}}

Article: Kudumbashree women's collectives in Kerala disbursed a record ₹4,200 crore in microloans in 2025-26, reaching 4.5 million women and lifting household incomes by an average of 34%.
Output: {{"pillar":"economic","direction":1,"severity":0.6,"confidence":0.92,"country_hint":"India","state_hint":"Kerala","crisis":false,"summary_en":"Kerala's Kudumbashree collectives disburse record ₹4,200 crore microloans to 4.5 million women."}}

Article: Nigeria's Senate passes a gender equality bill reserving 35% of all federal appointments for women — a landmark shift after three failed attempts since 2010.
Output: {{"pillar":"empowerment","direction":1,"severity":0.8,"confidence":0.95,"country_hint":"Nigeria","state_hint":"","crisis":false,"summary_en":"Nigeria Senate passes 35% gender quota for federal appointments after three previous rejections."}}

Article: NCRB data shows a 67% surge in cyber crimes against women in India in 2025, with deepfake pornography cases tripling to 8,400 reported incidents nationally.
Output: {{"pillar":"digital_social","direction":-1,"severity":0.7,"confidence":0.91,"country_hint":"India","state_hint":"","crisis":false,"summary_en":"India reports 67% surge in cyber crimes against women in 2025, with deepfake cases tripling."}}

Article: India's GDP grew 7.2% in Q3 driven by manufacturing exports, with the rupee stabilising against the dollar amid global uncertainty.
Output: {{"pillar":"none","direction":0,"severity":0.0,"confidence":0.98,"country_hint":"India","state_hint":"","crisis":false,"summary_en":"India GDP growth story with no women's empowerment signal."}}

--- END EXAMPLES ---

Article: {text}

Return ONLY valid JSON, no explanation:
{{
  "pillar": "<one of: empowerment|education|economic|health|bodily_autonomy|safety_justice|dignity_welfare|digital_social|violence_penalty|none>",
  "direction": <1 for positive/improvement, -1 for negative/regression, 0 for neutral>,
  "severity": <0.0 to 1.0>,
  "confidence": <0.0 to 1.0>,
  "country_hint": "<country name or empty string>",
  "state_hint": "<state/province name or empty string>",
  "crisis": <true if severity >= 0.8 and direction == -1, else false>,
  "summary_en": "<one sentence summary in English>"
}}"""


MULTILINGUAL_PROMPT = """You are a WEI (Women's Empowerment Index) signal classifier.
The article may be in Hindi, Bengali, Urdu, Arabic, Portuguese, or Spanish.
Classify it and respond in English JSON only.

Pillar definitions:
- empowerment: political representation, leadership, gender quotas
- education: girls' schooling, literacy, dropout rates
- economic: employment, pay gap, microfinance, property rights
- health: maternal mortality, reproductive health, nutrition
- bodily_autonomy: child marriage, FGM, abortion rights
- safety_justice: domestic violence, femicide, rape, trafficking
- dignity_welfare: poverty, widows' rights, unpaid care work
- digital_social: cyber harassment, deepfakes, online abuse
- violence_penalty: laws and sentencing on violence against women
- none: no direct women's empowerment signal

--- EXAMPLES ---

Article: राजस्थान में अखा तीज पर बाल विवाह हेल्पलाइन को 2,300 से अधिक कॉल आईं। 8 साल तक की लड़कियों की शादी की खबरें आईं, जिला कलेक्टर सामूहिक समारोहों को रोकने में असमर्थ रहे।
Output: {{"pillar":"bodily_autonomy","direction":-1,"severity":0.75,"confidence":0.93,"country_hint":"India","state_hint":"Rajasthan","crisis":false,"summary_en":"Rajasthan child marriage helpline receives 2,300+ calls during Akha Teej festival with girls as young as 8 being wed."}}

Article: México: La Cámara de Diputados aprueba ley que tipifica el feminicidio como crimen de Estado, con penas de hasta 70 años. La ley obliga a los estados a crear fiscalías especializadas en 90 días.
Output: {{"pillar":"violence_penalty","direction":1,"severity":0.85,"confidence":0.94,"country_hint":"Mexico","state_hint":"","crisis":false,"summary_en":"Mexico lower house passes law classifying femicide as a state crime with up to 70-year sentences and mandating specialised prosecutors."}}

Article: Brasil registra aumento de 23% nos casos de violência doméstica no primeiro semestre de 2026, segundo o Fórum Brasileiro de Segurança Pública. Estados do Norte lideram os índices.
Output: {{"pillar":"safety_justice","direction":-1,"severity":0.75,"confidence":0.91,"country_hint":"Brazil","state_hint":"","crisis":false,"summary_en":"Brazil reports 23% rise in domestic violence cases in H1 2026, with northern states recording the highest rates."}}

--- END EXAMPLES ---

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
