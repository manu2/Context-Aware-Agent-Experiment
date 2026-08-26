# Direct-API Launch Anomalies

## `opus_rep01_A` duplicate invocation (2026-08-27)

During the first live Claude pilot, the execution channel reported completion before
the runner had finished writing its artifacts. A second invocation of the same
predeclared trial ID was therefore started. The original runner created the trial
directory only after the API response returned and allowed the later invocation to
overwrite the earlier response, generated script, profile, and metadata.

The surviving `opus_rep01_A` files are retained without alteration, but the missing
first response means `opus_rep01_A` and its paired `opus_rep01_D` **must not be used
for pilot summaries, effect estimates, or manuscript evidence**. This is not a model
or benchmark outcome.

The replacement is the unused, predeclared `opus_rep02_A` / `opus_rep02_D` pair. The
runner now checks for an occupied trial directory before issuing an API request and
fails closed rather than overwriting an artifact. No other direct-API pilot ID was
invoked more than once.
