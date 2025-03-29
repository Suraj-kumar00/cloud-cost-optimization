# Her is the Step by step guide to do hands-on as per the architecture diagram and the python scirpt we have for Lambda function.

---

## **🔹 Step 1: Deploy the Lambda Function**

1. **Go to AWS Lambda** → Create a new Lambda function.
2. **Choose Python 3.x as the runtime.**
3. **Upload the script** or paste it in the inline editor.
4. **Attach IAM Role** with the following permissions:
   - `AmazonEC2FullAccess` (or custom permissions for listing and deleting snapshots).
   - `AmazonSNSFullAccess` (to send notifications).
   - `AWSLambdaBasicExecutionRole` (for logging to CloudWatch).
   - Or you can just the [IAM policy](./Least_Privilage_IAM.json) I have provided.
5. **Set up CloudWatch Logs**:
   - Enable logging for debugging and monitoring.

---

## **🔹 Step 2: Configure SNS for Notifications**

1. **Go to Amazon SNS** → Create a new topic.
2. **Choose type:** Standard or FIFO (Standard recommended).
3. **Add subscribers**:
   - **Email**: Receive notifications via email.
   - **SMS**: Get alerts on your phone.
   - **Lambda**: Trigger another Lambda if needed.
4. **Copy the SNS Topic ARN** and replace it in the Python script.

---

## **🔹 Step 3: Monitor & Test**

1. **Manually test the Lambda function**:
   - Click **"Test"** in AWS Lambda and check the logs in **CloudWatch**.
2. **Verify SNS notifications**:
   - Ensure you receive emails/SMS alerts when snapshots are deleted.
3. **Monitor CloudWatch Logs**:
   - Check if errors occur and debug accordingly.

---

## **🔹 Step 4: Optimize IAM & Security**

1. **Restrict IAM permissions**:
   - Only allow `ec2:DeleteSnapshot` on snapshots owned by your account.
2. **Enable AWS Config & Cost Explorer**:
   - Monitor cost savings after running the script for a few days.

---

### 🎯 **Final Outcome**

- **💰 Cost Savings**: Unused EBS snapshots are automatically deleted.
- **⚡ Efficiency**: No manual intervention needed.
- **📩 Notifications**: You get alerts for every action.
