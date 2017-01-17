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
1002, high, 2015-12-07 08:45:02, 2015-12-08 15:18:00, 1 day 6:32:58, 4:00:00, My Instances Are Not Good
```

## reservation_gap.py

This will look at your currently running on demand instances, compare with your reservations, and show which instances are unreserved in the greatest quantity. It makes no guesses as to what might be good to reserve (it doesn't examine billing history or anything like that), just plainly states the difference at the time of running. It also shows the inverse - reservations that you have already paid for but aren't currently running.

### Example
```
(aws)bigbox:~ kevin$ python reservation_gap.py
Reservation Gaps
availability_zone, instance_type, count
us-east-1c,i2.4xlarge,12
us-east-1b,m4.large,1
us-east-1b,t2.medium,1
us-east-1c,m2.4xlarge,1
us-east-1e,m1.small,1
us-east-1d,t1.micro,1
us-east-1c,m4.xlarge,1
-------------------------------------------
Unused Reservations
availability_zone, instance_type, count
us-east-1d,m4.xlarge,1
-------------------------------------------
```
