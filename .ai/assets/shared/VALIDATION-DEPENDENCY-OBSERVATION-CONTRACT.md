# Bounded Validation Dependency Observation Contract

## Purpose

This contract defines a first-phase, explicitly supported harness for observing
validator dependencies and comparing them with declared inputs. Observation is
lower-bound evidence. It never proves complete transitive closure, edits a
registry, removes an input, or makes validation evidence reusable.

The machine-readable contract is
`validation-dependency-observation.schema.yaml`. The source entrypoint is
`.ai/scripts/observe-validation-dependencies.py`.

## Supported Boundary

`in-process-python-callable/v1` loads one repository-relative Python entrypoint,
then observes one call to its named callable. The callable receives a bounded
string argument list and returns `0` or `None` on success.

The harness records these normalized dimensions:

| Dimension | Observed signal | Privacy-safe identity | Coverage |
| --- | --- | --- | --- |
| file | Python `open`, `io.open`, and `pathlib.Path.open` calls after target load | repository-relative path only | partial |
| subprocess | tokenized `subprocess.Popen` invocations | executable basename only | partial |
| Git | direct tokenized `git <subcommand>` invocations | `git:<subcommand>` | partial |
| environment | `os.getenv`, `os.environ.get`, and item access | variable name only | partial |
| runtime | active Python identity and direct repository-module imports | `python` and `module:<top-level-name>` | partial |

Every report keeps every dimension, even when its observed set is empty. No
dimension can report complete coverage under this version.

## Fail-Closed Comparison

The request declares sorted, unique dependencies for all five dimensions.
Repository file declarations may name a file or directory; a directory covers
observed descendants. Other declarations are exact identifiers.

- Any observed-but-undeclared dependency makes the observation decision
  `failed` within the representative harness boundary.
- Declared-but-unobserved dependencies are advisory. They are retained and are
  never removed automatically.
- An unsupported harness, untokenized shell command, target failure, unresolved
  subject, or incomplete observation boundary reports `blocked`.
- A `passed` decision means only that this execution observed no undeclared
  dependency. Its `closure_claim` remains `lower-bound-only` and
  `complete_transitive_closure` remains `false`.

The report is bound to the resolved repository `HEAD`, the canonical request
digest, and before/after tracked-status digests. A changed tracked status makes
the execution fail. Output is create-only beneath the ignored
`.dev/ai-context/local/validation/` root.

## Required Blind Spots

Every supported report names at least these blind spots:

- untaken branches;
- entrypoint imports and file reads completed before observation hooks;
- native extensions, direct operating-system calls, and child-process internals;
- environment or runtime dependencies not accessed by the representative path;
- provider and hosted state outside the local harness; and
- complete transitive dependency closure.

These blind spots cannot be converted to `complete` by a successful run.

## Fresh-Gate Boundary

Bounded observation is diagnostic input only. Current-head review-subject
binding, required hosted contexts, live provider admission, tag or Release
binding, and other inherently identity- or provider-sensitive operations stay
fresh. Independent-review validity remains content-addressed and is repeated
only when its content subject, criteria, or authority changes. Path filtering
or future evidence reuse must not make the fresh gates disappear.

## Privacy

Reports must not contain absolute paths, usernames, hostnames, environment
values, command arguments beyond the normalized Git subcommand, prompts,
tokens, credentials, or raw process output. Stable digests may authenticate
the request, subject, and tracked-status observations.
