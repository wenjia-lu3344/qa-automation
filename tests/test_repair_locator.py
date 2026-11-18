import pytest
from tools.repair_locator import propose
from tools.apply_repair import apply


def test_proposal():
    src = "await page.get_by_role('button', name='登録する').click(timeout=2000)"
    snapshot = '- button "送信する"'
    result = propose(src, snapshot, 1)
    assert result['status'] == 'proposal'
    assert "name='送信する'" in result['new_code']


def test_ambiguous():
    result = propose("await page.get_by_role('button', name='Pay').click()", '- button "Pay now"\n- button "Pay later"', 1)
    assert result['status'] == 'ambiguous'


def test_prevent_stale_file(tmp_path):
    f = tmp_path / 'test.py'
    f.write_text('some other code\n')
    with pytest.raises(ValueError, match='changed'):
        apply(f, {'status': 'proposal', 'line': 1, 'old_code': 'old', 'new_code': 'new'})


def test_duplicate_button_names_are_ambiguous():
    result = propose("await page.get_by_role('button', name='Pay').click()",
                     '- button "Pay now"\n- button "Pay now"', 1)
    assert result['status'] == 'ambiguous'

def test_non_locator_code_not_proposed():
    result = propose('assert total == 100', '- button "Pay"', 1)
    assert result['status'] == 'unsupported'
