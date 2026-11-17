# DOI post-release checklist

This checklist is intentionally unfilled. Never guess a DOI from a draft URL.
Use the DOI displayed on the published Zenodo record.

## Before publishing the Zenodo record

- Ensure the GitHub commit containing `.zenodo.json`, `CITATION.cff`, the final
  paper, and intended release files is pushed and is the release target.
- Confirm the Zenodo creator is `Liu, Zhen-Jun`, the title matches
  `.zenodo.json`, and the evidence description says noisy simulation with no
  hardware.
- A DOI is not required inside `CITATION.cff` for this release. If a DOI must
  appear inside the archived files, Zenodo supports reserving one before
  publication; otherwise leave it absent until the record is published.

## Record immediately after publication

- Version DOI: `TODO`
- DOI URL (`https://doi.org/...`): `TODO`
- Zenodo record URL: `TODO`
- Publication date: `TODO`
- GitHub release tag and commit: `TODO`

Open the DOI URL in a private browser window and confirm that it resolves to
the intended record before editing repository metadata.

## Three required updates

1. Add this badge near the top of `README.md`, replacing `DOI_VALUE`:

   ```markdown
   [![DOI](https://zenodo.org/badge/DOI/DOI_VALUE.svg)](https://doi.org/DOI_VALUE)
   ```

2. Add to the OSF project `y7m29` description:

   ```text
   Archived software, protocol, results, raw-data package, and paper:
   https://doi.org/DOI_VALUE
   ```

3. Add the published version metadata to `CITATION.cff`:

   ```yaml
   version: "RELEASE_TAG"
   doi: "DOI_VALUE"
   date-released: YYYY-MM-DD
   ```

Keep `.zenodo.json` as the authoritative Zenodo deposit metadata. Do not add a
made-up DOI field there.

## Verification and handoff

- Confirm GitHub's default branch displays “Cite this repository” and that its
  APA/BibTeX export contains Zhen-Jun Liu, the correct title, release tag, and
  DOI.
- Confirm the README badge resolves, the OSF link resolves, and the Zenodo file
  list and checksums match the intended upload.
- Commit and push only the post-release metadata update; do not recreate or
  overwrite the published Zenodo record merely to add the DOI to the default
  branch.

Official references:

- [GitHub: About CITATION files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)
- [Zenodo: reserve a DOI](https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/)
- [Zenodo: manage versions](https://help.zenodo.org/docs/deposit/manage-versions/)
