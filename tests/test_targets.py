"""Unit tests for targets.py - Constants and device resolution."""
import pytest
from unittest.mock import patch
from flaas.targets import (
    Targets,
    DEFAULT_TARGETS,
    MASTER_TRACK_ID,
    resolve_utility_device_id
)
from flaas.osc_rpc import OscTarget


class TestTargets:
    """Test Targets dataclass."""
    
    def test_targets_defaults(self):
        """Test Targets has correct defaults."""
        targets = Targets()
        assert targets.master_lufs == -10.5
        assert targets.true_peak_ceiling_dbfs == -1.0
        assert targets.stem_peak_ceiling_dbfs == -6.0
    
    def test_targets_custom_values(self):
        """Test Targets accepts custom values."""
        targets = Targets(master_lufs=-14.0, true_peak_ceiling_dbfs=-2.0)
        assert targets.master_lufs == -14.0
        assert targets.true_peak_ceiling_dbfs == -2.0
    
    def test_default_targets_exists(self):
        """Test DEFAULT_TARGETS constant exists."""
        assert isinstance(DEFAULT_TARGETS, Targets)
    
    def test_targets_frozen(self):
        """Test that Targets is immutable."""
        targets = Targets()
        with pytest.raises(Exception):  # FrozenInstanceError
            targets.master_lufs = -20.0


class TestConstants:
    """Test module constants."""
    
    def test_master_track_id(self):
        """Test MASTER_TRACK_ID is correct."""
        assert MASTER_TRACK_ID == -1000


class TestResolveUtilityDeviceId:
    """Test utility device ID resolution."""
    
    @patch("flaas.targets.request_once")
    def test_resolve_utility_device_id_found(self, mock_request):
        """Test resolving Utility device ID when found."""
        mock_request.return_value = (-1000, "EQ Eight", "Utility", "Limiter")
        
        device_id = resolve_utility_device_id(OscTarget())
        assert device_id == 1  # Second device (0-indexed from names list)
    
    @patch("flaas.targets.request_once")
    def test_resolve_utility_device_id_case_insensitive(self, mock_request):
        """Test resolution is case insensitive."""
        mock_request.return_value = (-1000, "UTILITY")
        
        device_id = resolve_utility_device_id(OscTarget())
        assert device_id == 0
    
    @patch("flaas.targets.request_once")
    def test_resolve_utility_device_id_with_whitespace(self, mock_request):
        """Test resolution handles whitespace."""
        mock_request.return_value = (-1000, "  Utility  ")
        
        device_id = resolve_utility_device_id(OscTarget())
        assert device_id == 0
    
    @patch("flaas.targets.request_once")
    def test_resolve_utility_device_id_not_found(self, mock_request):
        """Test exit when Utility not found."""
        mock_request.return_value = (-1000, "EQ Eight", "Limiter")
        
        with pytest.raises(SystemExit) as exc_info:
            resolve_utility_device_id(OscTarget())
        assert exc_info.value.code == 20
    
    @patch("flaas.targets.request_once")
    def test_resolve_utility_device_id_osc_error(self, mock_request):
        """Test exit on OSC error."""
        mock_request.side_effect = TimeoutError("Connection failed")
        
        with pytest.raises(SystemExit) as exc_info:
            resolve_utility_device_id(OscTarget())
        assert exc_info.value.code == 20
    
    @patch("flaas.targets.request_once")
    def test_resolve_utility_device_id_first_device(self, mock_request):
        """Test resolving when Utility is first device."""
        mock_request.return_value = (-1000, "Utility", "EQ Eight", "Limiter")
        
        device_id = resolve_utility_device_id(OscTarget())
        assert device_id == 0
    
    @patch("flaas.targets.request_once")
    def test_resolve_utility_device_id_last_device(self, mock_request):
        """Test resolving when Utility is last device."""
        mock_request.return_value = (-1000, "EQ Eight", "Limiter", "Utility")
        
        device_id = resolve_utility_device_id(OscTarget())
        assert device_id == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
