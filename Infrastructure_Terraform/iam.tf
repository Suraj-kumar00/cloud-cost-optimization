# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "ebs-cleanup-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "lambda.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

# IAM Policy for Lambda
resource "aws_iam_policy" "lambda_policy" {
  name        = "ebs-cleanup-lambda-policy"
  description = "Allows Lambda to manage EBS snapshots"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["ec2:DescribeSnapshots", "ec2:DescribeInstances", "ec2:DescribeVolumes"],
        Resource = "*"
      },
      {
        Effect   = "Allow",
        Action   = "ec2:DeleteSnapshot",
        Resource = "*"
      }
    ]
  })
}

# Attach IAM Policy to Role
resource "aws_iam_role_policy_attachment" "attach_lambda_policy" {
  policy_arn = aws_iam_policy.lambda_policy.arn
  role       = aws_iam_role.lambda_role.name
}
