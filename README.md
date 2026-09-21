# Day 5 Assignment — Student LangChain Agent

LangChain + Gemini agent backed by SQLite.

## Implemented
- SQLite `students.db` with the five assignment students
- `get_student_info(student_id)`
- `get_student_marks(student_id)`
- `calculator(expression)`
- `get_passing_rules()`
- Gemini agent with dynamic tool selection
- No fixed tool-call sequence

## Setup

```bash
python -m venv .venv
pip install -r requirements.txt
```

Set `GOOGLE_API_KEY`, then:

```bash
python setup_db.py
python test_tools.py
python app.py
```

## Challenge question

```text
I am 22CS045. Tell me my name, department, total marks, average marks, and whether I satisfy the university passing requirements.
```

Expected facts: Dhanushya, Computer Science, total 325, average 81.25%. The supplied rules are average >= 40% and every subject >= 35%.

## Security
- Never commit `.env` or an API key.
- The calculator uses a restricted AST evaluator, not Python `eval()`.
- `students.db` is generated locally and ignored by Git.
