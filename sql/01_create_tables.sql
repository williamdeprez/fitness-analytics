DROP TABLE IF EXISTS analytics.training_lift_day;

CREATE TABLE analytics.training_lift_day (
    date DATE,
    exercise TEXT,
    total_volume DOUBLE PRECISION,
    max_weight DOUBLE PRECISION,
    total_sets INTEGER,
    total_reps DOUBLE PRECISION,
    mean_rpe DOUBLE PRECISION,
    rpe_coverage DOUBLE PRECISION,
    stress_volume DOUBLE PRECISION,
    stress_rpe DOUBLE PRECISION,
    stress DOUBLE PRECISION,
    rolling_stress_7d DOUBLE PRECISION,
    rolling_stress_14d DOUBLE PRECISION,
    ewma_stress DOUBLE PRECISION,
    days_since_last_session DOUBLE PRECISION,
    ewma_smooth DOUBLE PRECISION,
    ewma_slope DOUBLE PRECISION,
    ewma_slope_smooth DOUBLE PRECISION,
    fatigue_phase TEXT,
    phase_group INTEGER,
    sessions_in_phase INTEGER,
    ewma_slope_magnitude DOUBLE PRECISION
);