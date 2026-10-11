# Operation, failure, and recovery

1. Pin the candidate's source/diff, dependency locks, configuration/artifact digests, environment/network, relevant packages/objects, and consumers in the original record.
2. Run this repository's CI and registered product commands; retain logs and summaries. Unregistered, unperformed, or failed gates must not be rewritten as passed.
3. An actual independent acceptor checks the exact combination and recovery. release-ready checks material completeness; final approval still follows original authorization.
4. Authorized executors perform production deployment, upgrades, initialization, and signing at the exact target and read back the result. This template does not automatically perform these operations.
5. For failures, record the original intent/digest, effects, paid resources, and checkpoints. Query the original result first when the outcome is unknown. A readback failure after success does not make the result unknown; do not repeat minting/upload/payment.
6. Frontends/SDKs can revert to pinned artifacts; do not assume on-chain state, transfers, or upgrades are reversible. Verify the actual actions covered by pause/resume and lawful exits individually.
7. Attach the handoff to the original record, retaining source candidates/evidence/remaining conditions. Release exclusive resources such as wallets, browsers, and deployment environments. Stopping an executor does not delete historical assets or paid resources.

Operational responsibilities, monitoring sources/windows/thresholds, recovery drills, and actual production targets remain pending until established. Without actual observations, do not claim monitoring is enabled.
Tooling repositories do not own business operational gates. Handle cross-repository failures for the exact affected combination and hand off to the relevant maintainer.

## Current owning regression activation candidate

Four owning tests use the accepted exact transport with real current Core fixtures. The registered `scripts/verify_current_consumer.py` reads current owning sources, pins modes/hashes and reviewed local dependency edges, and requires all 44 exact identities plus unchanged production and prior 407 Core test-build module bytes. This is local combined Core consumer regression. Standalone Market CI, independent hosted release, deployment and chain acceptance remain pending. Historical `verify_candidate.py` and its receipts remain historical; their independent 44-test result is not current verification.

Run `SUI_BINARY=<pinned-local-tool> MARKET_REGRESSION_OUTPUT=<new-isolated-output> python3 scripts/ci.py --product`. Optional relocated producer roots: `SOUL_ACT_ROOT`, `SOUL_ECOSYSTEM_ROOT`. Core remains actual consumer authority; the harness adds no production Core dependency to Market. `MARKET_OWNING_TEST_ROOT` is reserved for explicit isolated preactivation rehearsal; activation must use the actual repository default. All output and temporary compiler data stay below the new output directory, with denied networking and an empty isolated keystore.

The runner inventories selected compiler directories recursively, including initially empty or absent scripts and Core root examples/tests. It follows only the 13 reviewed producer aliases and rejects unknown/dangling/cyclic links or alternate owners. Phase CURRENT documents are source-CAS safety guards outside the product gate; changes to those documents do not require a Market CI/configuration release. All609 retained source hashes/modes and the exact four owning tests remain product pins.

Current combined regression inventories the consumed provider dev fixtures recursively for all selected packages. All220 existing provider dev files are pinned and staged; added/nested members refuse before compilation. This does not establish standalone release or deployed behavior.
