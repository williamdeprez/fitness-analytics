CREATE INDEX IF NOT EXISTS idx_training_lift_day_exercise
ON analytics.training_lift_day (exercise);

CREATE INDEX IF NOT EXISTS idx_training_lift_day_date
ON analytics.training_lift_day (date);
