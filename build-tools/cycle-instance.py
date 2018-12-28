#!/usr/bin/env python

import boto3
import requests

from pprint import pprint

client = boto3.client('ec2')
resource = boto3.resource('ec2')
INSTANCE_NAME = 'psf'

for page in client.get_paginator('describe_instances').paginate():
  for instance in page['Reservations']:
    for something in instance['Instances']:
      if INSTANCE_NAME in [tag['Value'] for tag in something.get('Tags', [])]:
        if something['State']['Code'] in [16]:
          client.terminate_instances(InstanceIds=[something['InstanceId']])

instances = resource.create_instances(
    ImageId='ami-3dec9947',
    InstanceType='t1.micro',
    KeyName='blank',
    MinCount=1,
    MaxCount=1,
    Monitoring={
      'Enabled': False,
    },
    Placement={
      'AvailabilityZone': 'us-east-1b',
      'Tenancy': 'default'
    },
    SecurityGroupIds=['sg-933566e6'],
    SubnetId='subnet-40ac146b',
    TagSpecifications=[
      {
        'ResourceType': 'instance',
        'Tags': [{'Key': 'Name', 'Value': INSTANCE_NAME}]
      }
    ])

client.create_tags(Resources=[res.id for res in instances], Tags=[{'Key': 'Name', 'Value': INSTANCE_NAME}])

def capture_ip_address():
  while True:
    incomplete = False
    for instance in client.describe_instances(InstanceIds=[res.id for res in instances])['Reservations']:
      for something in instance['Instances']:
        if something['PublicIpAddress'] in ['', None]:
          incomplete = True
          break
        else:
          return something['PublicIpAddress']

      if incomplete:
        break

    if incomplete:
      print("Polling for Public IP address")
      time.sleep(1)
      continue

    break

print('New instance with new IP Address %s' % capture_ip_address())

