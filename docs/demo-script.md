# Demo script

1. Explain that all data is synthetic and the API is local.
2. Run `pytest -m boundary` and show that Alice cannot read Bob's project.
3. Run `pytest -m rbac` and explain member versus viewer behavior.
4. Run `pytest -m side_effect` and show the read-back assertions for exports, links, and jobs.
5. Open `docs/authorization-matrix.md` and map each test to a rule.
6. Explain limitations: passing this suite is not a complete security assessment.
