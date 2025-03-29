# CloudWatch Event Rule (Runs every 6 hours)
resource "aws_cloudwatch_event_rule" "lambda_trigger" {
  name                = "ebs-cleanup-schedule"
  description         = "Triggers the EBS cleanup Lambda function every 6 hours"
  schedule_expression = "rate(2 minutes)"
}

# Connect CloudWatch Event to Lambda
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_trigger.name
  target_id = "lambda"
  arn       = aws_lambda_function.ebs_cleanup_lambda.arn
}

# Allow CloudWatch to Invoke Lambda
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ebs_cleanup_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_trigger.arn
}
