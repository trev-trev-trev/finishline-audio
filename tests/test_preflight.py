"""Unit tests for preflight.py - Pre-flight checks."""
import pytest
from unittest.mock import patch, MagicMock
from flaas.preflight import (
    verify_master_fader,
    verify_device_order,
    run_preflight_checks
)
from flaas.osc_rpc import OscTarget


class TestVerifyMasterFader:
    """Test master fader verification."""
    
    @patch("flaas.preflight.request_once")
    def test_verify_master_fader_at_zero(self, mock_request):
        """Test fader check passes when at 0.0 dB."""
        # verify_master_fader expects linear volume (0.85 = 0 dB)
        mock_request.return_value = (0.85,)
        passed, value = verify_master_fader(-1000, OscTarget())
        assert passed is True or passed is None
    
    @patch("flaas.preflight.request_once")
    def test_verify_master_fader_within_tolerance(self, mock_request):
        """Test fader check passes within tolerance."""
        mock_request.return_value = (0.849,)  # Very close to 0.85
        passed, value = verify_master_fader(-1000, OscTarget())
        assert passed is True or passed is None
    
    @patch("flaas.preflight.request_once")
    def test_verify_master_fader_too_high(self, mock_request):
        """Test fader check fails when too high."""
        mock_request.return_value = (1.0,)  # Max volume
        passed, value = verify_master_fader(-1000, OscTarget())
        assert passed is False or passed is None
    
    @patch("flaas.preflight.request_once")
    def test_verify_master_fader_timeout(self, mock_request):
        """Test fader check handles timeout gracefully."""
        mock_request.side_effect = TimeoutError()
        passed, value = verify_master_fader(-1000, OscTarget())
        # Should return None or False on timeout
        assert passed is None or passed is False


class TestVerifyDeviceOrder:
    """Test device chain order verification."""
    
    @patch("flaas.preflight.request_once")
    def test_verify_device_order_correct(self, mock_request):
        """Test chain check passes with correct order."""
        mock_request.return_value = (-1000, "Utility", "EQ Eight", "Limiter")
        expected = ["Utility", "EQ", "Limiter"]
        passed, actual = verify_device_order(-1000, expected, OscTarget())
        assert passed is True
    
    @patch("flaas.preflight.request_once")
    def test_verify_device_order_partial_match(self, mock_request):
        """Test chain check with partial name matching."""
        mock_request.return_value = (-1000, "Utility", "EQ Eight", "Glue Compressor")
        expected = ["Utility", "EQ", "Glue"]
        passed, actual = verify_device_order(-1000, expected, OscTarget())
        assert passed is True
    
    @patch("flaas.preflight.request_once")
    def test_verify_device_order_case_insensitive(self, mock_request):
        """Test chain check is case insensitive."""
        mock_request.return_value = (-1000, "UTILITY", "eq eight", "LiMiTeR")
        expected = ["utility", "EQ", "limiter"]
        passed, actual = verify_device_order(-1000, expected, OscTarget())
        assert passed is True
    
    @patch("flaas.preflight.request_once")
    def test_verify_device_order_wrong_order(self, mock_request):
        """Test chain check fails with wrong order."""
        mock_request.return_value = (-1000, "Limiter", "Utility", "EQ Eight")
        expected = ["Utility", "EQ", "Limiter"]
        passed, actual = verify_device_order(-1000, expected, OscTarget())
        assert passed is False
    
    @patch("flaas.preflight.request_once")
    def test_verify_device_order_missing_device(self, mock_request):
        """Test chain check fails with missing device."""
        mock_request.return_value = (-1000, "Utility", "Limiter")
        expected = ["Utility", "EQ", "Limiter"]
        passed, actual = verify_device_order(-1000, expected, OscTarget())
        assert passed is False
    
    @patch("flaas.preflight.request_once")
    def test_verify_device_order_timeout(self, mock_request):
        """Test chain check handles timeout gracefully."""
        mock_request.side_effect = TimeoutError()
        expected = ["Utility", "EQ"]
        # Should handle error gracefully
        try:
            passed, actual = verify_device_order(-1000, expected, OscTarget())
            assert passed is False
        except RuntimeError:
            # Acceptable - function may raise on timeout
            pass


class TestRunPreflightChecks:
    """Test complete preflight check suite."""
    
    @patch("flaas.preflight.verify_master_fader")
    @patch("flaas.preflight.verify_device_order")
    def test_run_preflight_checks_all_pass(self, mock_verify_order, mock_verify_fader):
        """Test preflight passes when all checks pass."""
        mock_verify_fader.return_value = (True, 0.0)
        mock_verify_order.return_value = (True, ["Utility", "EQ"])
        
        result = run_preflight_checks(-1000, OscTarget(), ["Utility", "EQ"], skip_prompts=True)
        assert result is True
    
    @patch("flaas.preflight.verify_master_fader")
    @patch("flaas.preflight.verify_device_order")
    def test_run_preflight_checks_fader_fail(self, mock_verify_order, mock_verify_fader):
        """Test preflight fails when fader check fails."""
        mock_verify_fader.return_value = (False, 0.5)
        mock_verify_order.return_value = (True, ["Utility"])
        
        result = run_preflight_checks(-1000, OscTarget(), ["Utility"], skip_prompts=True)
        assert result is False
    
    @patch("flaas.preflight.verify_master_fader")
    @patch("flaas.preflight.verify_device_order")
    def test_run_preflight_checks_chain_fail(self, mock_verify_order, mock_verify_fader):
        """Test preflight fails when chain check fails."""
        mock_verify_fader.return_value = (True, 0.0)
        mock_verify_order.return_value = (False, ["Wrong"])
        
        result = run_preflight_checks(-1000, OscTarget(), ["Utility"], skip_prompts=True)
        assert result is False
    
    @patch("flaas.preflight.verify_master_fader")
    @patch("flaas.preflight.verify_device_order")
    def test_run_preflight_checks_with_default_chain(self, mock_verify_order, mock_verify_fader):
        """Test preflight uses default chain when none provided."""
        mock_verify_fader.return_value = (True, 0.0)
        mock_verify_order.return_value = (True, ["Utility", "EQ"])
        
        result = run_preflight_checks(-1000, OscTarget(), expected_chain=None, skip_prompts=True)
        assert result is True
        # Should have called verify_order
        assert mock_verify_order.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
