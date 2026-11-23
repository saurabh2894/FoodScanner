"""Actual existing code-free OCR disagreement, no new OCR/accuracy claims."""
from pathlib import Path
from foodscan.pipeline import analyse_image, analyse_text, _reading_items
D=Path(__file__).parent/'fixtures/ingredient_reading_conflict'
class Captured:
    def __init__(self, prefix): self.prefix=prefix
    def extract_text(self,path): return (D/(self.prefix+'-1.txt')).read_text()
    def extract_text_alt(self,path): return (D/(self.prefix+'-2.txt')).read_text()

def test_actual_code_free_item_differences_get_review_without_merging():
    for prefix in ['native-N08','native-N14','browser-N08','browser-N09']:
        e=Captured(prefix);a=analyse_image('unused',e);c=a.reading_conflict
        assert c and c['items_differ'],prefix
        assert not any(r['codes'] for r in c['readings'])
        chosen=next(r for r in c['readings']if r['label']==c['chosen'])
        assert a.extracted_text==chosen['text']
        assert a.ingredients==chosen['ingredients']
        assert c['readings'][0]['ingredients']!=c['readings'][1]['ingredients']

def test_signature_ignores_only_case_spacing_punctuation():
    assert _reading_items(analyse_text('Ingredients: Milk, Sugar.'))==_reading_items(analyse_text('INGREDIENTS: milk , sugar'))
    assert _reading_items(analyse_text('Ingredients: Milk (2%), Sugar'))!=_reading_items(analyse_text('Ingredients: Milk (3%), Sugar'))
    assert _reading_items(analyse_text('Ingredients: Milk, Sugar'))!=_reading_items(analyse_text('Ingredients: Sugar, Milk'))

def test_actual_identical_readings_no_false_notice():
    class Same(Captured):
        def extract_text_alt(self,path):return self.extract_text(path)
    for prefix in ['native-N08','native-N14','browser-N08','browser-N09']:
        assert analyse_image('unused',Same(prefix)).reading_conflict is None
