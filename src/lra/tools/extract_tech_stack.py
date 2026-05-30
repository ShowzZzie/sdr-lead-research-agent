TECH_PATTERNS = {
    "googletagmanager.com": "Google Tag Manager",
    "google-analytics.com": "Google Analytics",
    "hotjar.com": "Hotjar",
    "intercom.io": "Intercom",
    "js.stripe.com": "Stripe",
    "cdn.segment.com": "Segment",
    "cdn.amplitude.com": "Amplitude",
    "cdn.mixpanel.com": "Mixpanel",
    "js.hsforms.net": "HubSpot",
    "salesforce.com": "Salesforce",
    "marketo.net": "Marketo",
    "cdn.pendo.io": "Pendo",
    "js.chilipiper.com": "Chili Piper",
    "drift.com": "Drift",
    "clearbit.com": "Clearbit",
}


EXTRACT_TECH_STACK = {
    "name": "extract_tech_stack",
    "description": "Parse the raw HTML, and look for signal on Tech Stacks used by the given website. Signals, as in patterns in HTML code clearly signaling use of a particular tech in the website. This tool should only be called after fetch_homepage has been used in this conversation.",
    "input_schema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}


def extract_tech_stack(raw_html: str) -> list[str]:
    stack = []

    for pattern in TECH_PATTERNS:
        if pattern in raw_html:
            stack.append(TECH_PATTERNS[pattern])

    return stack