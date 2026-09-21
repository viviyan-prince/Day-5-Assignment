import ast
import operator as op
import os
import sqlite3
from typing import Any

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

DB_PATH = os.path.join(os.path.dirname(__file__), "students.db")


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                python INTEGER NOT NULL,
                database INTEGER NOT NULL,
                ai INTEGER NOT NULL,
                web INTEGER NOT NULL
            )"""
        )
        students = [
            ("22CS045", "Dhanushya", "Computer Science", 85, 72, 90, 78),
            ("22CS046", "Rahul", "Computer Science", 65, 70, 68, 72),
            ("22CS047", "Priya", "Information Technology", 92, 88, 95, 90),
            ("22CS048", "Arun", "Information Technology", 55, 60, 58, 62),
            ("22CS049", "Meena", "Computer Science", 78, 85, 80, 88),
        ]
        conn.executemany(
            """INSERT OR IGNORE INTO students
            (student_id, name, department, python, database, ai, web)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            students,
        )
        conn.commit()
    finally:
        conn.close()


def _get_student(student_id: str) -> tuple[Any, ...] | None:
    conn = sqlite3.connect(DB_PATH)
    try:
        return conn.execute(
            "SELECT student_id, name, department, python, database, ai, web "
            "FROM students WHERE student_id = ?",
            (student_id.strip(),),
        ).fetchone()
    finally:
        conn.close()


@tool
def get_student_info(student_id: str) -> str:
    """Get a student's name and department."""
    student = _get_student(student_id)
    if student is None:
        return f"No student was found with ID {student_id}."
    return f"Student ID: {student[0]}\nName: {student[1]}\nDepartment: {student[2]}"


@tool
def get_student_marks(student_id: str) -> str:
    """Get Python, Database, AI, and Web marks."""
    student = _get_student(student_id)
    if student is None:
        return f"No student was found with ID {student_id}."
    return (
        f"Student ID: {student[0]}\n"
        f"Python: {student[3]}\n"
        f"Database: {student[4]}\n"
        f"AI: {student[5]}\n"
        f"Web: {student[6]}"
    )


_ALLOWED_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}
_ALLOWED_UNARYOPS = {ast.UAdd: op.pos, ast.USub: op.neg}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left, right = _safe_eval(node.left), _safe_eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large")
        return _ALLOWED_BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Only basic arithmetic expressions are allowed")


@tool
def calculator(expression: str) -> str:
    """Calculate a basic arithmetic expression."""
    try:
        result = _safe_eval(ast.parse(expression.strip(), mode="eval"))
        return str(int(result)) if result.is_integer() else f"{result:.4f}".rstrip("0").rstrip(".")
    except Exception as exc:
        return f"Calculator error: {exc}"


@tool
def get_passing_rules() -> str:
    """Return the university passing rules."""
    return (
        "University passing rules:\n"
        "1. Minimum overall average: 40%\n"
        "2. Minimum mark in each subject: 35%"
    )


def build_agent():
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("GOOGLE_API_KEY is not set.")
    model = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        temperature=0,
    )
    tools = [get_student_info, get_student_marks, calculator, get_passing_rules]
    system_prompt = """
You are a student information assistant.
Choose tools dynamically; do not follow a hard-coded sequence.
Use database tools for student information and marks.
Use calculator for totals and averages.
Use get_passing_rules for pass/eligibility questions.
Never invent student data or university rules.
Give short, clear answers.
"""
    return create_agent(model, tools=tools, system_prompt=system_prompt)


def ask(agent, question: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    content = result["messages"][-1].content
    return content if isinstance(content, str) else str(content)


if __name__ == "__main__":
    init_db()
    agent = build_agent()
    print("Student Agent ready. Type 'exit' to quit.\n")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        try:
            print("Agent:", ask(agent, question), "\n")
        except Exception as exc:
            print("Error:", exc)
