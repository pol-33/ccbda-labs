from dotenv import dotenv_values
import sys

# instance profile and service role must be created beforehand
ebOptions = {
    'min-instances': '1',
    'max-instances': '3',
    'instance_profile': 'aws-elasticbeanstalk-ec2-role',
    'service-role': 'AWSServiceRoleForElasticBeanstalk',
    'elb-type': 'application',
    'instance-types':'t3.small',
    'keyname':'aws-eb'
}

try:
    CONFIGURATION_FILE = sys.argv[1]
    HOSTNAME = sys.argv[2]
except:
    print('ERROR: filename missing\npython ebcreate.py filename hostname')
    exit()
config = dotenv_values(CONFIGURATION_FILE)

hostname = f'{HOSTNAME}.{config["AWS_REGION"]}.elasticbeanstalk.com'

hosts = config['DJANGO_ALLOWED_HOSTS'].split(':')
if hostname not in hosts:
    hosts.append(hostname)
    config['DJANGO_ALLOWED_HOSTS'] = ':'.join(hosts)
opt = []
for k, v in config.items():
    opt.append(f'{k}={v}')
ebOptions['cname'] = HOSTNAME
ebOptions['envvars'] = '"%s"' % ','.join(opt)


opt = []
for k, v in ebOptions.items():
    opt.append(f'--{k} {v}')

print(f'eb create {HOSTNAME} %s ' % ' '.join(opt))