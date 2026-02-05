library(tidyverse)

df <- read_csv("data/processed/training_lift_day_aggregates.csv")

bench <- df |>
  filter(str_detect(exercise, "bench press"))

bench

print(
  ggplot(bench, aes(x = date, y = ewma_stress, color = fatigue_phase)) +
    geom_line(linewidth = 0.4) +
    geom_point(size = 1.2) +
    labs(
      title = "EWMA Stress Over Time for Bench Press",
      x = "Date",
      y = "EWMA Stress",
      color = "Fatigue Phase"
    ) +
    theme_minimal()
)

ggsave(
  filename = "assets/figures/bench_press_ewma_stress.png",
  width = 8,
  height = 5,
  dpi = 150
)