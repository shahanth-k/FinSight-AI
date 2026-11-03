"""__init__ for the FinSight AI modules package.

Imports are kept lazy so lightweight consumers (e.g. unit tests for the
response parser) do not need the google-generativeai SDK installed.
"""

__all__ = [
    "GeminiAPIError",
    "GeminiConfigError",
    "ResponseParseError",
    "SYSTEM_INSTRUCTION",
    "build_analysis_prompt",
    "generate_analysis",
    "parse_analysis_response",
]


def __getattr__(name):
    if name in ("GeminiAPIError", "GeminiConfigError", "generate_analysis"):
        from . import genai_client
        return getattr(genai_client, name)
    if name in ("ResponseParseError", "parse_analysis_response"):
        from . import output_parser
        return getattr(output_parser, name)
    if name in ("SYSTEM_INSTRUCTION", "build_analysis_prompt"):
        from . import prompt_templates
        return getattr(prompt_templates, name)
    raise AttributeError(f"module 'modules' has no attribute {name!r}")