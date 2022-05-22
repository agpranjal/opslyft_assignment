import boto3
import os
from datetime import datetime

ec2 = boto3.resource("ec2")
ses = boto3.client("ses")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("instance-email-mapping")

def get_tag_value(instance, tag_name):
    # Return the value of tag from instance
    
    for tag in instance.tags:
        if tag["Key"] == tag_name:
            return tag["Value"]
        
def has_tag(instance, tag_name):
    # Check if tag exists in given instance
    
    for tag in instance.tags:
        if tag["Key"] == tag_name:
            return True
    return False

def send_email(recepient, subject, data):
    # Send email using SES service
    
    response = ses.send_email(
        Destination={
            "ToAddresses": [recepient]
        },
        Message={
            "Body": {
                "Text": {
                    "Data": data
                }
            },
            "Subject": {
                "Data": subject
            }
        },
        Source=os.getenv("SENDER_EMAIL_ADDRESS")
    )

def get_instance_by_id(instances, id):
    # Return instance obj from instance id
    
    for i in instances:
        if i.id == id:
            return i
    return None

def get_missing_tags(instance):
    # Send a list containing tags that are missing
    # Returns empty list in case of no missing tags
    
    has_environment_tag = has_tag(instance, "Environment")
    has_name_tag = has_tag(instance, "Name")
    missing_tags = []
    
    if not has_environment_tag:
        missing_tags.append("Environment")
    if not has_name_tag:
        missing_tags.append("Name")
    
    return missing_tags

def terminate_instances_after_six_hours():
    
    # Scan DynamoDB table
    # If instance exists and 6hrs have elapsed and instance has missing tags => send email to the owner
    # Terminate the instance if 6hrs have elapsed
    instances = [i for i in ec2.instances.all()]
    
    for item in table.scan()["Items"]:
        date = datetime.fromisoformat(item["created_at"])
        instance_id = item["instance_id"]
        owner_email = item["email"]
        hours_elapsed = ((datetime.now() - date).total_seconds())/(60*60)
        
        if hours_elapsed >= 6:
            instance = get_instance_by_id(instances, instance_id)
            missing_tags = get_missing_tags(instance)
            
            if instance and len(missing_tags) > 0:
                subject = "Instance Deleted | AWS EC2"
                source = "pranjal.ag.1999@gmail.com"
                data = """
                Hi,
                An AWS EC2 instance with instance id {0} has been deleted
                """.format(instance_id)
                send_email(owner_email, subject, data)
                instance.terminate()
            
            table.delete_item(Key={"instance_id": instance_id})

def notify_instances_missing_tags():
    
    # Get a list of all instances
    # Get a list of missing tags of single instance
    # Send email to owner of that instance
    # Add the instance to DyanmoDB table to check later if 6hrs have passed and the instance has the tags or not
    
    for instance in ec2.instances.all():
        has_environment_tag = has_tag(instance, "Environment")
        has_name_tag = has_tag(instance, "Name")
        
        missing_tags = get_missing_tags(instance)
        
        if len(missing_tags) > 0:
            owner_email = get_tag_value(instance, "created by")
            subject = "Missing Tags | AWS EC2"
            source = "pranjal.ag.1999@gmail.com"
            data = """
            Hi,
            An AWS EC2 instance with instance id {0} is missing the following tags: {1}
            Please add the missing tags before the instance gets deleted.
            """.format(instance.id, missing_tags)
            send_email(owner_email, subject, data)
            
            # If instance.id exist in DyanmoDB => no need to modify it
            # If instance.id does not exist, add in DyanmoDB
            if "Item" not in table.get_item(Key={"instance_id": instance.id}):
                table.put_item(
                    Item={
                        "instance_id": instance.id,
                        "email": owner_email,
                        "created_at": datetime.now().isoformat()
                    },
                    ConditionExpression="attribute_not_exists(instance_id)"
                )
    
    
def lambda_handler(event, context):
    
    # Terminate the instances which do not have Name and Environment tags and 6hrs has passed since first email
    terminate_instances_after_six_hours()
    
    # Email the owner of the instances which do not have Name and Environment tags
    notify_instances_missing_tags()
    
    
    
