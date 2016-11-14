# AWS Tools

A collection of tools I have for working with AWS.

## find_sla_issues.py

This will search back through your support case history and find cases where the first response from AWS came in after the SLA for the severity of the case had expired. For instance, if it's a `critical` case (now they call it `Business-critical system down`), this would highlight the case if AWS's response came in after 15 minutes of you opening it.

Right now it makes a best effort guess to see if a response was from AWS or you, and also doesn't trigger on open (not resolved) cases.

### Example
```
(aws)bigbox:~ kevin$ python find_sla_issues.py
display_id, severity, creation_timestamp, first_timestamp, response_time, sla, subject
1001, high, 2015-11-20 19:23:59, 2015-11-21 01:25:19, 6:01:20, 4:00:00, My Instances Are Too Good
1002, high, 2015-12-07 08:45:02, 2015-12-08 15:18:00, 1 day, 6:32:58, 4:00:00, My Instances Are Not Good
```
