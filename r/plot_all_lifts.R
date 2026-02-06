library(tidyverse)

# Paths
DATA_PATH <- "data/processed/training_lift_day_aggregates.csv"
PLOT_DIR <- "assets/figures/plots"

# Create PLOT_DIR if it doesn't exist
dir.create(PLOT_DIR, showWarnings = FALSE)

# Load data
df <- read_csv(DATA_PATH, show_col_types = FALSE)

df <- df |>
  mutate(date = as.Date(date))

lifts <- df |>
  distinct(exercise) |>
  pull(exercise)

for (lift in lifts) {
  lift_df <- df |>
    filter(exercise == lift) |>
    arrange(date) |>
    mutate(
      date_next = lead(date),
      ewma_next = lead(ewma_stress)
    ) |>
    drop_na(date_next, ewma_next)

  if (nrow(lift_df) == 0) {
    next
  }

  plt <- ggplot(lift_df) +
    geom_segment(
      aes(
        x = date,
        xend = date_next,
        y = ewma_stress,
        yend = ewma_next,
        color = fatigue_phase
      ),
      linewidth = 0.4
    ) +
    labs(
      title = paste("EWMA Training Stress -", str_to_title(lift)),
      x = "Date",
      y = "EWMA Stress",
      color = "Fatigue Phase",
    ) +
    theme_minimal() +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1),
      plot.title = element_text(face = "bold")
    )

  filename <- paste0(
    PLOT_DIR, "/",
    str_replace_all(str_trim(lift), " ", "_"),
    ".png"
  )

  ggsave(filename, plot = plt, width = 10, height = 5, dpi = 150)

  message("Saved plot for ", lift, " to ", filename)
}

message("All plots saved to ", PLOT_DIR)