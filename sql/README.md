# SQL Layer – Fitness Analytics

This folder defines the PostgreSQL schema used for analytics and modeling.

## Setup Instructions

1. Start PostgreSQL
2. Create the database:
   ```sql
   CREATE DATABASE fitness_analytics;
3. Connect
   ```sql
   psql -d fitness_analytics
4. Run SQL files in this order 
   ```sql
   \i sql/00_create_schema.sql
   \i sql/01_create_tables.sql
   \i sql/02_indexes.sql
   \i sql/03_load_data.sql
