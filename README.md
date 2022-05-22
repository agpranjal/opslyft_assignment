# How It Works

The lambda function will execute every hour and send emails to owners of instances that does not have "Name" or "Environment" tag. Instances that do not have the tag are stored in a DynamoDB table along with other information like value of "created by" tag and a "created_at" key that stores the time DynamoDB record is created.
This "created_at" helps in determining if 6hrs have passed since the record creation.If 6hrs have passed, the instance is terminated, an email is sent to the owner and the record is removed from the DynamoDB

# How To Deploy

### Following things need to be inorder to run this lambda function

0. Create necessary policies
1. Create an IAM role and assign it policies
2. Create the lambda function and attach it to the IAM role
3. Create DynamoDB Table
4. Create Amazon EventBridge rule

## 0. Creating necessary policies

- Create the following IAM policy and name it as "ec2-terminate-policy"

`{ "Version": "2012-10-17", "Statement": [ { "Sid": "VisualEditor0", "Effect": "Allow", "Action": [ "ec2:TerminateInstances", "ec2:DescribeInstances", "ec2:StartInstances", "ec2:DescribeRegions", "ec2:StopInstances", "ec2:DescribeInstanceStatus" ], "Resource": "*" } ] }`

- Create the following IAM policy and name it as "send-email-ses-policy"

`{ "Version": "2012-10-17", "Statement": [ { "Sid": "VisualEditor0", "Effect": "Allow", "Action": "ses:SendEmail", "Resource": "*" } ] }`

- Create the following IAM policy and name it as "dynamodb-read-write-polcy"

`{ "Version": "2012-10-17", "Statement": [ { "Sid": "VisualEditor0", "Effect": "Allow", "Action": "dynamodb:*", "Resource": "*" } ] }`

## 1. Creating an IAM role

- Create an AWS IAM role for a lambda function and attach the three policies created above
- Name the role as "lambda-permissions-role" and create

## 2. Creating the lambda function

- Create an AWS lambda function and attach the above created IAM role to it. Make sure to select "Author from scratch" and name it as "monitorEC2Tags"
- Head over to lambda functions dashboard and and paste the code in src/main.py to index.js file
- Add the following environment variables for the lambda function in the Configuration tab.

Key: `SENDER_EMAIL_ADDRESS`

Value: `YOUR_VERIFIED_EMAIL_ADDRESS`

> **Note**: Replace YOUR_VERIFIED_EMAIL_ADDRESS with an email address that has been verified in AWS SES. This is required so that lambda function can send email using ses

## 3. Create DynamoDB Table

- Create a dynamodb table named "instance-email-mapping"
- Type the following as partition key: `instance_id`
- Type of partition key should be string
- Go with the rest of the default setting and click create

## 4. Create AWS EventBridge Rule

- Go to AWS EventBridge -> Create Rule
- Type the name as: `lambdaEveryHour`
- Select the rule type as "Schedule". Click Next
- Enter the "Schedule" value as a rate of value as "1" and unit as "Hours"
- Add the previously created lambda function as Target
- Create Rule

## Create dummy EC2 instances

- Create multiple dummy EC2 instances. Add "Name" and "Environment" tags in some of them.
- Make sure "created by" tag is present in every EC2 instance
