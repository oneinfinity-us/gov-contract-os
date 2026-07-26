# Grant inbox

Drop grant announcements here as one folder per grant.

```
opportunities/grants/inbox/<slug>/
├── manifest.yaml   # required — structured metadata
└── *.pdf           # optional — source NOFO / RFA / RFP documents
```

Then run:

```powershell
py -3.12 -m gov_contract_os grants import opportunities/grants/inbox/<slug>/
py -3.12 -m gov_contract_os grants screen --nonprofit nonprofit --new
```

See [example-federal-grant/manifest.yaml](example-federal-grant/manifest.yaml) for the field schema.

In Phase 2, an LLM-assisted extractor will read the PDF and pre-fill the manifest for human review. For now, manifests are hand-authored.

## What NOT to put here

- Real EIN, banking, or PII from the funder's contact database beyond the public program officer contact.
- Any solicitation attachment that the funder marks as confidential.
- See [SECURITY.md](../../../SECURITY.md).
