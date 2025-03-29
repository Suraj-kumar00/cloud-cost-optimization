
# Create an SNS Topic for Snapshot Deletion Alerts
resource "aws_sns_topic" "snapshot_cleanup" {
  name = "snapshot-cleanup-alerts"
}

# Subscribe an email to SNS for notifications
resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.snapshot_cleanup.arn
  protocol  = "email"
  endpoint  = "suraj.ukumar.p@gmail.com" 
}