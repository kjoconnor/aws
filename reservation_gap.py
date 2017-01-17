from collections import Counter

from boto.ec2 import connect_to_region

REGION = 'us-east-1'

COUNTER_KEY_FMT = '{availability_zone},{instance_type}'

ec2 = connect_to_region(REGION)

running_instance_counter = Counter()
current_reservations_counter = Counter()


def get_instances(ec2):
    reservations = ec2.get_all_instances(filters={
        'instance-state-name': 'running',
    })

    instances = []

    for reservation in reservations:
        instances.extend(reservation.instances)

    return instances


instances = get_instances(ec2)

for instance in instances:
    counter_key = COUNTER_KEY_FMT.format(
        availability_zone=instance.placement,
        instance_type=instance.instance_type,
    )

    running_instance_counter[counter_key] += 1

for reservation in ec2.get_all_reserved_instances(filters={'state': 'active'}):
    counter_key = COUNTER_KEY_FMT.format(
        availability_zone=reservation.availability_zone,
        instance_type=reservation.instance_type,
    )

    current_reservations_counter[counter_key] += reservation.instance_count

running_non_reserved_instances = (
    running_instance_counter - current_reservations_counter
)

reservations_not_in_use = (
    current_reservations_counter - running_instance_counter
)

print 'Reservation Gaps'
print 'availability_zone, instance_type, count'
for counter_key, count in sorted(running_non_reserved_instances.items(), key=lambda x: x[1], reverse=True):
    availability_zone, instance_type = counter_key.split(',')
    print ','.join([availability_zone, instance_type, str(count)])
print '-------------------------------------------'

print 'Unused Reservations'
print 'availability_zone, instance_type, count'
for counter_key, count in sorted(reservations_not_in_use.items(), key=lambda x: x[1], reverse=True):
    availability_zone, instance_type = counter_key.split(',')
    print ','.join([availability_zone, instance_type, str(count)])
print '-------------------------------------------'
