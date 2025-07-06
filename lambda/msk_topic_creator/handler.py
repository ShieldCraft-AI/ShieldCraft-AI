import os
import json
import logging
import boto3
from kafka.admin import KafkaAdminClient, NewTopic

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_bootstrap_brokers(cluster_arn, region):
    client = boto3.client("kafka", region_name=region)
    resp = client.get_bootstrap_brokers(ClusterArn=cluster_arn)
    return resp["BootstrapBrokerStringTls"]


def lambda_handler(event, context):
    # Read config from environment or event
    cluster_arn = os.environ["MSK_CLUSTER_ARN"]
    region = os.environ.get("AWS_REGION", "af-south-1")
    topic_config = json.loads(
        os.environ["TOPIC_CONFIG"]
    )  # List of dicts: [{name, partitions, replication, ...}]
    logger.info(f"Creating topics: {topic_config}")

    brokers = get_bootstrap_brokers(cluster_arn, region)
    admin = KafkaAdminClient(bootstrap_servers=brokers, security_protocol="SSL")

    topics_to_create = []
    for t in topic_config:
        topics_to_create.append(
            NewTopic(
                name=t["name"],
                num_partitions=t.get("partitions", 1),
                replication_factor=t.get("replication", 2),
                topic_configs=t.get("configs", {}),
            )
        )

    try:
        admin.create_topics(new_topics=topics_to_create, validate_only=False)
        logger.info(f"Topics created: {[t['name'] for t in topic_config]}")
    except Exception as e:
        # If topics already exist, log and continue (idempotent)
        if "TopicAlreadyExistsError" in str(e):
            logger.info("Some or all topics already exist, skipping.")
        else:
            logger.error(f"Error creating topics: {e}")
            raise

    return {
        "statusCode": 200,
        "body": f"Topics processed: {[t['name'] for t in topic_config]}",
    }
