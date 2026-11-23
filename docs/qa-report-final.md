# QA Report: Final Sprint, Machine Learning and AI

| | |
|---|---|
| **Section** | Local VM |
| **Test author(s)** | Dane DeGiacomo |
| **Tester** | Dane DeGiacomo (Local VM: author and tester) |
| **Commit tested** | `git rev-parse --short HEAD` = 37a8206 |
| **Dates** | Cases written: 2026-11-22 Cases run: TC-01 to TC-03 on 2026-11-22, the rest in Weeks 12 and 13 |

## How to use this report

1. **Write the test cases first,** in Week 11, before the work they test exists. A test written after the fact tends to test what was built instead of what was asked for.
2. **Write the expected result before you run anything.** If the actual result surprises you, that is a finding, not a typo to fix.
3. **Paste real output or point to an evidence file.** "Works" is not a result. A command and its output is.
4. **Cover every success criterion with at least one case,** and include at least one negative test (something that must fail or be blocked) and the rebuild proof of life.
5. **Re-run every case in Week 13** on the rebuilt VM and update the status. A case that passed only on the old VM is a rebuild gap.

---

## Test Cases

### TC-01: Dataset has enough labeled rows

| Field | Value |
|---|---|
| Criterion | 1 |
| Type | Positive |
| Preconditions | `~/ml-ai-venv` exists |
| Steps (exact commands) | `cd capstone/ml-ai && ~/ml-ai-venv/bin/python generate_data.py --seed 4031 --out data/incidents.csv`, then count rows, categories, and severities |
| Expected (written before running) | At least 5,000 rows, at least 4 categories, at least 3 severities, every row has a title |
| Actual (output or evidence path) | `capstone/ml-ai/evidence/dataset-summary.txt`: 6,000 rows, 5 categories, 4 severities |
| Status | [x] Pass [ ] Fail [ ] Blocked |
| Run on | Original VM: 2026-11-22 Rebuilt VM: ____ |
| Notes | Labels come from my own rules, see ARCHITECTURE.md |

### TC-02: Same seed gives the same file

| Field | Value |
|---|---|
| Criterion | 1 |
| Type | Positive / Rebuild |
| Preconditions | TC-01 passes |
| Steps (exact commands) | Run the generator twice with `--seed 4031` into two files and `sha256sum` both |
| Expected (written before running) | Both hashes are identical, and they match the committed `data/incidents.csv` |
| Actual (output or evidence path) | `capstone/ml-ai/evidence/dataset-hash.txt`: both runs `22613f90a7f773f83cc60daaeb485101b0f6bdd56f57e48c8a6708d462a52965` |
| Status | [x] Pass [ ] Fail [ ] Blocked |
| Run on | Original VM: 2026-11-22 Rebuilt VM: ____ |
| Notes | This is also the rebuild proof of life for the data |

### TC-03: Model beats the baseline and severity accuracy is at least 0.80

| Field | Value |
|---|---|
| Criterion | 2 |
| Type | Positive |
| Preconditions | TC-01 passes |
| Steps (exact commands) | `~/ml-ai-venv/bin/python train.py --data data/incidents.csv --models models --metrics metrics.json`, then read `metrics.json` |
| Expected (written before running) | Test set is 20% and not used in training; severity accuracy at least 0.80; macro F1 reported for both targets; baseline recorded and clearly lower |
| Actual (output or evidence path) | `capstone/ml-ai/metrics.json` and `evidence/train-output.txt`: severity accuracy 0.956 vs baseline 0.334; category accuracy 0.905 vs baseline 0.207; macro F1 category 0.905, severity 0.958 |
| Status | [x] Pass [ ] Fail [ ] Blocked |
| Run on | Original VM: 2026-11-22 Rebuilt VM: ____ |
| Notes | A high score here mostly shows the model learned my labeling rules. Week 13 adds a harder test set |

### TC-04: Service answers with category, severity, and confidence in under 500 ms

| Field | Value |
|---|---|
| Criterion | 3 |
| Type | Positive |
| Preconditions | `ml-ai-infer:v1` imported into k3s and deployed through `week-5/` |
| Steps (exact commands) | From inside the VM, `curl -s -o /dev/null -w "%{time_total}\n"` a POST with a title to the service 10 times, plus one full response with `jq` |
| Expected (written before running) | JSON with `category`, `severity`, and `confidence`; every one of the 10 timings under 0.5 s |
| Actual (output or evidence path) | `evidence/timing.txt` (Week 12) |
| Status | [ ] Pass [ ] Fail [ ] Blocked |
| Run on | Original VM: ____ Rebuilt VM: ____ |
| Notes | |

### TC-05: A pod that isn't allowed gets blocked

| Field | Value |
|---|---|
| Criterion | 4 |
| Type | Negative (must be blocked) |
| Preconditions | NetworkPolicy selecting `app: ml-infer` is deployed |
| Steps (exact commands) | Apply the memory-limited `blocked-client` pod, `kubectl exec blocked-client -- wget -T 5 -qO- http://<service>:<port>/health`, save output, delete the pod |
| Expected (written before running) | The request times out; a request from the `web` pod still gets an answer |
| Actual (output or evidence path) | `evidence/netpol-blocked.txt` (Week 12/13) |
| Status | [ ] Pass [ ] Fail [ ] Blocked |
| Run on | Original VM: ____ Rebuilt VM: ____ |
| Notes | |

### TC-06: Memory and image size stay inside the budget

| Field | Value |
|---|---|
| Criterion | 5 |
| Type | Positive |
| Preconditions | Service deployed |
| Steps (exact commands) | `kubectl describe deploy ml-infer`, add up memory limits of every pod I added; `docker image ls ml-ai-infer:v1` |
| Expected (written before running) | Added memory limits under 512Mi combined; image under 600 MB |
| Actual (output or evidence path) | `evidence/memory.txt`, `evidence/image-size.txt` (Week 12/13) |
| Status | [ ] Pass [ ] Fail [ ] Blocked |
| Run on | Original VM: ____ Rebuilt VM: ____ |
| Notes | |

### TC-07: Rebuild proof of life

| Field | Value |
|---|---|
| Criterion | Rebuild |
| Type | Rebuild |
| Preconditions | Fresh VirtualBox VM, repo cloned, README followed |
| Steps (exact commands) | Regenerate the dataset and compare `sha256sum`, load both models, send one request to the service |
| Expected (written before running) | Hash matches TC-02, the models load, one request returns a category, a severity, and a confidence |
| Actual (output or evidence path) | Week 13 |
| Status | [ ] Pass [ ] Fail [ ] Blocked |
| Run on | Original VM: n/a Rebuilt VM: ____ |
| Notes | |
