# Grant analysis reports

`python -m gov_contract_os grants screen` writes analyses into SQLite. In Phase 2 the CLI will also emit per-grant Markdown/CSV artifacts here:

```
reports/grants/<grant-id>/
├── opportunity-summary.md
├── eligibility-matrix.csv
├── application-checklist.md
├── narrative-outline.md
├── budget-framework.csv
├── questions-for-funder.md
├── risk-register.md
└── decision-memo.md
```

Everything in this directory is generated. Do not hand-edit — re-run the CLI instead.
