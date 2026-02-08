-- Row counts
SELECT COUNT(*) AS total_rows
FROM analytics.training_lift_day;

-- Date coverage
SELECT
    MIN(date) AS start_date,
    MAX(date) AS end_date
FROM analytics.training_lift_day;

-- Lift count
SELECT
    COUNT(DISTINCT exercise) AS num_lifts
FROM analytics.training_lift_day;

-- Check for nulls in key columns
SELECT
    COUNT(*) FILTER (WHERE ewma_stress IS NULL) AS null_ewma,
    COUNT(*) FILTER (WHERE fatigue_phase IS NULL) AS null_phase
FROM analytics.training_lift_day;