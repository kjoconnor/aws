import logging

from datetime import datetime, timedelta

from boto.support import connect_to_region

AMZ_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'

AMZ_SLA = {
    'low': timedelta(hours=24),
    'normal': timedelta(hours=12),
    'high': timedelta(hours=4),
    'urgent': timedelta(hours=1),
    'critical': timedelta(minutes=15),
}

logging.basicConfig(level=logging.ERROR)

support = connect_to_region('us-east-1')


class SupportCommunication(object):
    def __init__(self, data):
        self.submitted_by = data['submittedBy']
        self.creation_time = datetime.strptime(
            data['timeCreated'],
            AMZ_TIME_FORMAT,
        )
        self.body = data['body']

    @property
    def customer_initiated(self):
        if self.submitted_by == 'Amazon Web Services':
            return False
        return True


class SupportCase(object):
    def __init__(self, data):
        self.case_id = data['caseId']
        self.display_id = data['displayId']
        self.severity = data['severityCode']
        self.subject = data['subject']
        self.creation_time = datetime.strptime(
            data['timeCreated'],
            AMZ_TIME_FORMAT,
        )
        self.communications = self._get_communications()

    def __unicode__(self):
        if self.customer_initiated:
            initiated = 'Customer Initiated'
        else:
            initiated = 'Amazon Initiated'

        return 'SupportCase ({display_id}/{initiated}) - <{subject}>'.format(
            display_id=self.display_id,
            initiated=initiated,
            subject=self.subject,
        )

    def __repr__(self):
        return self.__unicode__()

    def _get_communications(self):
        logging.info('Collecting communications for case %s', self.case_id)
        parsed_communications = []
        raw_communications = support.describe_communications(
            case_id=self.case_id,
            max_results=100,
        )

        for communication in raw_communications['communications']:
            parsed_communications.insert(
                0,
                SupportCommunication(data=communication),
            )

        return parsed_communications

    @property
    def customer_initiated(self):
        return self.communications[0].customer_initiated

    @property
    def first_response(self):
        return next((
            communication
            for communication in self.communications
            if not communication.customer_initiated
        ),
            False,
        )

    @property
    def first_response_time(self):
        try:
            return self.first_response.creation_time - self.creation_time
        except AttributeError:
            return False

    @property
    def sla_violated(self):
        # if created by amazon, skip
        if not self.customer_initiated:
            return False

        if not self.first_response:
            # We could probably also check existing cases without
            # a response, but not important for now
            return False

        if self.first_response_time > AMZ_SLA[self.severity]:
            logging.info(
                'SLA broken: case created at %s, first Amazon response at %s',
                self.creation_time,
                self.first_response.creation_time,
            )
            return True

        return False

if __name__ == '__main__':
    logging.info('Collecting cases...')
    cases = []
    raw_cases = support.describe_cases(
        after_time=datetime.strftime(
            datetime.utcnow() - timedelta(days=365),
            AMZ_TIME_FORMAT,
        ),
        include_resolved_cases=True,
        max_results=100,
    )

    for case in raw_cases['cases']:
        cases.append(SupportCase(data=case))

    print('display_id, severity, creation_timestamp, first_timestamp, response_time, sla, subject')
    for case in cases:
        if case.sla_violated:
            response_time = case.creation_time
            print(
                '{display_id}, {severity}, {creation_ts}, '
                '{first_response_ts}, {response_time}, '
                '{sla_time}, {subject}'.format(
                    display_id=case.display_id,
                    severity=case.severity,
                    creation_ts=case.creation_time,
                    first_response_ts=case.first_response.creation_time,
                    response_time=str(case.first_response_time).replace(',', ''),
                    sla_time=str(AMZ_SLA[case.severity]).replace(',', ''),
                    subject=case.subject,
                )
            )
