# Prompt Auditor

A Python script built for Code for Good's STEM Career Path — Week 2 Capstone.

## What it does

You give it a prompt (the kind you'd send to an AI model), and it flags four common gaps:

- **Missing scale requirements** — warns if the prompt mentions files, data, or records without stating any size, volume, or performance constraint
- **Missing error handling spec** — warns if the prompt never says what should happen on failure, invalid input, or edge cases
- **Missing output-format spec** — warns if the prompt never specifies an exact response format or structure
- **Estimated token waste** — flags repeated instructions and filler/hedge phrases ("please," "kindly," "make sure to") that add tokens without adding meaning

This tool uses keyword-based heuristics, not deep understanding — a prompt can be flagged even if the gap genuinely doesn't matter for that task, and a prompt can pass all four checks without actually being well-written. Treat it as a starting checklist, not a verdict.

## Before you start

You'll need:

1. **Python installed on your computer** (version 3.8 or newer). Check by opening a terminal (Command Prompt on Windows, Terminal on Mac) and typing:

   python3 --version

   If you see a version number, you're set. If not, download Python from python.org first.

2. **This code downloaded onto your computer.** Click the green "Code" button near the top of this page, then "Download ZIP." Unzip it somewhere you can find it (like your Desktop).

## Step-by-step: how to run it

1. Open a terminal (Command Prompt on Windows, Terminal on Mac).

2. Navigate to the folder where you unzipped the code:

   cd Desktop/prompt-auditor

3. Install the one dependency this script needs (only needs to be done once):

   pip install tiktoken

4. Run the script. You have two options:

   **Option A — analyze a prompt saved in a text file:**
   Create a plain text file (like `my_prompt.txt`) containing the prompt you want to check, save it in the same folder, then run:

   python3 prompt_auditor.py my_prompt.txt

   **Option B — paste your prompt directly:**
   Run the script with no file argument:

   python3 prompt_auditor.py

   It will ask you to paste your prompt. Paste it in, then press Ctrl+D (Mac/Linux) or Ctrl+Z then Enter (Windows) to finish.

5. You'll see output like this:

   PROMPT AUDITOR — RESULTS
   =================================================================
   Token count: 38

   [FLAGGED ⚠️] Missing scale requirements
       - Prompt references data/files/records but never states size, volume, or scale.
   [FLAGGED ⚠️] Missing error handling spec
       - Prompt doesn't specify what should happen on failure, invalid input, or edge cases.
   [OK ✅] Missing output-format spec
   [FLAGGED ⚠️] Estimated token waste
       - Filler/hedge phrases (2 total): 'please' x2
   =================================================================

## How the checks work (for transparency)

- **Scale check:** looks for words implying data/volume ("file," "data," "records," "batch") without any accompanying size or scale qualifier ("large," "1TB," "million," "concurrent," etc.).
- **Error handling check:** looks for any mention of failure, invalid input, edge cases, or conditional ("if," "error," "empty," "missing").
- **Output format check:** looks for explicit format specification ("JSON," "table," "return as," "exactly N fields," etc.).
- **Token waste check:** reuses the same filler-phrase and repeated-sentence detection built for the Week 1 Token Auditor project.

## Testing notes

This tool was tested against two cases during development:
- A deliberately weak, repetitive prompt with no scale/error/format specification — correctly flagged all four issues.
- A well-specified prompt (explicit file size, error handling, and JSON output format) — correctly passed all four checks after fixing an initial bug where digit-attached size units (e.g. "1TB") weren't being detected by the scale-check regex.
