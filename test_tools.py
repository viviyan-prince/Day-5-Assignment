from app import calculator, get_passing_rules, get_student_info, get_student_marks, init_db

def run():
    init_db()
    assert "Dhanushya" in get_student_info.invoke({"student_id": "22CS045"})
    assert "Computer Science" in get_student_info.invoke({"student_id": "22CS045"})
    marks = get_student_marks.invoke({"student_id": "22CS045"})
    assert all(value in marks for value in ["85", "72", "90", "78"])
    assert calculator.invoke({"expression": "85 + 72 + 90 + 78"}) == "325"
    assert calculator.invoke({"expression": "325 / 4"}) == "81.25"
    rules = get_passing_rules.invoke({})
    assert "40%" in rules and "35%" in rules
    print("All deterministic tool tests passed.")

if __name__ == "__main__":
    run()
