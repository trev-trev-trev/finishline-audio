"""Unit tests for util.py - Utility functions."""
import pytest
from unittest.mock import patch, MagicMock
from flaas.util import (
    set_utility_gain_norm,
    set_utility_gain_linear,
    UTILITY_GAIN_PARAM_ID
)
from flaas.osc_rpc import OscTarget


class TestSetUtilityGainNorm:
    """Test normalized utility gain setter."""
    
    @patch("flaas.util.SimpleUDPClient")
    def test_set_utility_gain_norm_sends_message(self, mock_client_class):
        """Test that gain setter sends OSC message."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        set_utility_gain_norm(track_id=-1000, device_id=0, gain_norm_0_1=0.5)
        
        mock_client.send_message.assert_called_once()
        args = mock_client.send_message.call_args[0]
        assert args[0] == "/live/device/set/parameter/value"
        assert args[1] == [-1000, 0, UTILITY_GAIN_PARAM_ID, 0.5]
    
    @patch("flaas.util.SimpleUDPClient")
    def test_set_utility_gain_norm_clamps_high(self, mock_client_class):
        """Test that gain values are clamped to 1.0."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        set_utility_gain_norm(track_id=-1000, device_id=0, gain_norm_0_1=1.5)
        
        args = mock_client.send_message.call_args[0][1]
        assert args[3] == 1.0  # Clamped to max
    
    @patch("flaas.util.SimpleUDPClient")
    def test_set_utility_gain_norm_clamps_low(self, mock_client_class):
        """Test that gain values are clamped to 0.0."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        set_utility_gain_norm(track_id=-1000, device_id=0, gain_norm_0_1=-0.5)
        
        args = mock_client.send_message.call_args[0][1]
        assert args[3] == 0.0  # Clamped to min
    
    @patch("flaas.util.SimpleUDPClient")
    def test_set_utility_gain_norm_uses_target(self, mock_client_class):
        """Test that custom target is used."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        target = OscTarget(host="192.168.1.100", port=9000)
        set_utility_gain_norm(track_id=-1000, device_id=0, gain_norm_0_1=0.5, target=target)
        
        # Verify client was created with custom target
        mock_client_class.assert_called_once_with("192.168.1.100", 9000)


class TestSetUtilityGainLinear:
    """Test linear utility gain setter."""
    
    @patch("flaas.util.get_param_range")
    @patch("flaas.util.set_utility_gain_norm")
    def test_set_utility_gain_linear_converts_to_norm(self, mock_set_norm, mock_get_range):
        """Test that linear value is converted to normalized."""
        from flaas.param_map import ParamRange
        
        # Mock param range: -1.0 to +1.0 linear maps to 0.0 to 1.0 normalized
        mock_get_range.return_value = ParamRange(
            min=-1.0,
            max=1.0
        )
        
        set_utility_gain_linear(track_id=-1000, device_id=0, gain_linear=0.0)
        
        # 0.0 linear should map to 0.5 normalized
        mock_set_norm.assert_called_once()
        # Check positional args
        call_args = mock_set_norm.call_args[0]
        assert abs(call_args[2] - 0.5) < 0.01  # gain_norm_0_1 is 3rd positional arg
    
    @patch("flaas.util.get_param_range")
    @patch("flaas.util.set_utility_gain_norm")
    def test_set_utility_gain_linear_max_value(self, mock_set_norm, mock_get_range):
        """Test that max linear value maps to 1.0 normalized."""
        from flaas.param_map import ParamRange
        
        mock_get_range.return_value = ParamRange(
            min=-1.0,
            max=1.0
        )
        
        set_utility_gain_linear(track_id=-1000, device_id=0, gain_linear=1.0)
        
        call_args = mock_set_norm.call_args[0]
        assert abs(call_args[2] - 1.0) < 0.01
    
    @patch("flaas.util.get_param_range")
    @patch("flaas.util.set_utility_gain_norm")
    def test_set_utility_gain_linear_min_value(self, mock_set_norm, mock_get_range):
        """Test that min linear value maps to 0.0 normalized."""
        from flaas.param_map import ParamRange
        
        mock_get_range.return_value = ParamRange(
            min=-1.0,
            max=1.0
        )
        
        set_utility_gain_linear(track_id=-1000, device_id=0, gain_linear=-1.0)
        
        call_args = mock_set_norm.call_args[0]
        assert abs(call_args[2] - 0.0) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
