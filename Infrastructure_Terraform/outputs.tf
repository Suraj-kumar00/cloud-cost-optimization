output "lambda_function_name" {
  value = aws_lambda_function.ebs_cleanup_lambda.function_name
}

output "lambda_arn" {
  value = aws_lambda_function.ebs_cleanup_lambda.arn
}

# Output values for reference
output "instance_id" {
  value = aws_instance.cost_optimized_ec2.id
}

output "ebs_volume_id" {
  value = aws_ebs_volume.my_volume.id
}

output "sns_topic_arn" {
  value = aws_sns_topic.snapshot_cleanup.arn
}