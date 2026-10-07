"""Pure-rule tests: structure validation, grading, scoring (tests 3-12 of the spec)."""
import copy

import pytest

from app.services import module_assessment_rules as rules
from module_assessment_helpers import load_seed_assessments, seed_assessment


def specs(data):
    return [{**q, "order": i} for i, q in enumerate(data["questions"], 1)]


def errors_for(data):
    return rules.validate_assessment_structure(specs(data), level=data["level"], passing_percent=80, required_coding=1)


def test_seeded_assessments_are_all_valid_and_cover_every_level():
    all_assessments = load_seed_assessments()
    assert {a["level"] for a in all_assessments} == {"beginner", "intermediate", "advanced"}
    for a in all_assessments:
        assert errors_for(a) == [], (a["module_slug"], a["level"])


@pytest.mark.parametrize("level", ["beginner", "intermediate", "advanced"])
def test_every_level_has_exactly_3_mcq_2_quiz_2_coding(level):
    data = seed_assessment(level)
    kinds = [q["type"] for q in data["questions"]]
    assert (len(kinds), kinds.count("mcq"), kinds.count("quiz"), kinds.count("coding")) == (7, 3, 2, 2)


def test_difficulty_changes_but_structure_does_not():
    difficulty = {lv: {q["difficulty"] for q in seed_assessment(lv)["questions"]} for lv in rules.LEVELS}
    assert difficulty == {"beginner": {"easy"}, "intermediate": {"medium"}, "advanced": {"hard"}}
    layouts = {tuple(q["type"] for q in seed_assessment(lv)["questions"]) for lv in rules.LEVELS}
    assert len(layouts) == 1


@pytest.mark.parametrize("swap", [("mcq", "quiz"), ("coding", "mcq")])
def test_wrong_composition_is_rejected(swap):
    data = seed_assessment()
    first = next(q for q in data["questions"] if q["type"] == swap[0])
    first["type"] = swap[1]
    assert any("must have exactly" in e for e in errors_for(data))


def test_wrong_question_count_is_rejected():
    data = seed_assessment()
    data["questions"].pop()
    assert any("exactly 7 questions" in e for e in errors_for(data))
    data["questions"] += [copy.deepcopy(data["questions"][0]) for _ in range(2)]
    assert any("exactly 7 questions" in e for e in errors_for(data))


def test_mcq_needs_four_options_and_one_valid_correct_answer():
    data = seed_assessment()
    mcq = next(q for q in data["questions"] if q["type"] == "mcq")
    mcq["options"] = mcq["options"][:3]
    assert any("exactly 4 options" in e for e in errors_for(data))
    mcq = next(q for q in seed_assessment()["questions"] if q["type"] == "mcq")
    data = seed_assessment()
    bad = next(q for q in data["questions"] if q["type"] == "mcq")
    bad["correct_answer"] = {"choice": "zzz"}
    assert any("correct_answer.choice" in e for e in errors_for(data))


def test_quiz_needs_a_valid_format_and_answer():
    data = seed_assessment()
    quiz = next(q for q in data["questions"] if q["type"] == "quiz")
    quiz["quiz_format"] = "essay"
    assert any("quiz_format must be one of" in e for e in errors_for(data))


def test_coding_needs_valid_execution_data():
    data = seed_assessment()
    coding = next(q for q in data["questions"] if q["type"] == "coding")
    coding["coding_config"]["test_cases"] = coding["coding_config"]["test_cases"][:2]
    coding["coding_config"]["function_name"] = "not valid"
    errors = errors_for(data)
    assert any("at least 3 test_cases" in e for e in errors) and any("function_name" in e for e in errors)


def test_every_question_needs_points_and_difficulty_matching_the_level():
    data = seed_assessment("advanced")
    data["questions"][0]["points"] = 0
    data["questions"][1]["difficulty"] = "easy"
    errors = errors_for(data)
    assert any("points must be a positive number" in e for e in errors)
    assert any("does not match the advanced level" in e for e in errors)


def outcomes(mcq, quiz, coding, coding_points=1.0):
    return (
        [{"type": "mcq", "points": 1.0, "correct": c} for c in mcq]
        + [{"type": "quiz", "points": 1.0, "correct": c} for c in quiz]
        + [{"type": "coding", "points": coding_points, "correct": c} for c in coding]
    )


def test_below_80_percent_fails():
    r = rules.compute_result(outcomes([True] * 3, [True, False], [True, False]), passing_percent=80, required_coding=1)
    assert r["percentage"] == 71.4 and not r["score_requirement_met"] and r["coding_requirement_met"] and not r["passed"]


def test_80_percent_without_a_passed_coding_question_fails():
    # Coding worth less, so 80%+ is reachable without any coding pass - the coding requirement must still fail it.
    r = rules.compute_result(outcomes([True] * 3, [True] * 2, [False, False], coding_points=0.25), passing_percent=80, required_coding=1)
    assert r["percentage"] >= 80 and r["score_requirement_met"] and not r["coding_requirement_met"] and not r["passed"]


def test_80_percent_with_one_coding_question_passes():
    r = rules.compute_result(outcomes([True] * 3, [True, False], [True, True]), passing_percent=80, required_coding=1)
    assert r["percentage"] == 85.7 and r["passed"]
    assert r["by_type"]["mcq"]["correct"] == 3 and r["by_type"]["quiz"]["correct"] == 1 and r["by_type"]["coding"]["correct"] == 2


def test_exactly_the_threshold_passes():
    r = rules.compute_result([{"type": "mcq", "points": 1, "correct": i < 4} for i in range(5)] + [{"type": "coding", "points": 1, "correct": True}] * 0,
                             passing_percent=80, required_coding=0)
    assert r["percentage"] == 80.0 and r["passed"]


@pytest.mark.parametrize("payload", [{"choices": "a"}, {"choices": [1, 2]}, {"choices": ["nope"]}])
def test_malformed_multi_select_answers_are_validation_errors(payload):
    spec = {"type": "quiz", "quiz_format": "multi_select", "options": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}, {"id": "c", "text": "C"}],
            "correct_answer": {"choices": ["a"]}}
    with pytest.raises(rules.AnswerValidationError):
        rules.grade_objective_question(spec, payload)


def test_unanswered_is_incorrect_not_an_error():
    spec = {"type": "mcq", "options": [{"id": "a", "text": "A"}] * 1, "correct_answer": {"choice": "a"}}
    assert rules.grade_objective_question(spec, None) is False
    assert rules.grade_objective_question(spec, {}) is False


def test_short_answer_matching_ignores_case_and_spacing():
    spec = {"type": "quiz", "quiz_format": "short_answer", "correct_answer": {"accepted": ["len", "len()"]}}
    assert rules.grade_objective_question(spec, {"text": "  LEN() "}) is True
    assert rules.grade_objective_question(spec, {"text": "size"}) is False
