# Consumed contracts and verification combinations

Register actual consumers and dependencies in module.json.compatibility. An empty list means Gate0 is incomplete; it does not establish zero dependencies.
Configuration declares, and CI validates, eight fields per consumer, eight per dependency, and seven dependency categories.
Record the provider's exact interface, actual actions/types, schema/behavior, required effects, permissions/state, failure/exit/recovery, version/artifacts, and verification/migration evidence separately.

Review changes across four dimensions: types/formats/ABI, behavior, permissions/funds, and migration/old entry points.
Verify at least baseline/current, candidate/current, and candidate/candidate; add reverse combinations when consumption is bidirectional.
Pin source, dependency locks, configuration, and artifacts; reject floating latest and incorrect hashes. Reverification does not automatically require unrelated consumers to republish.
For unknown passive extensions, the target is 0 forced Market releases. Perform or explicitly reject funds/authorization/supply/transfer/content/exit obligations according to the contracts actually selected.

Register each actual package/SDK artifact, type origin, exact dependencies, and upgrade boundary in release_units. Disclose shared upgrade boundaries for shared UpgradeCaps.
Version numbers, directory splits, and compilable ABIs do not prove compatibility for funds, authorization, or recovery.

## Current owning regression activation candidate

Four owning tests use the accepted exact transport with real current Core fixtures. The registered `scripts/verify_current_consumer.py` reads current owning sources, pins modes/hashes and reviewed local dependency edges, and requires all 44 exact identities plus unchanged production and prior 407 Core test-build module bytes. This is local combined Core consumer regression. Standalone Market CI, independent hosted release, deployment and chain acceptance remain pending. Historical `verify_candidate.py` and its receipts remain historical; their independent 44-test result is not current verification.

Run `SUI_BINARY=<pinned-local-tool> MARKET_REGRESSION_OUTPUT=<new-isolated-output> python3 scripts/ci.py --product`. Optional relocated producer roots: `SOUL_ACT_ROOT`, `SOUL_ECOSYSTEM_ROOT`. Core remains actual consumer authority; the harness adds no production Core dependency to Market. `MARKET_OWNING_TEST_ROOT` is reserved for explicit isolated preactivation rehearsal; activation must use the actual repository default. All output and temporary compiler data stay below the new output directory, with denied networking and an empty isolated keystore.

The runner inventories selected compiler directories recursively, including initially empty or absent scripts and Core root examples/tests. It follows only the 13 reviewed producer aliases and rejects unknown/dangling/cyclic links or alternate owners. Phase CURRENT documents are source-CAS safety guards outside the product gate; changes to those documents do not require a Market CI/configuration release. All609 retained source hashes/modes and the exact four owning tests remain product pins.

Current combined regression inventories the consumed provider dev fixtures recursively for all selected packages. All220 existing provider dev files are pinned and staged; added/nested members refuse before compilation. This does not establish standalone release or deployed behavior.
