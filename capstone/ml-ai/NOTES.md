# Notes: every command that worked (Week 11)

Run from the repo root (`~/inet4031-degia005`) on my VM. This turns into the RUNBOOK later.

## Environment Checkpoint (Local VM block)

```bash
export KUBECONFIG=$HOME/.kube/config
kubectl get nodes
kubectl get pods -A
kubectl get networkpolicy
curl -s http://$(kubectl get service web -o jsonpath='{.spec.clusterIP}'):8080/health
./week-10/sql.sh
tail -5 ~/deploy.log
free -h
```

Saved to `capstone/ml-ai/evidence/environment-checkpoint.txt`.

## Tools

```bash
sudo apt-get install -y python3 python3-venv curl jq
python3 -m venv ~/ml-ai-venv
~/ml-ai-venv/bin/pip install --upgrade pip
~/ml-ai-venv/bin/pip install --no-cache-dir scikit-learn numpy scipy joblib flask
~/ml-ai-venv/bin/pip freeze > capstone/ml-ai/requirements.txt
```

Verify outputs saved to `capstone/ml-ai/TOOL-VERSIONS.txt`. k3d isn't part of the Local VM, so `kubectl get nodes` is there instead.

## Dataset (criterion 1)

```bash
cd capstone/ml-ai
~/ml-ai-venv/bin/python generate_data.py --seed 4031 --out /tmp/incidents-run1.csv
~/ml-ai-venv/bin/python generate_data.py --seed 4031 --out /tmp/incidents-run2.csv
sha256sum /tmp/incidents-run1.csv /tmp/incidents-run2.csv
cp /tmp/incidents-run1.csv data/incidents.csv
```

## Baseline and first model (criterion 2)

```bash
cd capstone/ml-ai
~/ml-ai-venv/bin/python train.py --data data/incidents.csv --models models --metrics metrics.json
```

Takes a couple of seconds on the CPU. Writes `metrics.json` and `models/category.joblib` + `models/severity.joblib`.

## Git

Branch `ml-ai-week-11`, pull request into `master`, merged after the three Deploy gate checks passed. Nothing in `week-5/` changed, so `deploy.sh` has nothing to apply.
