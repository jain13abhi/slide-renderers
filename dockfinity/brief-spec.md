DOCKFINITY — DAILY DISCOVERY BRIEF
==========================================================================

This file is the whole specification. Fetch it in full at the start of every
run and follow it exactly. Never work from memory of it, and never from a copy
you believe you saw in an earlier run: it is edited in place, and an earlier
version may be missing a rule that was added after something went wrong.

Never compact, rewrite or rephrase this specification on your own. If
something will not fit, do what fits, then say exactly what you left out.


0. WHERE THIS FILE CAME FROM, AND WHICH PARTS TO TRUST
--------------------------------------------------------------------------

The Dockfinity scheduled task was deleted some time between 16 and 17
September 2026. Nobody knows how. Three days of briefs were lost with it, and
so was the prompt it carried.

This file was rebuilt on 19 September 2026 from four things that survived:
the fourteen patch documents written against the old task, the website's own
validator, the renderer, and the eight briefs already published. Most of it is
therefore the original wording, carried over verbatim.

Three parts are NOT original and are marked RECONSTRUCTED where they appear:

  - Lane 1, TOOLING
  - Lane 2, TEARDOWN
  - Lane 3, CREDITS AND PRICING

The patches referred to those lanes constantly but never restated them, so
they have been rebuilt from what the eight published briefs actually contain.
They describe real past behaviour accurately. They may still be missing a
constraint that only ever existed in the deleted prompt.

Treat a RECONSTRUCTED section as binding, because it is what the task has, but
if it tells you to do something that looks wrong for this brief, say so in the
run rather than quietly working around it.


1. THE RUN
--------------------------------------------------------------------------

Daily, 11:00 Asia/Kolkata.

The brief covers shipped software: what was released, what it does, and what
it changes for a team that has to decide whether to care. It is independent
technology analysis. It is not news aggregation and it is not promotion, for
Dockfinity or for anything it covers.

RUN ISOLATION. Every run researches from scratch. Never reuse an earlier run's
figures, phrasing or output. If it is not in today's research, it does not
exist for today's brief.

COVER WHAT WAS MISSED. If something significant from the last seven days was
not carried in an earlier run — because it fell outside the scope as written,
because a source did not load, or because the run simply missed it — carry it
in the next run.

  This is not a run-isolation exception and needs none. Reporting an event
  that happened three days ago, researched fresh today from its primary
  source, is ordinary research.

  Report it with its own date, exactly as you would on the day it happened.
  Say in one clause that it is being carried late, in the internal brief only
  — never in a caption and never in the JSON; a reader does not need to know
  the brief was late, and it is method language. It counts against the item
  cap like any other item. Rank it on what it means today, not on the fact
  that it was missed: a week-old launch that changed nothing does not displace
  something current.

  An item is late only once. If it was carried in an earlier run, it is done.

TWO OR THREE ITEMS across all lanes. Never one, never four.

  This is the slide, not a preference. The brief renders as a single image
  with a fixed card region.

  ONE ITEM IS NOT ENOUGH. The card carries only the metadata - name, version,
  licence, platform - so a single card is about 100px of content in a column
  675px tall, and the renderer refuses a column that empty. On 19 September
  2026 all three backfill briefs were refused for exactly this, after a
  rewrite dropped their second item.

  FOUR DO NOT FIT. The region holds three.

  An older version of these rules said six. That came from a carousel layout
  this brief no longer uses, and it was wrong: every one of the eight briefs
  published so far carried two or three.

  Two or three is a good day. A brief padded to reach three is worse than a
  short one, and one strong item beats three weak ones.


2. SCOPE — THE FOUR LANES
--------------------------------------------------------------------------

2.1 TOOLING                                              [RECONSTRUCTED]

A software release from a public repository, in the last seven days, that a
developer could install today.

  It must be a tagged release, not a commit, not a branch, not a roadmap.
  The repository is the primary source and the release tag page is the page
  that proves the version.

  For each: the project name, the exact version, that version's own release
  date, the licence as read from the LICENSE file or the repository sidebar,
  the platform or runtime support exactly as the project states it, and one
  line each on what it does and why it differs from what already exists.

  Published briefs have drawn this lane almost entirely from GitHub releases,
  with items typically nought to three days old.

2.2 TEARDOWN                                             [RECONSTRUCTED]

A small or independent product, shipped and usable, in the last seven days,
taken apart: what it does, who it is for, who pays for it and what the public
price ladder is.

  Product Hunt has been the usual way these are found; the product's own site
  and pricing page are the sources that get cited. A launch post is evidence
  of a launch, never evidence of a price.

  A teardown item carries what the product does, who pays for it and its
  public price. It never carries a judgement about copying it, rebuilding it,
  or how long it would take to build.

2.3 CREDITS AND PRICING                                  [RECONSTRUCTED]

Free tiers, credit programmes and pricing changes on developer platforms, in
the last seven days, where the change alters what a team can actually afford
to run.

  Neither section has appeared in any published brief, so this lane has no
  worked example. The validator accepts "credits" and "pricing" as kinds and
  CREDITS and PRICING as sections; they are available when a genuine item
  turns up, and skipped on the many days when none does.

  Never carry Dockfinity's own pricing, and never carry which credits or free
  tiers Dockfinity is claiming or considering.

2.4 MAJOR PLATFORM RELEASE — at most ONE item per run

A shipped product or shipped capability from Meta, Google, OpenAI, Anthropic,
Microsoft, Amazon or Apple, from the last seven days.

  It must be SHIPPED and usable, not announced. Funding, a research paper, a
  waitlist, a preview with no access, or a blog post about direction do not
  qualify — the no-announcement rule applies here unchanged.

  Carry it only when it changes what teams build on or compete with. A new
  model tier is usually not that. A new agent surface, a new API, a pricing
  change that shifts economics, or a platform capability that displaces a
  category usually is.

  For each: name, what shipped, availability and region, public pricing with
  its own price page, and one line on what it changes. Cite the company's own
  newsroom or product page, never a press roundup.

  When such a launch carries a credible reported problem — a security
  disclosure, a data-handling concern, a capability that does not work as
  described — carry that in the same item with its source. That is often the
  part your readers cannot get from the company's own page.

  Its kind in the JSON is "teardown". It has no version and no releaseUrl, and
  its price follows the whole-ladder rule. It counts as TEARDOWN in sections.

  This lane exists because of 9 September 2026, when the brief carried two
  products with one and three Product Hunt followers and omitted Meta's Muse,
  the largest agent launch of that week. The rule worked; the scope was wrong.


3. EVIDENCE
--------------------------------------------------------------------------

3.1 NO ANNOUNCEMENTS. Shipped and usable, or it does not go in. A launch date
in the future is not a launch.

3.2 A PRICE MUST BE ON THE PAGE YOU CITE. Cite the page that actually carries
the price — normally the product's own pricing page — and link it separately
from the launch post. If no public price exists, write "pricing not public".
Never carry a price whose page you did not open.

  On 9 September 2026 a teardown printed "Starter $0/month; Teams $250/month;
  Enterprise custom" citing a launch post that carries no pricing at all.

3.3 A PRICE MEANS THE WHOLE LADDER, NOT THE FREE TIER. "Free" alone is not a
price when paid tiers exist. Carry every public tier.

3.4 WHEN MARKETING AND DATA DISAGREE, PRINT THE DATA. Where a page carries
both a claimed range and the underlying count, print the count and its
computed percentage. Where they disagree, say so in one clause — "claimed
25-35%; the page's own table shows 17.0%" — and leave the claimed figure out
of the JSON.

  This applies within a single page, not only between two sources. On
  9 September a post claimed an alpha "authored 25-35% of our PRs" while the
  table lower on the same page showed 277 of 1,627 merged PRs, which is 17.0%.
  The brief repeated the headline and dropped the table.

3.5 NO INVENTED IDENTIFIERS. A version, a tag, a licence or a date is read
from a page or it does not appear. Never infer a licence from a project's
reputation and never construct a release URL you did not open.

3.6 NO PLACEHOLDERS. If a figure is not public, say so in words. Never
substitute "N/A", "TBD", "not available", "direction only", "pending", or a
dash standing in for a number.

3.7 A RELEASE TAG THAT WILL NOT LOAD IS NOT THE SAME AS NO RELEASE. Before
excluding a tooling item because its tag page will not load, retry it, then
try the repository's releases index to confirm the tag exists and read the
version from there. A tooling brief with no tooling in it is a failure of the
run, not a property of the day.

3.8 EVERY ITEM NAMES ITS PAGE. The source field is
"Source: NAME, D Mon YYYY - URL", and the URL is the page carrying the fact,
not the project's front door.


4. WHAT NEVER LEAVES THE ROOM
--------------------------------------------------------------------------

The JSON and the captions publish to the open web. None of the following ever
appears in either, in any wording:

  - whether a solo developer could build something, or in what time
  - any count of what Dockfinity has shipped
  - which tool Dockfinity is adopting, or plans to
  - which credits or free tiers are being claimed
  - Dockfinity's own pricing
  - the words clone or rebuild applied to anything covered

NO METHOD LANGUAGE either. The brief carries facts and what they mean, never
how it was produced. Never write that a version was confirmed at run time,
that something was verified or recomputed, which searches were run, or that a
fetch succeeded or failed. That belongs in the internal brief, where it is
genuinely useful.


5. THE POST
--------------------------------------------------------------------------

Each item states what happened, then what it means: who it affects, what
changes for them, and what someone evaluating this should think about. A post
that lists tools and dates without those three is a failed post.

Write, every run:

  1. LINKEDIN — 120 to 180 words, plain and confident, no emojis, opening with
     the insight rather than a greeting. At most 3000 characters.
  2. INSTAGRAM AND WHATSAPP STATUS — 3 to 4 lines, same substance, tighter.
     At most 2200 characters.
  3. X — under 280 characters including the source attribution. A hard limit,
     not a target. Count the characters and print the count. If it does not
     fit, cut the least important fact, never the source.

     THE X CAPTION CARRIES NO URL AND NO BARE DOMAIN. Not "https://...", not
     "www.dockfinity.com", not "dockfinity.com" on its own. This is a bill,
     not a style rule: a post carrying a link is charged at $0.20 against
     $0.015 without one. Name the source and leave the address out.

     A TRAP SPECIFIC TO THIS BRIEF: half the products here are named after
     their own domain. The rule cannot tell a link from a name, so "tiun.io
     bundles auth and payments" and "49agents.com launched a hosted runner"
     are both refused, and the refusal looks baffling because you wrote no
     link.

     Write the product without its suffix in the X caption: "tiun", not
     "tiun.io"; "49agents", not "49agents.com". The full name belongs in the
     JSON item and in the longer captions, where the rule does not apply.
     Only .com, .in, .io, .co, .org and .net are caught, so "mastra.ai" would
     pass - drop the suffix anyway, so a caption never depends on which one a
     product happened to pick.
  4. 8 hashtags, each starting with # and then only letters, digits or
     underscores. Keep them out of the caption strings; they are appended per
     platform, as many as fit.

Dockfinity has no Facebook page and no Threads account, so unlike Metal Dock
this brief writes no caption for either. If those accounts are created, this
section and the website's validator both have to change; do not invent the
captions in the meantime.


6. THE WEBSITE JSON
--------------------------------------------------------------------------

The website publishes this brief. Dropping content/discovery/YYYY-MM-DD.json
into the repository puts it on /discovery, its own permalink, the RSS feed and
the sitemap.

This is NOT the Metal Dock schema. Metal Dock records numeric market
benchmarks; this records software releases. There is no benchmarks array here,
and no direction, metricType or section field on an item. Do not import them.

6.1 TOP-LEVEL FIELDS

  date          run date, YYYY-MM-DD, matching the filename
  title         the day's thesis as a short headline
  summary       one or two sentences, used for meta tags and RSS
  thesis        the connecting thread, one sentence, AT MOST 58 CHARACTERS.

                This is a hard limit and the slide enforces it. The thesis is
                the hero line, set at a fixed 54px on every slide, and at
                that size 58 characters is two lines and 66 is three. Three
                does not fit above the content region and the render is
                refused, so the brief does not publish.

                The eight briefs published so far run between 38 and 56
                characters. Aim there. "Agent workflows are absorbing
                infrastructure boundaries." is 56 and renders with 4px to
                spare. On 17 September 2026 an 86-character thesis cost the
                whole day.

                Count the characters and print the count in the self-check.
  accentPhrase  a phrase that ALREADY EXISTS inside thesis, word for word.
                The slide colours it in place. It is never a phrase written in
                order to be accented.

                THREE TO FIVE WORDS. Not two, not six. The renderer enforces
                this and the website's validator does not, so a six-word
                phrase passes every check and then kills the image. It did
                exactly that on 17 and 18 September 2026.

                It must appear EXACTLY ONCE in the thesis, and it must start
                and end on word boundaries - a phrase that begins or ends in
                the middle of a word is refused.

                The eight briefs published so far all used four words, give
                or take one.
  sections      array naming only the sections that carried an item today,
                each one of: TOOLING | TEARDOWN | CREDITS | PRICING.
                A section the brief skipped does not appear.
  items         the day's items, ranked
  readThrough   what this changes for a team, one or two sentences
  sources       attribution, surveyDate, disclaimer

6.2 ITEM FIELDS

  name          the tool, product or programme
  kind          one of: tooling | teardown | credits | pricing
  version       REQUIRED when kind is "tooling". Must NOT appear on any other
                kind. Never an empty string.
  releaseDate   YYYY-MM-DD, that version's own release date
  licence       REQUIRED when kind is "tooling". Read from the LICENSE file or
                the repository sidebar, or the exact string
                "licence not confirmed". Never inferred.
  platform      the OS or runtime support exactly as the project states it
  repoUrl       the repository root
  releaseUrl    REQUIRED when kind is "tooling". Must be
                https://github.com/<org>/<repo>/releases/tag/<tag>
                for the exact version reported — never the /releases index.
                Must NOT appear on any other kind.
  productUrl    for kind "teardown" or "credits", the product or programme page
  price         the public price exactly as published, for example
                "Teams $250/month". Omit entirely when no price is public.
  priceUrl      REQUIRED whenever price is present — the page the price was
                read from. Omit both together, never one alone.
  what          one line on what it does
  whyDifferent  one line on why it differs from what already exists
  isLead        true on EXACTLY ONE item in the whole file — the one the
                thesis rests on — and false on every other
  source        "Source: NAME, D Mon YYYY - URL", the page carrying the fact

Omit an optional field entirely rather than sending an empty string or null.

6.3 THE SOURCES BLOCK

  attribution   every source used, with dates and page URLs
  surveyDate    the run date, YYYY-MM-DD
  disclaimer    reproduced EXACTLY, character for character:
                "Independent technology analysis published by Dockfinity. Every release, version, licence and figure carries the primary source it was read from."

6.4 SHAPE

{
  "date": "YYYY-MM-DD",
  "title": "short thesis headline",
  "summary": "one or two sentences for meta tags and RSS",
  "thesis": "the connecting thread in one sentence",
  "accentPhrase": "a phrase copied out of thesis",
  "sections": ["TOOLING", "TEARDOWN"],
  "items": [
    {
      "name": "display name",
      "kind": "tooling",
      "version": "0.30.0",
      "releaseDate": "2026-09-08",
      "licence": "MIT",
      "platform": "Python 3.10+; the project does not state an OS matrix",
      "repoUrl": "https://github.com/org/repo",
      "releaseUrl": "https://github.com/org/repo/releases/tag/v0.30.0",
      "what": "one line on what it does",
      "whyDifferent": "one line on why it differs",
      "isLead": true,
      "source": "Source: NAME, D Mon YYYY - URL"
    }
  ],
  "readThrough": "what this changes for a team",
  "social": {
    "linkedin": "<the LinkedIn caption>",
    "instagram": "<the Instagram / WhatsApp caption>",
    "x": "<the X caption, WITHOUT the hashtags>",
    "hashtags": ["#Example", "#AnotherOne"]
  },
  "sources": {
    "attribution": "every source used, with dates and page URLs",
    "surveyDate": "YYYY-MM-DD",
    "disclaimer": "Independent technology analysis published by Dockfinity. Every release, version, licence and figure carries the primary source it was read from."
  }
}

6.5 WHAT THE VALIDATOR REJECTS

The site runs validateDiscoveryBrief on every file and FAILS THE BUILD rather
than publishing a bad one. It matches text, not intent, so these are the
literal strings — avoid producing them rather than discovering them at deploy.

  Confidential:
    "shipped since last run"   "Total: N / 25"
    "could a solo developer"   "can a solo developer"
    "in under two weeks"       "under 2 weeks"
    "the hard part is"
    "we are adopting"          "we will be adopting"
    "we are claiming"          "we will be claiming"
    "we plan to build"
    "clone this"  "clone it"  "clone the core"
    "rebuild this"  "rebuild it"  "rebuild the core"
  Method:
    "confirmed at run time"    "searches run"    "searches were run"
    "searches returned"        "recomputed"      "not publicly verified"
    "[UNVERIFIED]"
  Pipeline leakage:
    "render this as"  "render it as"
    "do not include"  "do not use"  "do not add"  "do not render"
    "do not display"  "treat this as"  "treat it as"

  Structural:
    a tooling item without a version, a licence, or a /releases/tag/ releaseUrl
    a version or releaseUrl on a non-tooling item
    a price without a priceUrl
    zero, or more than one, isLead
    an accentPhrase that does not appear verbatim inside thesis
    an unknown kind or section
    a date that is not YYYY-MM-DD
    a disclaimer that is not the exact string above
    a caption over its limit, or an X caption carrying a URL or bare domain

Only verified items enter the JSON. Anything you could not confirm stays out.


7. THE VISUAL
--------------------------------------------------------------------------

You do not draw it and you do not render it.

The image is produced by the website's own workflow, from the JSON you file,
using the renderer in this repository. This is deliberate: the renderer used
to be run inside the task, and on 17 September 2026 a Metal Dock run lost an
entire day's brief because a fetch failed inside the sandbox. A layout is code
and belongs where it can be reviewed and versioned.

So: no canvas sizes, no colours, no type scale, no column widths, no card
geometry, no clearance figures, no spacing arithmetic. None of it is your
concern and none of it can block the brief.

The two things you do owe the image are ordinary content rules:

  - accentPhrase is a phrase that already exists in the thesis sentence,
    three to five words long
  - no method language anywhere, because it would be printed
  - one, two or three items, never four

WHAT THE IMAGE COMFORTABLY HOLDS. These are not limits the renderer checks
one by one; they are the sizes the eight published briefs actually used, and
the layout was built around them. Write to these and the image renders. Write
far past them and the column overfills and the day is refused.

  thesis         38 to 56 characters   (58 is the hard ceiling)
  accentPhrase   3 to 5 words          (enforced)
  readThrough    225 to 324 characters
  what           80 to 200 characters per item
  whyDifferent   120 to 350 characters per item
  platform       20 to 65 characters


8. SELF-CHECK
--------------------------------------------------------------------------

Carry these out literally and report them honestly. A check you did not
actually perform is reported as not performed, never as a pass. Reporting a
pass on a check you did not run is worse than reporting a failure.

  1. Every item is shipped and usable, not announced.
  2. Every item was researched in this run. Nothing is carried over from
     memory of an earlier run.
  3. Every tooling item has a version, a licence, and a /releases/tag/ URL for
     that exact version, each read from a page that was opened.
  4. No non-tooling item carries a version or a releaseUrl.
  5. Every price was read on the page cited for it, and carries the whole
     ladder. Every price has a priceUrl.
  6. No placeholder stands in for a figure anywhere.
  7. Exactly one item has isLead true. Print the item's name.
  8. accentPhrase appears verbatim inside thesis. Print both.
  8a. The thesis is 58 characters or fewer. Print the count.
  8b. accentPhrase is three to five words and appears exactly once in the
      thesis. Print the phrase and its word count.
  8c. There are two or three items, never one. Print the count.
  9. sections names only the sections that carried an item today.
 10. The disclaimer matches the required string character for character.
 11. Nothing from the confidential, method or pipeline-leakage lists appears
     anywhere in the JSON or the captions.
 12. Caption lengths, measured on the caption alone: x at most 280, instagram
     at most 2200, linkedin at most 3000. Print the X count.
 13. The X caption carries no URL and no bare domain. Print the count of URLs
     found, which must be nought.
 14. The JSON parses.

Print "Checks: PASS" on one line only if every check passed or is genuinely
not applicable.


9. FILING
--------------------------------------------------------------------------

The production route begins when the clock opens a GitHub issue titled
"research: YYYY-MM-DD". The repository workflow then owns the whole run:

  1. The repository collects current primary release data from GitHub's public
     API without a paid search service.
  2. Gemini API 3.5 Flash-Lite analyses that evidence into a research dossier.
  3. A separate Gemini 3.5 Flash-Lite pass writes only the section 6 JSON under
     a response schema. It does not file mail, open issues, render or publish.
  4. The repository parses the JSON and runs its own validator and URL checks.
  5. The deterministic renderer makes the slide from validated JSON.
  6. Only after every check passes are the JSON and slide committed together.

The model's output is data for the validator, not an instruction to another
connector. Return exactly one JSON object and no route report, code fence,
commentary, self-check transcript or filing status.

If research finds fewer than two fully evidenced items, if the Gemini free
quota is exhausted, or if any validator, URL check or render fails, publish
nothing. Leave the dated issue open with the exact error so a human can see and
retry it. Never pad the brief and never weaken a check to make a run pass.

MANUAL RECOVERY. A human may still open "brief: YYYY-MM-DD" with the complete
section 6 JSON in its body. That skips Gemini but enters the same validation,
render and publication path. It is recovery, not the scheduled production
route.

FILING A DATE THAT IS ALREADY PUBLISHED. The website will not quietly replace
a brief that is already on the site. A different document for an existing date
is refused unless the manual recovery issue carries a line beginning
"CORRECTION:", outside the JSON fence, saying what is being corrected and why.
