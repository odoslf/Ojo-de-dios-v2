"""Prompt template registry for local AI JSON tasks."""

from app.core.errors import ContractError

PROMPT_INTENT_INTERPRETER = "intent_interpreter"
PROMPT_PLANNER = "planner"
PROMPT_PARAMETER_FILLER = "parameter_filler"
PROMPT_EVIDENCE_ANALYZER = "evidence_analyzer"
PROMPT_REPORT_WRITER = "report_writer"
PROMPT_MODULE_EXPLAINER = "module_explainer"

PROMPT_TEMPLATES = {
    PROMPT_INTENT_INTERPRETER: (
        "Interpret the user intent for a controlled local workflow. "
        "Respond only with valid JSON using intent, target, confidence, and user_explanation fields."
    ),
    PROMPT_PLANNER: (
        "Create a conservative dry-run plan from provided context only. "
        "Do not invent unavailable actions. Respond only with valid JSON matching the AIPlanResponse schema."
    ),
    PROMPT_PARAMETER_FILLER: (
        "Review provided parameters and identify missing values. "
        "Respond only with valid JSON and do not fabricate unavailable values."
    ),
    PROMPT_EVIDENCE_ANALYZER: (
        "Summarize provided evidence metadata without adding unsupported claims. "
        "Respond only with valid JSON."
    ),
    PROMPT_REPORT_WRITER: (
        "Draft a concise user-facing explanation from provided structured context. "
        "Respond only with valid JSON."
    ),
    PROMPT_MODULE_EXPLAINER: (
        "Explain provided module metadata at a high level without operational instructions. "
        "Respond only with valid JSON."
    ),
}


def get_prompt_template(prompt_id: str) -> str:
    """Return a prompt template by id."""
    try:
        return PROMPT_TEMPLATES[prompt_id]
    except KeyError as error:
        raise ContractError("Unknown AI prompt id.") from error


def list_prompt_ids() -> list[str]:
    """Return registered prompt ids in deterministic order."""
    return sorted(PROMPT_TEMPLATES)
