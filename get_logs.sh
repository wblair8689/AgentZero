#!/bin/bash

# Get the ID of the most recent Cloud Build build
LATEST_BUILD_ID=$(gcloud builds list --limit=1 --sort-by=~finishTime --format='value(id)')

if [ -z "$LATEST_BUILD_ID" ]; then
  echo "Error: Could not find the latest build ID."
  exit 1
fi

echo "Attempting to fetch logs for build ID: $LATEST_BUILD_ID using 'gcloud builds log'..."

# Try the primary method first
gcloud builds log "$LATEST_BUILD_ID"

# Check the exit status of the gcloud builds log command
if [ $? -ne 0 ]; then
  echo "--------------------------------------------------------------------------------"
  echo "ERROR: Failed to fetch logs using 'gcloud builds log'."
  echo "This usually means the build is not configured to store logs in a GCS bucket."
  echo ""
  echo "RECOMMENDATION: View logs directly in the Google Cloud Console:"
  echo "1. Go to Cloud Build -> History"
  echo "2. Find and click on build ID: $LATEST_BUILD_ID"
  echo ""
  echo "Alternatively, configure a logsBucket in your build trigger or cloudbuild.yaml."
  echo "--------------------------------------------------------------------------------"
  
  # Optionally, uncomment the following lines to still attempt Cloud Logging 
  # as a fallback, although it might only show audit logs.
  # echo "Attempting secondary method using Cloud Logging (may only show audit logs)..."
  # gcloud logging read "resource.type=\"build\" AND resource.labels.build_id=\"$LATEST_BUILD_ID\"" --format=default --order=asc
else
    echo "--- Logs End ---"
fi

echo "Log fetching process complete." 