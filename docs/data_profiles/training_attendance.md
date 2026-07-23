# Training Attendance Data Profile

## Source files

- Meeting1 1.csv
- Meeting2 1.csv
- Meeting3 1.csv

## Source structure

Each source file contains three sections:

1. Summary
2. Participants
3. In-Meeting Activities

## Python responsibilities

- Detect file encoding and delimiter.
- Separate the three source sections.
- Preserve raw values.
- Add source file and source row metadata.
- Load data into the SOURCES schema.

## PL/SQL responsibilities

- Convert timestamps.
- Convert duration text to seconds.
- Validate participant records.
- Reconcile participant summaries with detailed activities.
- Load DIM_TRAINING.
- Load training participation into the fact table.

## Assumptions

- Meeting title and start time uniquely identify a training session.
- Email is the preferred participant identifier until DIM_EMPLOYEE
  mapping is confirmed.
- A difference of up to five seconds is accepted during duration
  reconciliation.