from didactopus.pedagogy import review_learning_path


def test_author_review_reports_alignment_without_learner_scoring():
    report = review_learning_path({"promise": "Learn", "outcomes": [{"id": "o1", "title": "Explain"}],
                                   "activities": [{"id": "a1", "title": "Practice", "outcome_ids": ["o1"],
                                                   "evidence": ["explanation"], "accessibility_options": ["text"]}]})
    assert report["status"] == "ready"
    assert report["learner_labels"] == []
