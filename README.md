# Fitness & Recovery Analytics
A Python-based training load and fatigue modeling project using real workout data.

## Project Goals
- Build a clean data pipeline for workout data.
- Engineer interpretable fatigue and stress features.
- Model long term load using EWMA

## Data Pipeline Overview

1. Data Ingestion

Currently, ingesting data from exported csv files from Strong workout tracking app with Future plans to record data directly. 

- cleaned,
- normalized, 
- standardized into a set-level dataset

Outputs:
`training_sets.normalized.csv`


Each row represents a single set with weight, reps, volume, and timestamp.

---

### 2. Lift-Day Aggregation

Set-level data is aggregated into **one row per exercise per day**.

For each lift-day, the following metrics are computed:

- total training volume
- maximum weight lifted
- total sets and reps
- mean RPE (when available)
- RPE coverage (fraction of sets with RPE recorded)

This aggregation provides the fundamental unit for fatigue modeling.

---

### 3. Stress Modeling

Training stress is defined using two complementary formulations:

- **Volume-based stress**  
  \[
  \text{Stress}_{\text{volume}} = \text{weight} \times \text{reps}
  \]

- **RPE-weighted stress** (when RPE is available)  
  \[
  \text{Stress}_{\text{RPE}} = \text{volume} \times \text{mean RPE}
  \]

When RPE is missing, the model falls back to volume-based stress.  
This ensures continuity while still leveraging subjective intensity when available.

---

### 4. Rolling Load & EWMA Fatigue Modeling

To model accumulated fatigue over time, the pipeline computes:

- Rolling stress sums (7-day, 14-day windows)
- Exponentially Weighted Moving Average (EWMA) of stress

The EWMA provides a smooth, memory-aware estimate of latent fatigue:

\[
\text{EWMA}_t = \alpha \cdot x_t + (1 - \alpha) \cdot \text{EWMA}_{t-1}
\]

Where:
- \( x_t \) is daily training stress
- \( \alpha \) controls how quickly past stress decays

EWMA captures long-term fatigue trends while suppressing short-term noise.

---

### 5. Time Since Last Session

For each exercise, the number of days since the previous session is computed.

This feature captures training frequency effects and distinguishes between acute fatigue and detraining.

---

### 6. Fatigue Phase Classification

Fatigue phases are inferred from the **smoothed derivative** of EWMA stress:

- **Accumulating**: fatigue increasing
- **Recovering**: fatigue decreasing
- **Stable**: fatigue relatively constant

This converts a continuous fatigue signal into interpretable training states aligned with real-world programming concepts.

---

### 7. Fatigue Phase Aggregation

Consecutive fatigue phases are grouped into contiguous blocks.

For each phase block, the model computes:

- start and end dates
- calendar duration
- number of training sessions
- mean fatigue and stress levels

This enables detection of prolonged accumulation, recovery periods, and phase transitions.

---

## Performance Modeling

To evaluate whether the fatigue model captures meaningful signal, a **linear regression** is trained to explain daily performance.

### Target Variable
- Maximum weight lifted per lift-day

### Features
- EWMA fatigue level
- Fatigue phase (categorical)
- Days since last session

Fatigue phase is one-hot encoded with a configurable baseline, allowing performance to be interpreted **relative to different training states**.

### Key Findings

- Stable fatigue phases are associated with substantially higher performance compared to accumulation phases
- Recovery phases show intermediate performance improvements
- EWMA fatigue magnitude explains within-phase performance variation
- Results are robust to baseline choice and align with known injury and ramp periods

This confirms that the fatigue signal captures meaningful latent structure rather than noise.

---

## Outputs

Processed datasets are written to `data/processed/`, including:

- `training_sets_normalized.csv`
- `training_lift_day_aggregates.csv`
- `training_global_daily_fatigue.csv`
- `fatigue_phase_summary.csv`

---

## Future Work

- Add EWMA slope magnitude as a feature
- Compare fatigue dynamics across different lifts
- Integrate nutrition and sleep data
- Build an interactive R Shiny dashboard for visualization
- Extend modeling to global, whole-body fatigue
- Add a complete PostgreSQL table lookup for individual's data.