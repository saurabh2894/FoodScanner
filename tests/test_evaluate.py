from foodscan.evaluate import evaluate, format_report, read_labels


def _setup(tmp_path, rows):
    (tmp_path / "labels.csv").write_text("file,nova_ref,status,notes\n" + "\n".join(rows) + "\n")


def _txt(tmp_path, name, text):
    (tmp_path / name).write_text(text)


def test_coverage_and_accuracy_are_separate_and_correct(tmp_path):
    _txt(tmp_path, "a.txt", "Ingredients: Whole wheat flour.")                     # answers 1, ref 1  -> right
    _txt(tmp_path, "b.txt", "Ingredients: Cucumber, water, salt, vinegar, dill.")  # answers 3, ref 4  -> wrong
    _txt(tmp_path, "c.txt", "Ingredients: Sugar, refined wheat flo")               # abstains
    _txt(tmp_path, "d.txt", "Ingredients: Sugar, maltodextrin, salt.")             # answers 4, label uncertain -> excluded
    _setup(tmp_path, ["a.txt,1,confirmed,", "b.txt,4,confirmed,", "c.txt,2,confirmed,", "d.txt,3,uncertain,"])
    rep = evaluate(tmp_path / "labels.csv")
    assert rep.total == 4 and len(rep.answered) == 3 and len(rep.abstained) == 1
    assert rep.coverage == 0.75
    assert len(rep.scored) == 2 and len(rep.wrong) == 1 and rep.accuracy == 0.5
    out = format_report(rep)
    assert "Coverage:  3/4" in out and "Accuracy on answered:  1/2" in out
    assert "b.txt: predicted 3, reference 4" in out           # wrong call listed
    assert "c.txt" in out and "truncated" in out              # abstention listed with reason
    assert "excluded: label uncertain" in out


def test_all_abstain_gives_na_accuracy_not_crash(tmp_path):
    _txt(tmp_path, "a.txt", "Salt")
    _setup(tmp_path, ["a.txt,2,confirmed,"])
    rep = evaluate(tmp_path / "labels.csv")
    assert rep.coverage == 0 and rep.accuracy is None
    assert "n/a" in format_report(rep)


def test_uncertain_label_abstention_kept_in_analysis(tmp_path):
    _txt(tmp_path, "a.txt", "Salt")
    _setup(tmp_path, ["a.txt,,uncertain,not sure"])
    rep = evaluate(tmp_path / "labels.csv")
    assert len(rep.abstained) == 1 and "no reference" in format_report(rep)


def test_bad_rows_and_missing_files_reported_not_silently_dropped(tmp_path):
    _setup(tmp_path, ["x.txt,1,confirmed,", "y.txt,9,confirmed,", "z.txt,,confirmed,"])
    rep = evaluate(tmp_path / "labels.csv")
    assert len(rep.errors) == 3 and rep.total == 0
    out = format_report(rep)
    assert "file not found" in out and "invalid nova_ref" in out and "needs a nova_ref" in out


def test_samples_subfolder_and_image_path_use_ocr_engine(tmp_path):
    (tmp_path / "samples").mkdir()
    (tmp_path / "samples" / "p.png").write_bytes(b"not really an image")

    class Fake:
        def extract_text(self, p):
            return "Ingredients: Cucumber, water, salt, vinegar, dill."

    _setup(tmp_path, ["p.png,3,confirmed,"])
    rep = evaluate(tmp_path / "labels.csv", ocr=Fake())
    assert rep.accuracy == 1.0


def test_read_labels_header_only(tmp_path):
    _setup(tmp_path, [])
    assert read_labels(tmp_path / "labels.csv") == ([], [])
