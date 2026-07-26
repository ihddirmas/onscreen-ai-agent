from webapp.styles import tokens


def test_color_tokens_present():
    required = {"bg", "surface", "border", "text", "text_muted", "accent", "success", "warning", "error"}
    assert required.issubset(tokens.COLOR.keys())


def test_font_tokens_present():
    assert "sans" in tokens.FONT
    assert "mono" in tokens.FONT


def test_radius_and_shadow_present():
    assert {"sm", "md", "pill"}.issubset(tokens.RADIUS.keys())
    assert tokens.SHADOW_CARD.startswith("0 ")
