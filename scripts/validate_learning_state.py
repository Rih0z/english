"""Validate the active lesson against an independently supplied learning date."""
import argparse
import datetime
import json
import pathlib

def validate(root, learning_date):
    day = datetime.date.fromisoformat(learning_date)
    assert str(day) == learning_date, "Date must use YYYY-MM-DD"
    manifest = json.loads((root / "latest.json").read_text())
    directory = day.strftime("%Y/%m/%d")
    cycle_path = directory + "/english_learning_cycle.json"
    note_path = directory + "/english_daily_note_" + learning_date + ".md"
    assert manifest["learning_date"] == learning_date, "Manifest learning date mismatch"
    assert manifest["cycle_path"] == cycle_path, "Cycle path mismatch"
    assert manifest["note_path"] == note_path, "Note path mismatch"
    cycle = json.loads((root / cycle_path).read_text())
    state = cycle["state"]
    assert cycle["meta"]["updated_date"] == learning_date, "Metadata date mismatch"
    assert state["active_learning_date"] == learning_date, "Active learning date mismatch"
    daily = state["daily_notes"][learning_date]
    assert daily["learning_date"] == learning_date, "Daily note date mismatch"
    assert state["lesson_number"] == daily["lesson_number"] == manifest["lesson_number"], "Lesson mismatch"
    ids = [s["session_id"] for d in state["daily_notes"].values() for s in d["sessions"]]
    assert len(ids) == len(set(ids)), "Duplicate session ID"
    for date, record in state["daily_notes"].items():
        prefix = "S-" + date.replace("-", "") + "-"
        assert all(s["session_id"].startswith(prefix) for s in record["sessions"]), "Session date mismatch"
    note = (root / note_path).read_text()
    assert learning_date in note and "Lesson " + str(manifest["lesson_number"]) in note, "Note header mismatch"
    assert cycle_path in note, "Note source mismatch"
    template = json.loads((root / "first-prompt.json").read_text())
    assert template["instructions"] == cycle["instructions"], "Template instructions mismatch"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--learning-date", required=True)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("."))
    args = parser.parse_args()
    validate(args.root, args.learning_date)
    print("Validated learning date, paths, lesson, session IDs, note, and template.")
