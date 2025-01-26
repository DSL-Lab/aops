#!/bin/bash
set -e  # Exit if any command fails

# Default values
TEST_MODE="False"
START_DATE="2000-01"
END_DATE="2024-12"
ITEMS_RAW_PATH="../out/items_raw.jl"
ITEMS_RAW_FILTERED_PATH="../out/items_filtered.jl"

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --test_mode)
      TEST_MODE="$2"
      shift 2
      ;;
    --start_date)
      START_DATE="$2"
      shift 2
      ;;
    --end_date)
      END_DATE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--test_mode True|False] [--start_date YYYY-MM] [--end_date YYYY-MM]"
      exit 1
      ;;
  esac
done

echo "Running with:"
echo "  TEST_MODE   = $TEST_MODE"
echo "  START_DATE  = $START_DATE"
echo "  END_DATE    = $END_DATE"

# Navigate to the crawler directory
cd aops_crawler || { echo "Directory 'aops_crawler' not found."; exit 1; }

# Create output directory if it doesn't exist
mkdir -p ../out

# Run Scrapy crawler
AOPS_FEED_URI="${ITEMS_RAW_PATH}" scrapy crawl aops --set="ROBOTSTXT_OBEY=False" -a start_date="$START_DATE" -a test_mode="$TEST_MODE"

# Run the cleaning script
python clean_raw.py --start "$START_DATE" --end "$END_DATE" --input "$ITEMS_RAW_PATH" --output "$ITEMS_RAW_FILTERED_PATH"

echo "Done!"