# 📘 Data Dictionary — Fitness & Recovery Analytics

This document describes the schema and semantics of all engineered features produced by the data pipeline.  
Each row in the primary dataset represents **one exercise performed on one calendar day**.

---

## 🗓️ Temporal & Identity Columns

### `date`
- **Type:** `date`
- **Description:**  
  Calendar date on which the exercise was performed.
- **Usage:**  
  Time-series analysis, rolling windows, recovery modeling.

---

### `exercise`
- **Type:** `string`
- **Description:**  
  Normalized exercise name (e.g., `"bench press"`, `"squat"`).
- **Usage:**  
  Groups workload, fatigue, and progression by lift.

---

## 🏋️ Raw Training Volume Metrics

### `total_volume`
- **Type:** `float`
- **Definition:**  
  \[
  \sum (\text{weight} \times \text{reps})
  \]
- **Description:**  
  Total mechanical work performed for the exercise on that day.
- **Usage:**  
  Baseline workload indicator independent of subjective effort.

---

### `max_weight`
- **Type:** `float`
- **Description:**  
  Heaviest load lifted for the exercise on that day.
- **Usage:**  
  Proxy for daily strength performance.

---

### `total_sets`
- **Type:** `int`
- **Description:**  
  Number of working sets performed.
- **Usage:**  
  Measures session density and workload distribution.

---

### `total_reps`
- **Type:** `int`
- **Description:**  
  Total repetitions completed across all sets.
- **Usage:**  
  Volume-based hypertrophy analysis.

---

## 🧠 RPE & Effort Metrics

### `mean_rpe`
- **Type:** `float`
- **Description:**  
  Mean Rate of Perceived Exertion across all sets where RPE was recorded.
- **Usage:**  
  Subjective training intensity estimation.

---

### `rpe_coverage`
- **Type:** `float` (0–1)
- **Description:**  
  Fraction of sets that include an RPE value.
- **Usage:**  
  Determines whether stress calculations rely on RPE-weighted or volume-only metrics.

---

## 🔥 Stress Modeling

### `stress_volume`
- **Type:** `float`
- **Definition:**  
  Equal to `total_volume`.
- **Description:**  
  Objective workload-based stress metric.
- **Usage:**  
  Fallback stress signal when RPE is unavailable.

---

### `stress_rpe`
- **Type:** `float`
- **Definition:**  
  \[
  \text{total_volume} \times \text{mean_rpe}
  \]
- **Description:**  
  Combines mechanical work with perceived effort.
- **Usage:**  
  Fatigue-aware stress estimation.

---

### `stress`
- **Type:** `float`
- **Description:**  
  Unified stress metric:
  - Uses `stress_rpe` when RPE data exists  
  - Otherwise falls back to `stress_volume`
- **Usage:**  
  Primary training stress signal throughout the pipeline.

---

## ⏳ Accumulated Load & Fatigue Memory

### `rolling_stress_7d`
- **Type:** `float`
- **Description:**  
  Sum of stress over the previous 7 training days for the exercise.
- **Usage:**  
  Short-term fatigue accumulation indicator.

---

### `rolling_stress_14d`
- **Type:** `float`
- **Description:**  
  Sum of stress over the previous 14 training days.
- **Usage:**  
  Medium-term workload exposure.

---

### `ewma_stress`
- **Type:** `float`
- **Description:**  
  Exponentially Weighted Moving Average of `stress`.
- **Usage:**  
  Models latent fatigue by weighting recent sessions more heavily.

---

## 🕒 Recovery Timing

### `days_since_last_session`
- **Type:** `float`
- **Description:**  
  Number of days since the exercise was last performed.
- **Usage:**  
  Captures recovery time and training frequency effects.

---

## 📉 Fatigue Dynamics (Second-Order Features)

### `ewma_smooth`
- **Type:** `float`
- **Description:**  
  Second-order smoothing of `ewma_stress`.
- **Usage:**  
  Reduces noise and clarifies long-term fatigue trends.

---

### `ewma_slope`
- **Type:** `float`
- **Description:**  
  First difference of `ewma_smooth`.
- **Usage:**  
  Measures directional change in fatigue (increasing vs decreasing).

---

### `ewma_slope_smooth`
- **Type:** `float`
- **Description:**  
  Smoothed version of `ewma_slope`.
- **Usage:**  
  Stabilizes fatigue phase classification.

---

### `ewma_slope_magnitude`
- **Type:** `float`
- **Definition:**  
  Absolute value of `ewma_slope`
- **Description:**  
  Rate of fatigue change regardless of direction.
- **Usage:**  
  Distinguishes sharp vs gradual fatigue transitions.

---

## 🔄 Fatigue Phase Classification

### `fatigue_phase`
- **Type:** `categorical`
- **Values:**
  - `accumulating` — fatigue increasing  
  - `recovering` — fatigue decreasing  
  - `stable` — fatigue plateau
- **Usage:**  
  Discrete representation of training state.

---

### `phase_group`
- **Type:** `int`
- **Description:**  
  Identifier for contiguous blocks of the same fatigue phase.
- **Usage:**  
  Enables duration-based phase aggregation.

---

### `sessions_in_phase`
- **Type:** `int`
- **Description:**  
  Number of consecutive training sessions spent in the current phase.
- **Usage:**  
  Measures phase depth (e.g., prolonged accumulation).

---

## 🧠 Design Notes

- Features are engineered to be **physiologically interpretable**
- Pipeline separates:
  - Feature creation
  - Aggregation
  - Modeling
- All changes to this schema should be **model-driven and intentional**

---

