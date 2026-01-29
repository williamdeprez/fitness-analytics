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

2. Lift-Day Aggregation
3. Stress modeling
Training stress is computed using two formulas:

4. Rolling Load & EWMA
To model accumulated fatigue over time, the pipeline computes:

- Rolling stress sums (7-day, 14-day)
- Exponentially Weighted Moving Average (EWMA)
$$
\text{EWMA}_t = \alpha \cdot x_t + (1 - \alpha) \cdot \text{EWMA}_{t-1}
$$