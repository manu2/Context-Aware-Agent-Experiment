# AAMAS 2027 anonymous manuscript package

This directory is the working **double-blind** package for the AAMAS 2027 Main
Technical Track. It is separate from the authored arXiv preprint and uses the
conference's mandatory LaTeX class without layout modifications.

## Official requirements captured here

- anonymous `aamas` class in `sigconf` format;
- eight content pages maximum, followed only by references;
- OpenReview submission ID in `\\acmSubmissionID` after abstract registration;
- PDF submission and optional anonymous supplementary ZIP (25 MB maximum);
- no author identity, personal repository URL, acknowledgements, or identifying
  PDF metadata in the review package.

The official template was downloaded from
`https://warwick.ac.uk/fac/sci/dcs/aamas2027/aamas_2027_template.zip` on
2026-09-11. SHA-256 of the downloaded archive:
`e70e88d36fd96db0777b9d00a1cd0bd1eecbbb28619e9e723dcf207a9bc6ce2a`.
The unmodified `aamas.cls`, `ACM-Reference-Format.bst`, and `by.pdf` files are
retained from that archive.

## Build

```bash
python -m pip install -r requirements.txt
python benchmarks/generate_aamas_figures.py
cd paper/aamas2027
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

Run the first two commands from the repository root. The TeX build requires a
complete LaTeX installation containing the packages loaded by the official
class (including `hyperxmp`). The generated charts are vector PDFs with embedded
fonts; the compiled manuscript is intentionally ignored as a build product.

All three 96-trajectory provider cohorts now pass their evidence audits, and the
manuscript contains the frozen 288-trajectory analysis. The release verifier
continues to block unresolved placeholders, missing submission metadata,
identity leaks, or package drift.

Draft verification:

```bash
python benchmarks/verify_aamas_submission.py --pdf paper/aamas2027/main.pdf
```

Build the deterministic anonymous supplement from the repository root:

```bash
python benchmarks/build_aamas_supplement.py
```

The resulting `paper/aamas2027/aamas2027_anonymous_supplement.zip` is a local
submission artifact and is not committed. It contains 288 effective trajectories
plus the preserved 32 pre-generation Gemini quota-interruption slots, omits
provider transport envelopes, and records per-member source and packaged hashes.

Final release verification (fail-closed on placeholders, submission ID, identity,
page limit, official-template hashes, PDF metadata, and supplementary ZIP size):

```bash
python benchmarks/verify_aamas_submission.py --release --pdf paper/aamas2027/main.pdf
```

## Anonymity and publication

The review PDF and supplementary ZIP must remain anonymous even though the
related arXiv preprint and development repository are public. The camera-ready
version may restore the author block and cite the public artifact. Do not include
raw credentials, local paths, API account identifiers, git remotes, or chat
exports in either package.
