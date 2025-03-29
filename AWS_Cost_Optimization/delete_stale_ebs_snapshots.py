import boto3
import logging
import json
from botocore.exceptions import BotoCoreError, ClientError

# Setup logging for CloudWatch monitoring
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS Clients
ec2 = boto3.client('ec2')
sns = boto3.client('sns')

# SNS Topic ARN (Replace with your actual ARN)
SNS_TOPIC_ARN = "arn:aws:sns:your-region:your-account-id:your-topic-name"

def send_sns_notification(message, subject="AWS EBS Snapshot Cleanup"):
    """ Sends a notification to AWS SNS """
    try:
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message),
            Subject=subject
        )
        logger.info(f"SNS Notification Sent: {response['MessageId']}")
    except ClientError as e:
        logger.error(f"Failed to send SNS notification: {e}")

def get_all_snapshots():
    """
    Retrieve all EBS snapshots owned by the account.
    Uses pagination to handle large data sets efficiently.
    """
    snapshots = []
    paginator = ec2.get_paginator('describe_snapshots')
    for page in paginator.paginate(OwnerIds=['self']):
        snapshots.extend(page['Snapshots'])
    return snapshots

def get_active_instance_ids():
    """
    Retrieve all active (running) EC2 instance IDs.
    Uses pagination to ensure all instances are fetched.
    """
    active_instance_ids = set()
    paginator = ec2.get_paginator('describe_instances')
    for page in paginator.paginate(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]):
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                active_instance_ids.add(instance['InstanceId'])
    return active_instance_ids

def delete_stale_snapshots():
    """
    Identifies and deletes stale EBS snapshots:
    - Snapshots not linked to any volume.
    - Snapshots linked to unattached volumes.
    """
    try:
        # Fetch all snapshots owned by the AWS account
        snapshots = get_all_snapshots()
        # Fetch all running EC2 instance IDs
        active_instance_ids = get_active_instance_ids()

        for snapshot in snapshots:
            snapshot_id = snapshot['SnapshotId']
            volume_id = snapshot.get('VolumeId')

            if not volume_id:
                # Delete snapshot if not associated with any volume
                try:
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    logger.info(f"Deleted EBS snapshot {snapshot_id} (not attached to any volume).")
                    send_sns_notification({"snapshot_id": snapshot_id, "reason": "No associated volume"})
                except ClientError as e:
                    logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
            else:
                try:
                    # Fetch volume details to check if it's attached to an instance
                    volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
                    if not volume_response['Volumes'][0]['Attachments']:
                        # Delete snapshot if the volume is not attached to any instance
                        try:
                            ec2.delete_snapshot(SnapshotId=snapshot_id)
                            logger.info(f"Deleted EBS snapshot {snapshot_id} (volume not attached).")
                            send_sns_notification({"snapshot_id": snapshot_id, "reason": "Volume not attached"})
                        except ClientError as e:
                            logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                        # Delete snapshot if its associated volume is not found
                        try:
                            ec2.delete_snapshot(SnapshotId=snapshot_id)
                            logger.info(f"Deleted EBS snapshot {snapshot_id} (associated volume not found).")
                            send_sns_notification({"snapshot_id": snapshot_id, "reason": "Volume not found"})
                        except ClientError as e:
                            logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")
                    else:
                        logger.error(f"Error checking volume {volume_id}: {e}")
                        continue

    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to process snapshots: {e}")

def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    Triggers the snapshot cleanup process.
    """
    delete_stale_snapshots()
