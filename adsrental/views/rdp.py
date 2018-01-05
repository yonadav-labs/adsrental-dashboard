from django.views import View
from django.http import FileResponse, Http404
from django.conf import settings
import boto3

from adsrental.models.lead import Lead


class RDPDownloadView(View):
    def get_instance(self, data):
        for reservation in data.get('Reservations'):
            for instance in reservation.get('Instances'):
                if instance['State']['Name'] != 'running':
                    continue
                return instance

        return None

    def get(self, request, rpid):
        lead = Lead.objects.filter(raspberry_pi__rpid=rpid).first()
        if not lead:
            raise Http404()

        boto_client = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        ).client('ec2', region_name=settings.AWS_REGION)

        response = boto_client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    # 'Values': ['WP00000015'],
                    'Values': [lead.raspberry_pi.rpid],
                },
            ],
            # MaxResults=10,
        )

        instance = self.get_instance(response)

        if not instance:
            raise Http404()

        public_dns_name = instance.get('PublicDnsName')
        ip_address = instance.get('PublicIpAddress')

        lead.raspberry_pi.ec2_hostname = public_dns_name
        lead.raspberry_pi.current_ip_address = ip_address
        lead.raspberry_pi.save()

        # raise ValueError(public_dns_name, ip_address)

        lines = []
        lines.append('auto connect:i:1')
        lines.append('full address:s:{}:23255'.format(public_dns_name))
        lines.append('username:s:Administrator')
        lines.append('password:s:Dk.YDq8pXQS-R5ZAn84Lgma9rFvGlfvL')
        lines.append('')
        content = '\n'.join(lines)

        response = FileResponse(content, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{}.rdp"'.format(rpid)
        return response
