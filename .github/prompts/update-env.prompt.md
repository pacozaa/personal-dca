---
name: update-env
description: Update Environment
---

When update environment variables, 
1. update the `.env.example` file with the new variable and its description. 
2. update the `.github/workflows/dca-stock-analyze.yml` file to include the new variable as a secret if necessary.
3. update the `docs/github-action-secrets.md` file to include the new variable in the list of required or optional secrets, along with its description and example value.