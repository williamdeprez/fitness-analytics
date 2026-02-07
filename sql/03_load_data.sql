-- Replace PATH_TO_CSV with your local path
\copy analytics.training_lift_day
FROM 'PATH_TO_CSV/data/processed/training_lift_day_aggregates.csv'
DELIMITER ',' CSV HEADER;
