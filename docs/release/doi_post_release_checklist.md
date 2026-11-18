# DOI post-release checklist

This project will have two distinct archival records. Never guess a DOI from a
draft URL; use the DOI displayed on each published Zenodo record.

1. **Software record:** created from GitHub release `v1.0` through the Zenodo
   GitHub integration. It archives the repository, protocol, results, and paper.
2. **Raw-data record:** the manually uploaded shot-level data package. It has a
   separate dataset DOI because the large raw files are not in git.

## Before publishing either record

- Ensure the GitHub commit containing `.zenodo.json`, `CITATION.cff`, the final
  paper, and intended release files is pushed and is the `v1.0` release target.
- Confirm that Zenodo's GitHub integration is enabled for this repository before
  creating the GitHub release.
- Confirm both records name the creator as `Liu, Zhen-Jun` and describe all
  results as noisy simulation with no hardware run.
- Confirm the software record states the repository's dual licensing: code and
  tests under MIT; paper, documentation, figures, configurations, manifests,
  and results under CC BY 4.0.
- Confirm the raw-data record's file list and checksums against the committed
  result JSONs and run markers before publishing it.
- A DOI is not required inside `CITATION.cff` before the release. Zenodo can
  reserve either DOI before publication if cross-linking the two draft records
  in advance is useful; otherwise add the links immediately after publication.

## Record immediately after publication

### Software record

- Version DOI: `TODO`
- Concept DOI, if displayed: `TODO`
- DOI URL (`https://doi.org/...`): `TODO`
- Zenodo record URL: `TODO`
- Publication date: `TODO`
- GitHub release tag and commit: `v1.0` / `TODO`

### Raw-data record

- Dataset DOI: `TODO`
- DOI URL (`https://doi.org/...`): `TODO`
- Zenodo record URL: `TODO`
- Publication date: `TODO`

Open both DOI URLs in a private browser window and confirm that each resolves to
the intended record before editing repository or OSF metadata.

## Required metadata updates

1. Add the **software DOI** badge near the top of `README.md`, replacing
   `SOFTWARE_DOI`:

   ```markdown
   [![Software DOI](https://zenodo.org/badge/DOI/SOFTWARE_DOI.svg)](https://doi.org/SOFTWARE_DOI)
   ```

   Add a separate raw-data link nearby:

   ```markdown
   Raw shot-level data: [DATA_DOI](https://doi.org/DATA_DOI)
   ```

2. Add both records to the OSF project `y7m29` description:

   ```text
   Archived software, protocol, results, and paper:
   https://doi.org/SOFTWARE_DOI

   Archived raw shot-level data:
   https://doi.org/DATA_DOI
   ```

3. Add only the **software version DOI** to `CITATION.cff`:

   ```yaml
   version: "v1.0"
   doi: "SOFTWARE_DOI"
   date-released: YYYY-MM-DD
   ```

4. Cross-link the two Zenodo records with related identifiers. The software
   record should identify the raw-data record as supplementary data, and the
   raw-data record should identify the software record as the related software.
   Check the direction shown in Zenodo's form before publishing the metadata.

5. After the dataset DOI exists, add it as a related identifier in
   `.zenodo.json` for future software releases. Do not add a placeholder DOI.

Keep `.zenodo.json` as the authoritative metadata for software deposits. The
raw-data DOI belongs in links and related identifiers, not in the `doi` field of
`CITATION.cff`.

## Verification and handoff

- Confirm GitHub's default branch displays **Cite this repository** and that its
  APA/BibTeX export contains Zhen-Jun Liu, the correct title, release tag, and
  software DOI.
- Confirm both README links and both OSF links resolve to the intended records.
- Confirm the software archive contains the intended release commit and the
  dataset file list/checksums match the upload manifest.
- Commit and push only the post-release metadata update. Do not recreate or
  overwrite either published Zenodo record merely to add its DOI to the default
  branch.

Official references:

- [GitHub: About CITATION files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)
- [Zenodo: reserve a DOI](https://help.zenodo.org/docs/deposit/describe-records/reserve-doi/)
- [Zenodo: manage versions](https://help.zenodo.org/docs/deposit/manage-versions/)
