# soul-market

MARKET: Optional order and settlement service. Orders, valid delivery relationships, settlement, cancellation, and service income.

Maintenance entry points: [MODULE](MODULE.md), [Agent boundaries](AGENTS.md), [Compatibility](COMPATIBILITY.md), [Operation and recovery](RUNBOOK.md). Machine configuration: [module.json](module.json).

Actual construction: the independent Market candidate has been extracted; production build and 44/44 cross-package VM checks passed; consumers have not switched. See module.json for detailed evidence status; independent deployment and remote CI have not been accepted.
Recommended role: CIPHER; the original Owner is unchanged. Unconfirmed actual maintainers and independent acceptors remain pending; role names are not accounts or audit qualifications.

```sh
python3 scripts/ci.py
python3 scripts/ci.py --product
python3 scripts/ci.py --release-ready
```

Default CI checks maintenance contracts; `--product` refuses to pass when product commands are unregistered. Readiness gates do not deploy or sign.

[Detailed Market extraction results and release boundaries](EXTRACTION_STATUS_CN.md).

## Current checkpoint

See [construction status](CONSTRUCTION_STATUS.md) for current evidence, blockers, recovery material and remote coordination. This checkpoint is not a release.
