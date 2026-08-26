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

`opus_rep02_A` / `opus_rep02_D` is a clean pilot pair, but it does not replace the
lost planned repetition. Protocol v1.2 adds `opus_rep06_A` / `opus_rep06_D` as the
documented replacement pair, preserving the target of five clean fresh Claude pairs.
The runner now atomically reserves a trial directory before issuing an API request
and fails closed rather than overwriting an artifact. No other direct-API pilot ID
was invoked more than once.
