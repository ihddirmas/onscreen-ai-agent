import reflex as rx

from webapp.components.hero import hero
from webapp.components.how_it_works import how_it_works
from webapp.components.nav import nav
from webapp.components.pricing import pricing
from webapp.components.social_proof import social_proof
from webapp.styles import tokens

# Subtle scroll parallax for elements tagged data-parallax="<factor>" (see
# hero.py, how_it_works.py). Bounded retry for elements that aren't in the
# DOM yet at script-run time, rAF-throttled scroll handler, and a hard skip
# for prefers-reduced-motion — motion here is a depth cue, not the point.
_PARALLAX_JS = """
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  function init() {
    var els = document.querySelectorAll('[data-parallax]');
    if (!els.length) return false;
    var ticking = false;
    function update() {
      var y = window.scrollY;
      els.forEach(function (el) {
        var factor = parseFloat(el.getAttribute('data-parallax')) || 0;
        el.style.transform = 'translateY(' + (y * factor).toFixed(1) + 'px)';
      });
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    return true;
  }
  if (!init()) {
    var iv = setInterval(function () { if (init()) clearInterval(iv); }, 200);
    setTimeout(function () { clearInterval(iv); }, 5000);
  }
})();
"""


def _footer() -> rx.Component:
    return rx.center(
        rx.text(
            f"© {tokens.BRAND_NAME}",
            color=tokens.COLOR["text_muted"], size="1",
        ),
        padding="24px", border_top=f"1px solid {tokens.COLOR['border']}",
        margin_top="24px",
    )


def landing_page() -> rx.Component:
    return rx.box(
        nav(),
        hero(),
        how_it_works(),
        social_proof(),
        pricing(),
        _footer(),
        rx.script(_PARALLAX_JS),
        background=tokens.COLOR["bg"], min_height="100vh",
    )
