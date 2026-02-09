## Possible error states:

Config file validation
Tell the user exactly which configuration variables are missing or invalid
Could not connect to the source system.
The source system did not respond before the timeout.
Authentication with the source system failed; credentials may be invalid or expired.
The requested payload was not found on the source system.
The source system returned no data.

The source returned a format different from what this job expects.
The payload’s expected fields were not found.
For CSV:

- The header row contained unexpected values and could not be processed.
- One or more data rows contained unexpected values and could not be processed.

For JSON:

- The timestamp or value key couldn’t be found with the specified JMESPath query

This job references a resource that no longer exists.
The file structure does not match the configuration.

HydroServer rejected some or all of the data.
The target datastream could not be found.
An internal system error occurred while processing the job.
The job stopped before completion.

## Possible warning states:

## Possible success states:
