"""Overlay markdown rendering (no Qt required)."""
from oncue.ui.overlay import markdown_to_html


def test_inline_code():
    html_out = markdown_to_html("use `Number()` here")
    assert "<code" in html_out
    assert "Number()" in html_out


def test_bold_text():
    html_out = markdown_to_html("This is **important**")
    assert "<strong>important</strong>" in html_out


def test_bullet_list():
    html_out = markdown_to_html("- first\n- second")
    assert "<ul" in html_out
    assert "<li>first</li>" in html_out


def test_fenced_code_block():
    html_out = markdown_to_html("```python\nx = 1\n```")
    assert "<pre" in html_out
    assert "x = 1" in html_out
