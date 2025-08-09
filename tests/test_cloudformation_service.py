"""
Test cases for the CloudFormationService class.
"""

import unittest
from unittest.mock import patch, MagicMock
import botocore
from infra.stacks.orchestration.cloudformation_service import CloudFormationService


class TestCloudFormationService(unittest.TestCase):
    def setUp(self):
        self.region = "us-east-1"
        self.env = "test"
        self.cf_service = CloudFormationService(
            region_name=self.region, environment=self.env
        )
        self.cf_service.client = MagicMock()

    def test_create_stack(self):
        self.cf_service.client.create_stack.return_value = {"StackId": "test-stack-id"}
        result = self.cf_service.create_stack("teststack", "http://template-url")
        self.cf_service.client.create_stack.assert_called_once()
        self.assertIn("StackId", result)

    def test_update_stack(self):
        self.cf_service.client.update_stack.return_value = {"StackId": "test-stack-id"}
        result = self.cf_service.update_stack("teststack", "http://template-url")
        self.cf_service.client.update_stack.assert_called_once()
        self.assertIn("StackId", result)

    def test_delete_stack(self):
        self.cf_service.client.delete_stack.return_value = {}
        result = self.cf_service.delete_stack("teststack")
        self.cf_service.client.delete_stack.assert_called_once()
        self.assertEqual(result, {})

    def test_get_stack_status(self):
        self.cf_service.client.describe_stacks.return_value = {
            "Stacks": [{"StackStatus": "CREATE_COMPLETE"}]
        }
        status = self.cf_service.get_stack_status("teststack")
        self.cf_service.client.describe_stacks.assert_called_once()
        self.assertEqual(status, "CREATE_COMPLETE")

    def test_list_stacks(self):
        self.cf_service.client.list_stacks.return_value = {
            "StackSummaries": [
                {"StackName": "teststack-test"},
                {"StackName": "otherstack-prod"},
            ]
        }
        stacks = self.cf_service.list_stacks()
        self.cf_service.client.list_stacks.assert_called_once()
        self.assertEqual(len(stacks), 1)
        self.assertEqual(stacks[0]["StackName"], "teststack-test")

    def test_get_stack_events(self):
        self.cf_service.client.describe_stack_events.return_value = {
            "StackEvents": [{"EventId": "evt-1"}]
        }
        events = self.cf_service.get_stack_events("teststack")
        self.cf_service.client.describe_stack_events.assert_called_once()
        self.assertEqual(events[0]["EventId"], "evt-1")

    def test_detect_drift(self):
        self.cf_service.client.detect_stack_drift.return_value = {
            "StackDriftDetectionId": "drift-1"
        }
        result = self.cf_service.detect_drift("teststack")
        self.cf_service.client.detect_stack_drift.assert_called_once()
        self.assertEqual(result["StackDriftDetectionId"], "drift-1")

    def test_get_stack_outputs(self):
        self.cf_service.client.describe_stacks.return_value = {
            "Stacks": [{"Outputs": {"Key": "Value"}}]
        }
        outputs = self.cf_service.get_stack_outputs("teststack")
        self.cf_service.client.describe_stacks.assert_called_once()
        self.assertEqual(outputs["Key"], "Value")

    def test_create_stack_happy(self):
        self.cf_service.client.create_stack.return_value = {"StackId": "test-stack-id"}
        result = self.cf_service.create_stack("teststack", "http://template-url")
        self.cf_service.client.create_stack.assert_called_once()
        self.assertIn("StackId", result)

    def test_create_stack_unhappy(self):
        self.cf_service.client.create_stack.side_effect = Exception("Create failed")
        with self.assertRaises(Exception):
            self.cf_service.create_stack("teststack", "http://template-url")

    def test_update_stack_happy(self):
        self.cf_service.client.update_stack.return_value = {"StackId": "test-stack-id"}
        result = self.cf_service.update_stack("teststack", "http://template-url")
        self.cf_service.client.update_stack.assert_called_once()
        self.assertIn("StackId", result)

    def test_update_stack_unhappy(self):
        self.cf_service.client.update_stack.side_effect = Exception("Update failed")
        with self.assertRaises(Exception):
            self.cf_service.update_stack("teststack", "http://template-url")

    def test_delete_stack_happy(self):
        self.cf_service.client.delete_stack.return_value = {}
        result = self.cf_service.delete_stack("teststack")
        self.cf_service.client.delete_stack.assert_called_once()
        self.assertEqual(result, {})

    def test_delete_stack_unhappy(self):
        self.cf_service.client.delete_stack.side_effect = Exception("Delete failed")
        with self.assertRaises(Exception):
            self.cf_service.delete_stack("teststack")

    def test_get_stack_status_happy(self):
        self.cf_service.client.describe_stacks.return_value = {
            "Stacks": [{"StackStatus": "CREATE_COMPLETE"}]
        }
        status = self.cf_service.get_stack_status("teststack")
        self.cf_service.client.describe_stacks.assert_called_once()
        self.assertEqual(status, "CREATE_COMPLETE")

    def test_get_stack_status_unhappy(self):
        error = botocore.exceptions.ClientError(
            {"Error": {"Code": "ValidationError", "Message": "Stack does not exist"}},
            "DescribeStacks",
        )
        self.cf_service.client.describe_stacks.side_effect = error
        status = self.cf_service.get_stack_status("teststack")
        self.assertIsNone(status)

    def test_list_stacks_happy(self):
        self.cf_service.client.list_stacks.return_value = {
            "StackSummaries": [
                {"StackName": "teststack-test"},
                {"StackName": "otherstack-prod"},
            ]
        }
        stacks = self.cf_service.list_stacks()
        self.cf_service.client.list_stacks.assert_called_once()
        self.assertEqual(len(stacks), 1)
        self.assertEqual(stacks[0]["StackName"], "teststack-test")

    def test_list_stacks_unhappy(self):
        self.cf_service.client.list_stacks.side_effect = Exception("List failed")
        with self.assertRaises(Exception):
            self.cf_service.list_stacks()

    def test_get_stack_events_happy(self):
        self.cf_service.client.describe_stack_events.return_value = {
            "StackEvents": [{"EventId": "evt-1"}]
        }
        events = self.cf_service.get_stack_events("teststack")
        self.cf_service.client.describe_stack_events.assert_called_once()
        self.assertEqual(events[0]["EventId"], "evt-1")

    def test_get_stack_events_unhappy(self):
        self.cf_service.client.describe_stack_events.side_effect = Exception(
            "Events failed"
        )
        with self.assertRaises(Exception):
            self.cf_service.get_stack_events("teststack")

    def test_detect_drift_happy(self):
        self.cf_service.client.detect_stack_drift.return_value = {
            "StackDriftDetectionId": "drift-1"
        }
        result = self.cf_service.detect_drift("teststack")
        self.cf_service.client.detect_stack_drift.assert_called_once()
        self.assertEqual(result["StackDriftDetectionId"], "drift-1")

    def test_detect_drift_unhappy(self):
        self.cf_service.client.detect_stack_drift.side_effect = Exception(
            "Drift failed"
        )
        with self.assertRaises(Exception):
            self.cf_service.detect_drift("teststack")

    def test_get_stack_outputs_happy(self):
        self.cf_service.client.describe_stacks.return_value = {
            "Stacks": [{"Outputs": {"Key": "Value"}}]
        }
        outputs = self.cf_service.get_stack_outputs("teststack")
        self.cf_service.client.describe_stacks.assert_called_once()
        self.assertEqual(outputs["Key"], "Value")

    def test_get_stack_outputs_unhappy(self):
        self.cf_service.client.describe_stacks.side_effect = Exception("Outputs failed")
        with self.assertRaises(Exception):
            self.cf_service.get_stack_outputs("teststack")


if __name__ == "__main__":
    unittest.main()
