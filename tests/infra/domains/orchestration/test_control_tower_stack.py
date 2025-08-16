"""
Test suite for ControlTowerService.
"""

import pytest
from unittest.mock import patch, MagicMock
from infra.domains.orchestration.control_tower_stack import ControlTowerService


@pytest.fixture
def service():
    return ControlTowerService(region_name="us-east-1")


def test_create_landing_zone_success(service):
    with (
        patch("subprocess.run") as mock_run,
        patch.object(
            service.org_client, "create_organizational_unit"
        ) as mock_create_ou,
        patch.object(service, "get_root_id", return_value="r-root"),
    ):
        mock_run.return_value = MagicMock(stdout="landing zone created")
        mock_create_ou.return_value = {"OrganizationalUnit": {"Id": "ou-123"}}
        ou_id = service.create_landing_zone("lz-test", "ou-test")
        assert ou_id == "ou-123"
        mock_run.assert_called()
        mock_create_ou.assert_called()


def test_create_landing_zone_failure(service):
    with patch("subprocess.run", side_effect=Exception("fail")):
        with pytest.raises(Exception):
            service.create_landing_zone("lz-test", "ou-test")
    # Test missing landing_zone_name
    with pytest.raises(ValueError):
        service.create_landing_zone("", "ou-test")
    # Test missing ou_name
    with pytest.raises(ValueError):
        service.create_landing_zone("lz-test", "")


def test_enable_guardrail_success(service):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="guardrail enabled")
        service.enable_guardrail("guardrail-test", "lz-123")
        mock_run.assert_called()


def test_enable_guardrail_failure(service):
    with patch("subprocess.run", side_effect=Exception("fail")):
        with pytest.raises(Exception):
            service.enable_guardrail("guardrail-test", "lz-123")
    # Test missing guardrail_name
    with pytest.raises(ValueError):
        service.enable_guardrail("", "lz-123")
    # Test missing landing_zone_id
    with pytest.raises(ValueError):
        service.enable_guardrail("guardrail-test", "")


def test_list_landing_zones_success(service):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="landing zones output")
        output = service.list_landing_zones()
        assert "landing zones output" in output


def test_list_landing_zones_failure(service):
    with patch("subprocess.run", side_effect=Exception("fail")):
        with pytest.raises(Exception):
            service.list_landing_zones()


def test_list_guardrails_success(service):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="guardrails output")
        output = service.list_guardrails("lz-123")
        assert "guardrails output" in output


def test_list_guardrails_failure(service):
    with patch("subprocess.run", side_effect=Exception("fail")):
        with pytest.raises(Exception):
            service.list_guardrails("lz-123")
    # Test missing landing_zone_id
    with pytest.raises(ValueError):
        service.list_guardrails("")


def test_get_root_id(service):
    with patch.object(
        service.org_client, "list_roots", return_value={"Roots": [{"Id": "r-root"}]}
    ):
        root_id = service.get_root_id()
        assert root_id == "r-root"
