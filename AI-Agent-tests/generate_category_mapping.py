#!/usr/bin/env python3
"""
Generate a CSV key-value mapping for all 3,822 generated tests.

Output columns:
  id                – test identifier (YAML id field / filename without .yml)
  agentic_category  – internal category name from the YAML (AGENTIC_*)
  asi_category      – OWASP Top 10 for Agentic Applications 2026 (ASI01-ASI10)

Usage:
  python3 generate_category_mapping.py
  → writes AI-Agent-tests/test_category_mapping.csv
"""

import csv
import os
import re

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
GENERATED_DIR = os.path.join(SCRIPT_DIR, "generated_tests")
OUTPUT_FILE   = os.path.join(SCRIPT_DIR, "test_category_mapping.csv")

# ─── ASI prefix → displayName  ────────────────────────────────────────────
# Each tuple: (list_of_filename_prefixes, asi_display_name)
ASI_MAP = [
    (
        [
            "SECURITY_AGENT_BEHAVIOR_HIJACK_AND_GOAL_MANIPULATION_",
            "SECURITY_PROMPT_INJECTION_",
            "SECURITY_INDIRECT_PROMPT_INJECTION_",
            "SECURITY_SYSTEM_PROMPT_OVERRIDE_",
            "SECURITY_JAILBREAK_",
            "SECURITY_MANIPULATION_",
            "SECURITY_CONTEXT_LEAKAGE_",
            "SECURITY_SENSITIVE_INFORMATION_DISCLOSURE_",
            "SECURITY_PHISHING_",
            "SAFETY_ILLEGAL_ACTIVITIES_",
            "SAFETY_PII_",
            "SAFETY_PRIVACY_VIOLATION_",
            "SAFETY_PROFANITY_",
            "SAFETY_HARMFUL_CONTENT_",
            "BUSINESS_ALIGNMENT_COMPETITOR_CHECK_",
            "BUSINESS_ALIGNMENT_INTENTIONAL_MISUSE_",
            "BUSINESS_ALIGNMENT_LEGALLY_BINDING_",
            "BUSINESS_ALIGNMENT_OFF_TOPIC_",
            "HALLUCINATION_AND_TRUSTWORTHINESS_PARANOID_PROTECTION_",
        ],
        "ASI01 - Agent Goal Hijacking",
    ),
    (
        [
            "SECURITY_TOOL_MISUSE_AND_EXPLOITATION_",
            "SECURITY_INSECURE_PLUGIN_USE_",
            "SECURITY_MALICIOUS_RESOURCE_FETCHING_",
            "SECURITY_DATA_EXFILTRATION_",
            "SECURITY_TOOL_DISCOVERY_",
            "HALLUCINATION_AND_TRUSTWORTHINESS_URL_CHECK_",
        ],
        "ASI02 - Tool Misuse and Exploitation",
    ),
    (
        [
            "SECURITY_IDENTITY_SPOOFING_",
            "SECURITY_REPUDIATION_UNTRACEABILITY_",
            "SECURITY_EXCESSIVE_AGENCY_",
        ],
        "ASI03 - Identity and Privilege Abuse",
    ),
    (
        [
            "SECURITY_AGENTIC_SUPPLY_CHAIN_VULNERABILITIES_",
            "SECURITY_TRAINING_DATA_POISONING_",
            "SECURITY_MODEL_THEFT_",
        ],
        "ASI04 - Agentic Supply Chain Vulnerabilities",
    ),
    (
        [
            "SECURITY_UNEXPECTED_CODE_EXECUTION_RCE_",
            "SECURITY_CODE_EXECUTION_",
            "SECURITY_WEB_INJECTION_",
            "SECURITY_XSS_",
        ],
        "ASI05 - Unexpected Code Execution",
    ),
    (
        [
            "SECURITY_CONTEXT_POISONING_",
            "SECURITY_RAG_POISONING_",
            "SECURITY_CROSS_SESSION_LEAKS_",
            "HALLUCINATION_AND_TRUSTWORTHINESS_RAG_PRECISION_",
        ],
        "ASI06 - Memory and Context Poisoning",
    ),
    (
        ["SECURITY_INSECURE_INTER_AGENT_COMMUNICATION_"],
        "ASI07 - Insecure Inter-Agent Communication",
    ),
    (
        [
            "HALLUCINATION_AND_TRUSTWORTHINESS_HALLUCINATION_PROPAGATION_",
            "SECURITY_OVERRELIANCE_",
            "SECURITY_MODEL_DENIAL_OF_SERVICE_",
            "HALLUCINATION_AND_TRUSTWORTHINESS_Q_A_",
        ],
        "ASI08 - Cascading Failures",
    ),
    (
        [
            "BUSINESS_ALIGNMENT_HUMAN_AGENT_TRUST_EXPLOITATION_",
            "BUSINESS_ALIGNMENT_OVERWHELMING_HUMAN_IN_THE_LOOP_",
        ],
        "ASI09 - Human-Agent Trust Exploitation",
    ),
    (
        [
            "BUSINESS_ALIGNMENT_ROGUE_AGENTS_",
            "BUSINESS_ALIGNMENT_MISALIGNED_AND_DECEPTIVE_BEHAVIORS_",
            "SAFETY_BIAS_",
        ],
        "ASI10 - Rogue Agents",
    ),
]

# Pre-built flat list for fast lookup: [(prefix, asi_display), ...]
# Sorted longest-first so more-specific prefixes match before shorter ones
_FLAT_ASI = sorted(
    [(prefix, asi) for prefixes, asi in ASI_MAP for prefix in prefixes],
    key=lambda x: -len(x[0]),
)

# Regex to pull category.name out of a YAML file
_CAT_NAME_RE = re.compile(r"  category:\s*\n    name:\s*(\S+)")


def get_asi(filename_no_ext: str) -> str:
    for prefix, asi in _FLAT_ASI:
        if filename_no_ext.startswith(prefix):
            return asi
    return "UNKNOWN"


def get_agentic_category(yaml_content: str) -> str:
    m = _CAT_NAME_RE.search(yaml_content)
    return m.group(1) if m else "UNKNOWN"


def main():
    files = sorted(f for f in os.listdir(GENERATED_DIR) if f.endswith(".yml"))

    rows = []
    unknowns = []

    for fname in files:
        test_id = fname[:-4]  # strip .yml
        fpath   = os.path.join(GENERATED_DIR, fname)

        with open(fpath, encoding="utf-8") as f:
            content = f.read()

        agentic_cat = get_agentic_category(content)
        asi_cat     = get_asi(test_id)

        if agentic_cat == "UNKNOWN" or asi_cat == "UNKNOWN":
            unknowns.append((test_id, agentic_cat, asi_cat))

        rows.append((test_id, agentic_cat, asi_cat))

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "agentic_category", "asi_category"])
        writer.writerows(rows)

    print(f"Mapped {len(rows)} tests  →  {os.path.basename(OUTPUT_FILE)}")

    # Summary by ASI category
    from collections import Counter
    asi_counts = Counter(r[2] for r in rows)
    print("\nDistribution:")
    for asi, count in sorted(asi_counts.items()):
        print(f"  {asi:<45}  {count:>5} tests")

    if unknowns:
        print(f"\nWARNING – {len(unknowns)} unmatched entries:")
        for r in unknowns:
            print(f"  {r}")


if __name__ == "__main__":
    main()
