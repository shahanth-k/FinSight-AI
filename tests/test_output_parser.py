"""Unit-style tests for the FinSight AI structured response parser.

Run with: python -m unittest discover -s tests
"""

import unittest

from modules.output_parser import (
    ResponseParseError,
    parse_analysis_response,
    _empty_result,
)


class ParseAnalysisResponseTests(unittest.TestCase):
    def test_parses_clean_json(self):
        raw = (
            '{'
            '"summary": "Test summary.", '
            '"sentiment": "Bullish", '
            '"reasoning": "Because revenue grew.", '
            '"jargon": [{"term": "EBITDA", "explanation": "Earnings before..."}], '
            '"takeaways": {"positives": ["Revenue up"], "risks": ["FX risk"]}'
            '}'
        )
        result = parse_analysis_response(raw)
        self.assertEqual(result["summary"], "Test summary.")
        self.assertEqual(result["sentiment"], "Bullish")
        self.assertEqual(result["reasoning"], "Because revenue grew.")
        self.assertEqual(len(result["jargon"]), 1)
        self.assertEqual(result["jargon"][0]["term"], "EBITDA")
        self.assertEqual(result["takeaways"]["positives"], ["Revenue up"])
        self.assertEqual(result["takeaways"]["risks"], ["FX risk"])

    def test_tolerates_markdown_fences(self):
        raw = (
            "```json\n"
            '{"summary": "S", "sentiment": "bearish", "reasoning": "R", '
            '"jargon": [], "takeaways": {"positives": [], "risks": []}}\n'
            "```"
        )
        result = parse_analysis_response(raw)
        self.assertEqual(result["sentiment"], "Bearish")
        self.assertEqual(result["summary"], "S")

    def test_extracts_json_from_prose(self):
        raw = (
            "Here is the analysis you asked for:\n"
            '{"summary":"X","sentiment":"neutral","reasoning":"Y",'
            '"jargon":[],"takeaways":{"positives":[],"risks":[]}}\n'
            "End of response."
        )
        result = parse_analysis_response(raw)
        self.assertEqual(result["summary"], "X")
        self.assertEqual(result["sentiment"], "Neutral")

    def test_normalises_unknown_sentiment(self):
        raw = (
            '{"summary":"","sentiment":"unknown","reasoning":"",'
            '"jargon":[],"takeaways":{}}'
        )
        result = parse_analysis_response(raw)
        self.assertEqual(result["sentiment"], "Neutral")

    def test_rejects_empty_input(self):
        with self.assertRaises(ResponseParseError):
            parse_analysis_response("")

    def test_rejects_no_json(self):
        with self.assertRaises(ResponseParseError):
            parse_analysis_response("nothing parseable here")

    def test_drops_malformed_jargon_entries(self):
        raw = (
            '{"summary":"","sentiment":"Neutral","reasoning":"",'
            '"jargon":[{"term":"OK","explanation":"fine"},'
            '{"term":"","explanation":"bad term, no term so dropped"},'
            '"raw string entry"],'
            '"takeaways":{}}'
        )
        result = parse_analysis_response(raw)
        # Entry with empty term is dropped; string entries kept with fallback explanation.
        # {"term":"OK","explanation":"fine"} → kept
        # {"term":"","explanation":"bad"} → dropped (no term)
        # "raw string entry" → kept as {"term": "raw string entry", "explanation": "No explanation provided."}
        self.assertEqual(len(result["jargon"]), 2)
        self.assertEqual(result["jargon"][0]["term"], "OK")
        self.assertEqual(result["jargon"][0]["explanation"], "fine")
        self.assertEqual(result["jargon"][1]["term"], "raw string entry")
        self.assertEqual(result["jargon"][1]["explanation"], "No explanation provided.")

    def test_empty_result_shape(self):
        empty = _empty_result()
        self.assertEqual(empty["sentiment"], "Neutral")
        self.assertEqual(empty["jargon"], [])
        self.assertEqual(empty["takeaways"], {"positives": [], "risks": []})


if __name__ == "__main__":
    unittest.main()
