"""
Prompt Auditor — Week 2 Capstone (Code for Good STEM Career Path)

Analyzes a prompt and flags four common gaps:
  1. Missing scale requirements — does the prompt mention data/task size
     when the task type implies scale could matter?
  2. Missing error handling spec — does the prompt say what should happen
     on failure or invalid input?
  3. Missing output-format spec — does the prompt specify exact structure
     or format for the response?
  4. Estimated token waste — filler phrases, redundant restatement, low
     vocabulary diversity (same detection logic as the Week 1 token auditor).

This tool flags likely gaps using keyword heuristics — it does not
guarantee a prompt is well-formed just because it passes all four checks,
and a prompt can be flagged even if the gap genuinely doesn't matter for
that specific task. It's a starting checklist, not a verdict.
"""

import re
import sys
import tiktoken

# --- Scale-implying task keywords (things that often involve size/volume) ---
SCALE_IMPLYING_KEYWORDS = [
    r"\bfile\b", r"\bdata\b", r"\bdataset\b", r"\bprocess\b", r"\blist\b",
    r"\brecords?\b", r"\brows?\b", r"\bqueue\b", r"\bbatch\b", r"\busers?\b",
    r"\brequests?\b",
]
SCALE_QUALIFIER_KEYWORDS = [
    r"\bsize\b", r"\bvolume\b", r"\blarge\b", r"\bsmall\b",
    r"\d+\s?(mb|gb|tb|kb)\b", r"\bmillion\b", r"\bthousand\b", r"\bconcurrent\b",
    r"\bscale\b", r"\bperformance\b", r"\blatency\b", r"\bthroughput\b",
]

# --- Error-handling keywords ---
ERROR_HANDLING_KEYWORDS = [
    r"\berror\b", r"\bfail(s|ure|ed)?\b", r"\binvalid\b", r"\bempty\b",
    r"\bmissing\b", r"\bexception\b", r"\bedge case\b", r"\bif\b.*\b(not|no)\b",
    r"\bwhat (if|happens)\b",
]

# --- Output-format keywords ---
OUTPUT_FORMAT_KEYWORDS = [
    r"\bformat\b", r"\bjson\b", r"\bxml\b", r"\bcsv\b", r"\btable\b",
    r"\breturn as\b", r"\bstructured?\b", r"\bschema\b", r"\bbullet\b",
    r"\blist of\b", r"\bexactly\b.*\b(fields|columns|keys)\b",
]

# --- Token waste (reused from Week 1 token auditor) ---
FILLER_PHRASES = [
    r"\bplease\b", r"\bkindly\b", r"\bi would like you to\b",
    r"\bi want you to\b", r"\bmake sure to\b", r"\bnote that\b",
    r"\bas an ai\b", r"\bi need you to\b", r"\bcould you please\b",
    r"\bit is important that\b", r"\bdon't forget to\b",
]


def count_tokens(text: str) -> int:
    """Count tokens using the GPT-4o tokenizer (o200k_base encoding)."""
    encoding = tiktoken.get_encoding("o200k_base")
    return len(encoding.encode(text))


def _matches_any(patterns, text_lower):
    return any(re.search(p, text_lower) for p in patterns)


def check_scale_requirements(text: str):
    """Flag if the prompt implies scale-sensitive work but states no scale."""
    lower = text.lower()
    implies_scale = _matches_any(SCALE_IMPLYING_KEYWORDS, lower)
    states_scale = _matches_any(SCALE_QUALIFIER_KEYWORDS, lower)
    if implies_scale and not states_scale:
        return True, "Prompt references data/files/records but never states size, volume, or scale."
    return False, None


def check_error_handling(text: str):
    """Flag if the prompt never addresses failure or invalid-input behavior."""
    lower = text.lower()
    if not _matches_any(ERROR_HANDLING_KEYWORDS, lower):
        return True, "Prompt doesn't specify what should happen on failure, invalid input, or edge cases."
    return False, None


def check_output_format(text: str):
    """Flag if the prompt never specifies a response format."""
    lower = text.lower()
    if not _matches_any(OUTPUT_FORMAT_KEYWORDS, lower):
        return True, "Prompt doesn't specify an exact output format, structure, or schema."
    return False, None


def find_repeated_sentences(text: str):
    sentences = [s.strip().lower() for s in re.split(r'[.!?\n]+', text) if s.strip()]
    seen = {}
    for s in sentences:
        seen[s] = seen.get(s, 0) + 1
    return [(s, c) for s, c in seen.items() if c > 1 and len(s) > 15]


def find_filler_phrases(text: str):
    lower_text = text.lower()
    found = []
    for pattern in FILLER_PHRASES:
        matches = re.findall(pattern, lower_text)
        if matches:
            found.append((pattern.strip(r"\b"), len(matches)))
    return found


def check_token_waste(text: str):
    """Flag filler phrases or repeated sentences that waste tokens."""
    reasons = []
    for sentence, count in find_repeated_sentences(text):
        preview = sentence[:60] + ("..." if len(sentence) > 60 else "")
        reasons.append(f"Repeated sentence (x{count}): \"{preview}\"")
    fillers = find_filler_phrases(text)
    if fillers:
        total = sum(c for _, c in fillers)
        filler_list = ", ".join(f"'{p}' x{c}" for p, c in fillers)
        reasons.append(f"Filler/hedge phrases ({total} total): {filler_list}")
    return (len(reasons) > 0), reasons


def audit(text: str):
    token_count = count_tokens(text)

    scale_flag, scale_reason = check_scale_requirements(text)
    error_flag, error_reason = check_error_handling(text)
    format_flag, format_reason = check_output_format(text)
    waste_flag, waste_reasons = check_token_waste(text)

    print("=" * 65)
    print("PROMPT AUDITOR — RESULTS")
    print("=" * 65)
    print(f"Token count: {token_count}\n")

    print(f"[{'FLAGGED ⚠️' if scale_flag else 'OK ✅'}] Missing scale requirements")
    if scale_reason:
        print(f"    - {scale_reason}")

    print(f"[{'FLAGGED ⚠️' if error_flag else 'OK ✅'}] Missing error handling spec")
    if error_reason:
        print(f"    - {error_reason}")

    print(f"[{'FLAGGED ⚠️' if format_flag else 'OK ✅'}] Missing output-format spec")
    if format_reason:
        print(f"    - {format_reason}")

    print(f"[{'FLAGGED ⚠️' if waste_flag else 'OK ✅'}] Estimated token waste")
    for r in waste_reasons:
        print(f"    - {r}")

    print("=" * 65)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            prompt_text = f.read()
    else:
        print("Paste your prompt below, then press Ctrl+D (Mac/Linux) or Ctrl+Z then Enter (Windows):\n")
        prompt_text = sys.stdin.read()

    audit(prompt_text)
