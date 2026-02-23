"""Unit tests for master_premium.py - Premium mastering optimization."""
import pytest
from unittest.mock import patch, MagicMock
from flaas.master_premium import (
    resolve_device_id_by_name,
    resolve_device_params,
    set_param_normalized,
    db_to_normalized,
    compute_sha256,
    master_premium
)
from flaas.osc_rpc import OscTarget
from pathlib import Path
import tempfile


class TestResolveDeviceIdByName:
    """Test device ID resolution by name."""
    
    @patch("flaas.master_premium.request_once")
    def test_resolve_first_device(self, mock_request):
        """Test resolving first device in chain."""
        mock_request.return_value = (-1000, "Utility", "EQ Eight", "Limiter")
        
        device_id = resolve_device_id_by_name(-1000, "Utility")
        assert device_id == 0
    
    @patch("flaas.master_premium.request_once")
    def test_resolve_middle_device(self, mock_request):
        """Test resolving middle device in chain."""
        mock_request.return_value = (-1000, "Utility", "EQ Eight", "Limiter")
        
        device_id = resolve_device_id_by_name(-1000, "EQ Eight")
        assert device_id == 1
    
    @patch("flaas.master_premium.request_once")
    def test_resolve_case_insensitive(self, mock_request):
        """Test case-insensitive device resolution."""
        mock_request.return_value = (-1000, "Utility", "EQ Eight")
        
        device_id = resolve_device_id_by_name(-1000, "utility")
        assert device_id == 0
    
    @patch("flaas.master_premium.request_once")
    def test_resolve_partial_match(self, mock_request):
        """Test partial name matching."""
        mock_request.return_value = (-1000, "Waves C6 Stereo", "Waves SSL")
        
        device_id = resolve_device_id_by_name(-1000, "C6")
        assert device_id == 0
    
    @patch("flaas.master_premium.request_once")
    def test_device_not_found_raises_error(self, mock_request):
        """Test that missing device raises RuntimeError."""
        mock_request.return_value = (-1000, "Utility", "EQ Eight")
        
        with pytest.raises(RuntimeError, match="not found"):
            resolve_device_id_by_name(-1000, "Nonexistent")


class TestResolveDeviceParams:
    """Test device parameter resolution."""
    
    @patch("flaas.master_premium.request_once")
    def test_resolve_params_returns_dict(self, mock_request):
        """Test that resolve_device_params returns a dict."""
        mock_request.side_effect = [
            (-1000, 0, "Param1", "Param2"),  # names
            (-1000, 0, 0.0, 0.5),             # values
            (-1000, 0, 0.0, 0.0),             # mins
            (-1000, 0, 1.0, 1.0)              # maxs
        ]
        
        params = resolve_device_params(-1000, 0)
        
        assert isinstance(params, dict)
        assert len(params) >= 1
    
    @patch("flaas.master_premium.request_once")
    def test_params_have_required_keys(self, mock_request):
        """Test that params have required structure."""
        mock_request.side_effect = [
            (-1000, 0, "Gain"),
            (-1000, 0, 0.5),
            (-1000, 0, 0.0),
            (-1000, 0, 1.0)
        ]
        
        params = resolve_device_params(-1000, 0)
        
        # Should have at least one param
        assert len(params) > 0
        # Each param should have metadata
        for param_name, param_data in params.items():
            assert isinstance(param_data, dict)


class TestSetParamNormalized:
    """Test normalized parameter setting."""
    
    @patch("flaas.master_premium.SimpleUDPClient")
    def test_set_param_sends_osc_message(self, mock_client_class):
        """Test that set_param sends OSC message."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        target = OscTarget()
        set_param_normalized(-1000, 0, 5, 0.75, target)
        
        mock_client.send_message.assert_called_once()
        args = mock_client.send_message.call_args[0]
        assert args[0] == "/live/device/set/parameter/value"
    
    @patch("flaas.master_premium.SimpleUDPClient")
    def test_set_param_clamps_to_valid_range(self, mock_client_class):
        """Test that values are clamped to [0, 1]."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        target = OscTarget()
        set_param_normalized(-1000, 0, 5, 1.5, target)  # Over max
        
        # Value should be clamped to 1.0
        args = mock_client.send_message.call_args[0][1]
        assert args[3] <= 1.0


class TestDbToNormalized:
    """Test dB to normalized conversion."""
    
    def test_min_value_returns_zero(self):
        """Test that minimum dB returns 0.0."""
        result = db_to_normalized(-60.0, -60.0, 0.0)
        assert abs(result - 0.0) < 0.01
    
    def test_max_value_returns_one(self):
        """Test that maximum dB returns 1.0."""
        result = db_to_normalized(0.0, -60.0, 0.0)
        assert abs(result - 1.0) < 0.01
    
    def test_midpoint_value(self):
        """Test midpoint conversion."""
        result = db_to_normalized(-30.0, -60.0, 0.0)
        # -30 dB is halfway between -60 and 0
        assert abs(result - 0.5) < 0.01
    
    def test_linear_interpolation(self):
        """Test linear interpolation between min and max."""
        # 25% of the way from -60 to 0 should be -45
        result = db_to_normalized(-45.0, -60.0, 0.0)
        assert abs(result - 0.25) < 0.01
        
        # 75% of the way from -60 to 0 should be -15
        result = db_to_normalized(-15.0, -60.0, 0.0)
        assert abs(result - 0.75) < 0.01


class TestComputeSha256:
    """Test SHA256 computation."""
    
    def test_sha256_returns_hex_string(self):
        """Test that SHA256 returns a hex string."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(b"test audio data")
            temp_path = Path(f.name)
        
        try:
            hash_value = compute_sha256(temp_path)
            assert isinstance(hash_value, str)
            assert len(hash_value) == 64  # SHA256 is 64 hex chars
            # Check it's valid hex
            int(hash_value, 16)
        finally:
            temp_path.unlink()
    
    def test_same_file_same_hash(self):
        """Test that same file produces same hash."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(b"consistent content")
            temp_path = Path(f.name)
        
        try:
            hash1 = compute_sha256(temp_path)
            hash2 = compute_sha256(temp_path)
            assert hash1 == hash2
        finally:
            temp_path.unlink()
    
    def test_different_files_different_hash(self):
        """Test that different files produce different hashes."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f1:
            f1.write(b"content one")
            path1 = Path(f1.name)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f2:
            f2.write(b"content two")
            path2 = Path(f2.name)
        
        try:
            hash1 = compute_sha256(path1)
            hash2 = compute_sha256(path2)
            assert hash1 != hash2
        finally:
            path1.unlink()
            path2.unlink()


class TestMasterPremiumMain:
    """Test master_premium main function."""
    
    @patch("flaas.master_premium.run_preflight_checks")
    def test_preflight_failure_exits_early(self, mock_preflight):
        """Test that preflight failure returns 1."""
        mock_preflight.return_value = False
        
        result = master_premium(
            target=OscTarget(),
            auto_export_enabled=True,
            mode="streaming_safe",
            skip_prompts=True
        )
        
        assert result == 1
    
    @patch("flaas.master_premium.run_preflight_checks")
    def test_skip_prompts_passed_to_preflight(self, mock_preflight):
        """Test that skip_prompts is passed to preflight."""
        mock_preflight.return_value = False
        
        master_premium(
            target=OscTarget(),
            auto_export_enabled=True,
            mode="streaming_safe",
            skip_prompts=True
        )
        
        # Verify skip_prompts was passed
        assert mock_preflight.called
        call_kwargs = mock_preflight.call_args[1]
        assert "skip_prompts" in call_kwargs
        assert call_kwargs["skip_prompts"] is True
    
    @patch("flaas.master_premium.run_preflight_checks")
    def test_mode_parameter_accepted(self, mock_preflight):
        """Test that different mode parameters are accepted."""
        mock_preflight.return_value = False
        
        for mode in ["streaming_safe", "loud_preview", "headroom"]:
            result = master_premium(
                target=OscTarget(),
                auto_export_enabled=True,
                mode=mode,
                skip_prompts=True
            )
            assert result == 1  # Fails at preflight
    
    @patch("flaas.master_premium.run_preflight_checks")
    def test_custom_target_passed(self, mock_preflight):
        """Test that custom OscTarget is used."""
        mock_preflight.return_value = False
        custom_target = OscTarget(host="192.168.1.100", port=9000)
        
        master_premium(
            target=custom_target,
            auto_export_enabled=True,
            mode="streaming_safe",
            skip_prompts=True
        )
        
        # Verify custom target was passed
        assert mock_preflight.called
        call_args = mock_preflight.call_args
        # Target should be in args or kwargs
        passed_target = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("target")
        assert passed_target == custom_target


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
