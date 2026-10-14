#!/usr/bin/env python3
"""
The validator's own check. Run before trusting a change to it.

The spec arrives from a language model by way of an email and an issue body,
so the failures worth catching are quiet ones: a field dropped, a gloss with
no phrase, a brand name misspelt. Each of those would otherwise render a
clean-looking post with something missing from it.

    python occasion/check-spec.py
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec_mod = importlib.util.spec_from_file_location("render_posts", HERE / "render-posts.py")
render = importlib.util.module_from_spec(spec_mod)
spec_mod.loader.exec_module(render)

GOOD = json.loads((HERE / "example-micchami-dukkadam.json").read_text(encoding="utf-8"))


def rejects(mutate, because: str) -> None:
    broken = copy.deepcopy(GOOD)
    mutate(broken)
    try:
        render.validate(broken)
    except render.PostError:
        return
    raise AssertionError(f"accepted a spec it should have rejected: {because}")


def accepts(mutate, because: str) -> None:
    ok = copy.deepcopy(GOOD)
    mutate(ok)
    try:
        render.validate(ok)
    except render.PostError as exc:
        raise AssertionError(f"rejected a spec it should have accepted ({because}): {exc}")


def main() -> int:
    render.validate(copy.deepcopy(GOOD))

    rejects(lambda s: s.pop("slug"), "no slug, so the files have no name")
    rejects(lambda s: s.update(slug="   "), "a blank slug")
    rejects(lambda s: s["occasion"].pop("eyebrow"), "no eyebrow")
    rejects(lambda s: s["occasion"].pop("phrase"), "a gloss with nothing to gloss")
    rejects(lambda s: s["occasion"].update(gloss=[["miccha"]]), "a one-sided gloss pair")
    rejects(lambda s: s["brands"]["metaldock"].pop("reading"), "Metal Dock with no reading")
    rejects(lambda s: s["brands"]["dockfinity"].pop("ask"), "Dockfinity with no ask")
    rejects(lambda s: s["brands"]["metaldock"].update(reading=""), "an empty string is not copy")
    rejects(lambda s: s["brands"].update(metaldoc=s["brands"]["metaldock"]), "a misspelt brand")
    rejects(lambda s: s.update(brands={}), "no brands at all")
    rejects(lambda s: s["brands"]["metaldock"].update(headline="We ask your forgiveness."),
            "a headline that is a string rather than lines")
    rejects(lambda s: s["brands"]["metaldock"].update(headline=["a", "b", "c", "d"]),
            "four headline lines, which the plate cannot hold")

    # An occasion that is not built on an unfamiliar phrase - Diwali, Republic
    # Day - carries neither phrase nor gloss, and that is not an error.
    accepts(lambda s: [s["occasion"].pop("phrase"), s["occasion"].pop("gloss")],
            "no phrase and no gloss")
    accepts(lambda s: s["brands"].pop("dockfinity"), "one brand only")
    accepts(lambda s: s["brands"].pop("metaldock"), "the other brand only")

    print("check-spec: all cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
