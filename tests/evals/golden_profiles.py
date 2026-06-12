MONDAY_FACTS = [
    ("company.name", "monday.com", "eq"),
    ("company.stock_symbol", None, "is_not_none"), # has stock symbol
    ("company.website", ["https://monday.com/", "https://www.monday.com/"], "eq_any"),
]

ZAPIER_FACTS = [
    ("company.name", "Zapier", "eq"),
    ("company.stock_symbol", None, "eq"), # no stock symbol
    ("company.website", ["https://zapier.com/", "https://www.zapier.com/"], "eq_any"),
]

STRIPE_FACTS = [
    ("company.name", "Stripe", "eq"),
    ("company.stock_symbol", None, "eq"), # no stock symbol
    ("company.website", ["https://stripe.com/", "https://www.stripe.com/"], "eq_any"),
]

HUBSPOT_FACTS = [
    ("company.name", ["HubSpot", "HubSpot, Inc."], "eq_any"),
    ("company.stock_symbol", None, "is_not_none"), # has stock symbol
    ("company.website", ["https://hubspot.com/", "https://www.hubspot.com/"], "eq_any"),
]

SALESFORCE_FACTS = [
    ("company.name", "Salesforce", "eq"),
    ("company.stock_symbol", None, "is_not_none"), # has stock symbol
    ("company.website", ["https://salesforce.com/", "https://www.salesforce.com/"], "eq_any"),
]

NOTION_FACTS = [
    ("company.name", "Notion", "eq"),
    ("company.stock_symbol", None, "eq"), # no stock symbol
    ("company.website", ["https://notion.com/", "https://www.notion.com/"], "eq_any"),
]

LINEAR_FACTS = [
    ("company.name", "Linear", "eq"),
    ("company.stock_symbol", None, "eq"), # no stock symbol
    ("company.website", ["https://linear.app/", "https://www.linear.app"], "eq_any"),
]

FIGMA_FACTS = [
    ("company.name", ["Figma", "Figma, Inc."], "eq_any"),
    ("company.stock_symbol", None, "is_not_none"), # has stock symbol
    ("company.website", ["https://figma.com/", "https://www.figma.com/"], "eq_any"),
]

INTERCOM_FACTS = [
    ("company.name", ["Intercom", "Intercom (rebranded as Fin)"], "eq_any"),
    ("company.stock_symbol", None, "eq"), # no stock symbol
    ("company.website", ["https://intercom.com/", "https://www.intercom.com/"], "eq_any"),
]

DATADOG_FACTS = [
    ("company.name", ["Datadog", "Datadog, Inc."], "eq_any"),
    ("company.stock_symbol", None, "is_not_none"), # has stock symbol
    ("company.website", ["https://datadoghq.com/", "https://www.datadoghq.com/"], "eq_any"),
]

SNOWFLAKE_FACTS = [
    ("company.name", ["Snowflake", "Snowflake Inc."], "eq_any"),
    ("company.stock_symbol", None, "is_not_none"), # has stock symbol
    ("company.website", ["https://snowflake.com/", "https://www.snowflake.com/"], "eq_any"),
]

ATLASSIAN_FACTS = [
    ("company.name", ["Atlassian", "Atlassian Corporation"], "eq_any"),
    ("company.stock_symbol", None, "is_not_none"), # has stock symbol
    ("company.website", ["https://atlassian.com/", "https://www.atlassian.com/"], "eq_any"),
]

GITHUB_FACTS = [
    ("company.name", "GitHub", "eq"),
    ("company.stock_symbol", None, "eq"), # no stock symbol
    ("company.website", ["https://github.com/", "https://www.github.com/"], "eq_any"),
]

ALL_GOLDEN_PROFILES = [
    ("monday.com", MONDAY_FACTS),
    ("zapier.com", ZAPIER_FACTS),
    ("stripe.com", STRIPE_FACTS),
    ("hubspot.com", HUBSPOT_FACTS),
    ("salesforce.com", SALESFORCE_FACTS),
    ("notion.com", NOTION_FACTS),
    ("linear.app", LINEAR_FACTS),
    ("figma.com", FIGMA_FACTS),
    ("intercom.com", INTERCOM_FACTS),
    ("datadoghq.com", DATADOG_FACTS),
    ("snowflake.com", SNOWFLAKE_FACTS),
    ("atlassian.com", ATLASSIAN_FACTS),
    ("github.com", GITHUB_FACTS),
]