"""Unit tests for osc_rpc.py - OSC request/response."""
import pytest
import time
from unittest.mock import patch, MagicMock
from flaas.osc_rpc import OscTarget, request_once


class TestOscTarget:
    """Test OscTarget dataclass."""
    
    def test_osctarget_defaults(self):
        """Test OscTarget has correct defaults."""
        target = OscTarget()
        assert target.host == "127.0.0.1"
        assert target.port == 11000
    
    def test_osctarget_custom_values(self):
        """Test OscTarget accepts custom values."""
        target = OscTarget(host="192.168.1.100", port=9000)
        assert target.host == "192.168.1.100"
        assert target.port == 9000
    
    def test_osctarget_frozen(self):
        """Test that OscTarget is immutable (frozen)."""
        target = OscTarget()
        with pytest.raises(Exception):  # FrozenInstanceError
            target.host = "new_host"


class TestRequestOnce:
    """Test request_once RPC function."""
    
    @pytest.fixture
    def mock_server(self):
        """Mock OSC server."""
        with patch("flaas.osc_rpc.ThreadingOSCUDPServer") as mock:
            server_instance = MagicMock()
            mock.return_value = server_instance
            yield server_instance
    
    @pytest.fixture
    def mock_client(self):
        """Mock OSC client."""
        with patch("flaas.osc_rpc.SimpleUDPClient") as mock:
            client_instance = MagicMock()
            mock.return_value = client_instance
            yield client_instance
    
    def test_request_once_returns_tuple(self, mock_server, mock_client):
        """Test that request_once returns a tuple."""
        # Mock queue to return test data immediately
        with patch("flaas.osc_rpc.queue.Queue") as mock_queue:
            queue_instance = MagicMock()
            queue_instance.get.return_value = (1, 2, 3)
            mock_queue.return_value = queue_instance
            
            result = request_once(OscTarget(), "/test/address", 1)
            assert result == (1, 2, 3)
    
    def test_request_once_sends_message(self, mock_server, mock_client):
        """Test that request_once sends OSC message."""
        with patch("flaas.osc_rpc.queue.Queue") as mock_queue:
            queue_instance = MagicMock()
            queue_instance.get.return_value = ("reply",)
            mock_queue.return_value = queue_instance
            
            target = OscTarget(host="localhost", port=8000)
            request_once(target, "/test", 42)
            
            # Verify client was created with correct host/port
            mock_client.send_message.assert_called_once_with("/test", 42)
    
    def test_request_once_timeout(self, mock_server, mock_client):
        """Test that request_once raises TimeoutError on timeout."""
        with patch("flaas.osc_rpc.queue.Queue") as mock_queue:
            import queue
            queue_instance = MagicMock()
            queue_instance.get.side_effect = queue.Empty()
            mock_queue.return_value = queue_instance
            
            with pytest.raises(TimeoutError):
                request_once(OscTarget(), "/test", 1, timeout_sec=0.1)
    
    def test_request_once_custom_listen_port(self, mock_server, mock_client):
        """Test that custom listen port is used."""
        with patch("flaas.osc_rpc.queue.Queue") as mock_queue:
            queue_instance = MagicMock()
            queue_instance.get.return_value = ("reply",)
            mock_queue.return_value = queue_instance
            
            with patch("flaas.osc_rpc.ThreadingOSCUDPServer") as mock_server_class:
                server_instance = MagicMock()
                mock_server_class.return_value = server_instance
                
                request_once(OscTarget(), "/test", 1, listen_port=12345)
                
                # Verify server was created with custom port
                mock_server_class.assert_called_once()
                args = mock_server_class.call_args[0]
                assert args[0][1] == 12345  # Port in (host, port) tuple


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
