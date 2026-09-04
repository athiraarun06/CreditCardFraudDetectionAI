# Viva / Interview Questions & Answers

## Machine Learning

**Q: Why SMOTE instead of just using class weights?**
Class weights change the loss function's penalty but don't change what the model *sees* during
training — with a 2-3% fraud rate, a model can still learn almost nothing about the minority class
structure. SMOTE synthesizes new minority-class samples along feature-space neighbors, giving the
model more examples to learn fraud patterns from. This project uses SMOTE on the training split
only (never the test split, to avoid leaking synthetic patterns into evaluation) and supports
class weights as a complementary technique in the model configs.

**Q: Why did you optimize threshold by cost instead of just using 0.5 or maximizing F1?**
In fraud detection, a missed fraud (false negative) costs far more than a false positive (an
annoying manual review). `optimize_threshold_by_cost()` in `train.py` sweeps thresholds and picks
the one minimizing `FN×cost_fn + FP×cost_fp`, with `cost_fn` set much higher — this produces a
threshold that trades some false positives for much better fraud recall, matching how a real bank
would tune its system.

**Q: Why combine a rule engine with the ML model instead of relying on the model alone?**
Three reasons: (1) explainability — regulators and fraud analysts need a clear "why" a hard rule
gives instantly, (2) responsiveness — a new fraud pattern (e.g. a specific merchant getting
compromised) can be blocked immediately by adding a rule, without waiting for a retrain, and
(3) guardrails — rules act as a floor so a known-bad pattern is never missed even if the model's
probability happens to be borderline. `combine_scores()` blends them as
`1 - (1-ml_prob)×(1-rule_score)` so either signal alone can push the combined score up.

**Q: How do you prevent data leakage in feature engineering?**
`engineer_features()` only derives features from information available *at transaction time*
(the transaction's own fields, and behavior counters like previous_transactions/txns_last_hour
that are computed from history *before* this transaction). No feature is derived from the label,
and SMOTE/scaling are fit only on the training split, then applied (not re-fit) to the test split.

**Q: Why is ROC-AUC used to pick the best model instead of accuracy?**
With ~97% of transactions being legitimate, a model that predicts "not fraud" for everything gets
97% accuracy while being useless. ROC-AUC (and PR-AUC, which is even more informative under class
imbalance) measures ranking quality across all thresholds, which is what actually matters for a
system where the operating threshold is tuned separately.

## System Design

**Q: Why SQLite by default instead of requiring PostgreSQL?**
Zero setup friction — a reviewer or grader can clone the repo and run it with no external
dependencies. `DATABASE_URL` swaps to PostgreSQL with no code changes (`app/core/database.py`
builds the SQLAlchemy engine from whichever URL is provided, with SQLite-specific connect args
applied conditionally).

**Q: How does the rate limiter work, and why not just use a library?**
It's a small in-memory sliding-window counter per client IP (`app/core/rate_limit.py`) — enough to
demonstrate the concept and protect a single-process demo deployment. A production, multi-instance
deployment would swap this for a Redis-backed limiter (noted in the module's docstring) since
in-memory state doesn't share across processes/machines.

**Q: Why store both `ml_probability` and `rule_score` separately from the combined `probability`?**
Auditability. A fraud analyst reviewing a decision needs to see whether a transaction was flagged
because the model found it statistically unusual, because a hard rule fired, or both — collapsing
them into one number would make the system a black box.

## Frontend

**Q: Why build custom UI components instead of installing a component library?**
To keep the dependency footprint small and avoid version/config fragility for a project meant to
`npm install && npm run build` cleanly in any environment — the ShadCN-style components in
`components/ui/` are hand-built Tailwind primitives with the same visual language.

**Q: How does dark/light mode work without a UI framework's theming system?**
A `ThemeProvider` toggles a `.light` class on `<html>`; `index.css` defines dark-mode styles as the
default and light-mode overrides scoped under `html.light`, including explicit overrides for the
specific opacity-based utility classes (`text-white/60` etc.) used throughout the app.

## Trade-offs / Honest Limitations

**Q: What would you change for a real production deployment?**
Move the rate limiter to Redis; add a proper migrations tool (Alembic) instead of
`create_all()`; add role-based access control (analyst vs. admin) instead of a single user role;
stream transactions through a message queue instead of synchronous REST calls for very high
throughput; and retrain on a real, much larger labeled dataset rather than a synthetic one.
