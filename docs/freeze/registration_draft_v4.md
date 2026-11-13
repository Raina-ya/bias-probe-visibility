# Registration draft for protocol v4

Status: draft, 2026-11-12. Nothing is registered yet. The owner commits and
pushes first. The OSF files are then uploaded from that commit, and the owner
ticks the research-plan confirmation and clicks **Register**.

## Registration text (Summary field)

Data collection. No development, holdout, device-parameter or hardware data
exist. Protocol v3 (OSF j67wy) was registered earlier the same day; a pre-data
audit (docs/freeze/pre_data_defect_audit_v3.md) found definition conflicts that
made its primary endpoint uninterpretable, so v4 supersedes it before any data.
Design inputs come only from analytic derivations and population-level
computations on a disjoint software-test seed namespace (split 99).

Primary endpoint. Pooled change in false-certification rate (dFC) between the
CI-only rule and the bias-aware rule (designated probe per structure, alarms
calibrated on the clean null) at a fixed budget of 16,384 shots per
graph-cell-repeat, over seven error structures, 100 holdout graphs, and 32
repeats. The outcome is prespecified: improvement if the 2.5th percentile of
dFC is above 0; no decision problem at this budget if, otherwise, the 97.5th
percentile of the CI-only false-certification rate is below 0.01; inconclusive
otherwise.

Secondary. Coverage and abstention cost, interception, decision-flip-subset
detection, non-flip false alarms, the readout certificate, probe fraction, the
Proposition-1 hit rate, and agreement with the 42-cell visibility matrix (4
visible, 13 partial, 25 blind), reported separately for the invariant stratum
(23 cells) and the sensitive stratum (19 cells).

Power. Power v5 (non-circular) gives design probabilities of 0.69--0.78 for
"no decision problem" and at most 0.15 for "improvement". These are stated
before data.

Exclusions. No graph is excluded for its ideal gap, noisy result, or probe
behaviour; failed runs are retained.

Second lock. The development-derived strength map, thresholds, mismatch
report, error log, and timing pilot are committed and timestamped as
confirmatory_lock_v4.json before the holdout is run once.

Frozen at GitHub commit <commit>. Protocol docs/freeze/frozen_protocol_v4.md
(LF-normalized SHA-256 a7fc98fe53f540442783960b833fad7e575931e3c2f68c9e705af34a35243355); all files and
hashes are listed in docs/freeze/registration_draft_v4.md.

## Files to archive (LF-normalized SHA-256)

The first 47 rows are the `files` map of
`registration_v4.template.json`, which `split_guard_v4` checks.

| File | SHA-256 |
|---|---|
| `docs/freeze/frozen_protocol_v4.md` | `a7fc98fe53f540442783960b833fad7e575931e3c2f68c9e705af34a35243355` |
| `docs/theory/06_matrix_v4.csv` | `53a2048062b25e8f09c772c332c56c463fa32a6b24e9cb56a3d8ff129fad661b` |
| `docs/freeze/pre_data_defect_audit_v3.md` | `5ccd3e29521a22306fcd72b359436261fd85d3b259be6afe1474980b97ccf3f5` |
| `artifact_registry_v1.yaml` | `c45a49dce800f112dca06a06c9733776c352ae17cc2d8bc8d1c916a40d052ee9` |
| `artifact_registry_v4.yaml` | `38f8136723fed12dd21d61970d8b1bd2a6bcfba02c44c5c46ab97e6db44db8f4` |
| `src/provenance.py` | `94f4c8da4574460256798b50c87ecc3a66055a74abc027042d06195664279f12` |
| `src/provenance_v4.py` | `95333c6d7cf36017e57e940c54caeaf6c02b3fbc3f7ec56a316f9a5cedd25e39` |
| `src/hashing.py` | `265a1c4f037e871eb09698d899dbe5a7d3c329ffd2c6c1b393f9bc0a1865e68c` |
| `src/protocol_contract.py` | `fefe74173178fb3c6cd27016eab7536e5e533505470324b1e02bd0105ab52bea` |
| `src/manifest.py` | `fe659495ab5e32682d24b9af451d108f563b898990f3d7e8f34735e55bedb21b` |
| `src/manifest_v4.py` | `cae12c4c943d3046383b8d434460c149e31600013f5a8d61f5b0a0b4aceb9fab` |
| `src/split_guard.py` | `8c3533dd96dbe34cfbb20fdccd4a8343cae0ffbd58c0f79c325d5b0b6095662c` |
| `src/split_guard_v4.py` | `7443514448fd0f47d6df961bb894499c0f3ee01d8072980ce66a1602cf0dbd56` |
| `src/circuits.py` | `a42e8cd5dab26b6e693d7ac362399bb0482cc7173452d23cb727762869121e40` |
| `src/simulate.py` | `9023ec405e0c86ee65d9ef86d911eac62d397ff43ebf6858265bec4e5b83254b` |
| `src/channels.py` | `41684d3807ba192c293c02b02cfcdcaf2d4268e41e01d07e523209ff41eed008` |
| `src/probes.py` | `7c804d9e07c0be5ebc039dc482f8d773edddf710923580785e1120e6cf1506db` |
| `src/execution.py` | `8a3384564c3d22d3b47ab5edffe1f10ce410386216ad901c0ce24d9c687acc5d` |
| `src/reference.py` | `680d3b3bcf1e425520cd5046b026a1e2bc2d3465e23fd958f3c2cce1de68c439` |
| `src/cells_v4.py` | `86b689688fd39d26d9f411b9aa0c61622f653dfe9f7ef3fad00c42657deb73bd` |
| `src/strength_map.py` | `bd31f0d40f472621d34bddf6169eaa750d35f0bf49b96a34014641859f8b816a` |
| `src/alarm_calibration.py` | `eca0cba5ae09c7da80811b4111a92aa333f4244d92bb33c99235845052cd8d86` |
| `src/analysis.py` | `15d009ed84125ec6b98223b0292e446729937abe3d2b42142d899b57f4bee9c4` |
| `src/analysis_v4.py` | `fdf1221bdfb3813ae40a23a50126a2f3833d53992d8c5b5ae69d71e70910b4a3` |
| `src/runner.py` | `e8f496e9cbad95fe7285d188912919b2a409b8cc81367bfe28c19b0038e2e47e` |
| `tests/conftest.py` | `d9ac33decfc02fe9bc149e0a64ad1ba26a2426f88549067f678fe52d205200ff` |
| `tests/test_design_checks.py` | `32fd843a412f7ff42b69d55d2d9070e33f456176cb6858913fd9ccb86d8531cd` |
| `tests/test_execution.py` | `57a768c68078f69ef1081df6c873e1971c16f0b8678d9cb04a676c5f7d592082` |
| `tests/test_freeze_v3.py` | `2cf68bb196e5496e72fd05e5de17b46991d8cdd351877f85cee070f4bf2466ad` |
| `tests/test_power_analysis_v4.py` | `4da9189a5e5b5111d8fdc62575e2b61d9728e47b8ac623418423a69e94d6184b` |
| `tests/test_protocol_contract.py` | `9c937b539ba6cc0903d26b9dbfd0a1071be02a2b1fcafee62d9c8804361b3281` |
| `tests/test_protocol_v2.py` | `efc97371fb28910aae3e16543a174d53516a8264ae5ce376bc9827af981a4fb3` |
| `tests/test_protocol_v3.py` | `ab9c5e9f2d75945c80009c30a4f9ad845f8e9334a4946d11918bfbaf1ba88274` |
| `tests/test_provenance.py` | `29ba0fc0ed800e87c1ee62f145561bc879e97848411c6ca9760e5e3ce7b4529c` |
| `tests/test_registration_state.py` | `6b3226d4779c4bdc7163060381fff31691eefe80f51bd8bbef5e50d1c4a06f41` |
| `tests/test_v4.py` | `bea92f74b30d59621efcef7244ca95ce9d92bb9602c2fb93fded41457ac84941` |
| `docs/freeze/power_analysis_v5.md` | `86e0969026163c51db3df4273bef8794d6e9b4cb0e0864e2a44de44e2f5f43b0` |
| `docs/part2/execution_contract_v4.md` | `cb78e16ef2759b7061785bcc0fb5485a564cf6d77db32a46095adf613bb7773d` |
| `experiments/audit/p0_unresolved_audit.py` | `e3d59236ba18fad3011406c4f49142dc6c8f31261cc4c54e71462cf537d20134` |
| `experiments/audit/p4_construction_audit.py` | `12ab52fc88996b9cb6bc2553125de2ee5e629988d94e5a493528e2dc19541a1a` |
| `experiments/semantic/semantic_tests_v4.py` | `8acb4a700df64ca8813de606af0fb5f2319756a5ff471a061e34b6bcc13b5feb` |
| `experiments/semantic/semantic_tests_v4.csv` | `ae3340f023f77db9e80647ebf39f140c8ab7b38f6a747d39eaeb97463d50fca6` |
| `experiments/semantic/semantic_tests_v4_first_pass.csv` | `110aaa1f2e8c0e8da79ffa16fbb641f0bbfbf833d5ccf340328602afedc9f946` |
| `experiments/power/decision_design_inputs_v5.py` | `2d8793463423c648cb58e7bfbc7e145a6726680bcdcb35b8362b6eac1c6a0f89` |
| `experiments/power/decision_design_inputs_v5.csv` | `9deea18b81716c7456787c8ec9738d8c041320ecabfc58dea1a0fe0ac7a51125` |
| `experiments/power/run_power_analysis_v5.py` | `4f6ca6aa2f6d2b1b30827ef0d1a9cb4dcbaf7acff28ad7e31b359c2552b0c292` |
| `experiments/power/power_analysis_summary_v5.csv` | `75df9d07d2ccf52d6a6cc689d8146b34dbed8d3a9b3cb76e0de53899849fb6c8` |
| `docs/freeze/frozen_protocol_v4.sha256` | `ea1e1890b5a2c23d7ceaebbc129e691654c2873c0fd17f0b2a62296c7c738600` |
| `experiments/audit/p0_unresolved_log.txt` | `f174ebfd22eb9ae99442d6fc6ca004df69bf9c012a0f21fc566b20b6b50cb1a5` |
| `experiments/audit/p4_construction_log.txt` | `1873f26d78536d8480e9e9963a3e0ca1e04ce49c27cac3f428b1ba3c3b92812a` |
| `experiments/semantic/semantic_tests_v4_log.txt` | `cf5a33b158c8a0413c90875a682c62b2118066b3f738699dc6a8f41133dff476` |
| `experiments/semantic/semantic_tests_v4_first_pass_log.txt` | `2c653dd00fb31e74f9b343713377ed8ff7456c56ae8c6fe4b9ba7f043f69d035` |
| `experiments/power/power_analysis_raw_v5.csv` | `6eceed85e99d0c6df39859d524c3cd97dc862a1a38159fc518620b369b031d51` |
| `experiments/power/run_log_v5.txt` | `ee5a8e23003dc96324d947cb060329e67062aa1cf1dbace4f01cd300a1156dbc` |
| `docs/freeze/frozen_protocol_v3.md` | `50f68ae3455f544140f0bba114fef8b02feee7677eb676986f0efe0cf41ca513` |
