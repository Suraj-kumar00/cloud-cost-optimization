import boto3
import logging
import json
from botocore.exceptions import BotoCoreError, ClientError

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS Clients
ec2 = boto3.client("ec2")
sns = boto3.client("sns")

# SNS Topic ARN (Replace with actual ARN)
SNS_TOPIC_ARN = "arn:aws:sns:your-region:your-account-id:your-topic-name"

def send_sns_notification(message, subject="AWS EBS Snapshot Cleanup"):
    """ Sends a notification to AWS SNS """
    try:
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message),
            Subject=subject,
        )
        logger.info(f"SNS Notification Sent: {response['MessageId']}")
    except ClientError as e:
        logger.error(f"Failed to send SNS notification: {e}")

def get_active_volumes():
    """ Retrieves all active (running + stopped) EC2 instance volumes """
    active_volumes = set()
    try:
        instances = ec2.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}])
        for res in instances["Reservations"]:
            for instance in res["Instances"]:
                for block in instance.get("BlockDeviceMappings", []):
                    if "Ebs" in block:
                        active_volumes.add(block["Ebs"]["VolumeId"])
        logger.info(f"Active volumes: {active_volumes}")
    except ClientError as e:
        logger.error(f"Error fetching EC2 instances: {e}")
    return active_volumes

def delete_stale_snapshots():
    """ Identifies and deletes stale snapshots not linked to active volumes """
    try:
        snapshots = ec2.describe_snapshots(OwnerIds=["self"])["Snapshots"]
        active_volumes = get_active_volumes()

        for snapshot in snapshots:
            if "VolumeId" in snapshot and snapshot["VolumeId"] not in active_volumes:
                snapshot_id = snapshot["SnapshotId"]
                try:
                    ec2.delete_snapshot(SnapshotId=snapshot_id)
                    logger.info(f"Deleted stale snapshot: {snapshot_id}")
                    send_sns_notification({"snapshot_id": snapshot_id, "status": "Deleted"}, "Snapshot Cleanup")
                except ClientError as e:
                    logger.error(f"Failed to delete snapshot {snapshot_id}: {e}")

    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to process snapshots: {e}")

def lambda_handler(event, context):
    """ AWS Lambda Entry Point """
    logger.info("Starting snapshot cleanup process...")
    delete_stale_snapshots()
    logger.info("Snapshot cleanup completed.")
    return {"status": "Cleanup completed"}
