resource "aws_lambda_function" "ebs_cleanup_lambda" {
  function_name    = "ebs-cleanup-lambda"
  role            = aws_iam_role.lambda_role.arn
  handler        = "lambda_function.lambda_handler"
  runtime        = "python3.9"
  timeout        = 30
  memory_size    = 128

  filename         = "lambda_function.zip"
  source_code_hash = filebase64sha256("lambda_function.zip")

  environment {
    variables = {
      LOG_LEVEL = "INFO"
    }
  }
}
