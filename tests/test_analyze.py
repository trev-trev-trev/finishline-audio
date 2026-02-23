"""Unit tests for analyze.py - LUFS/True Peak measurement."""
import pytest
import numpy as np
import soundfile as sf
from pathlib import Path
from flaas.analyze import analyze_wav


class TestAnalyze:
    """Test audio analysis functions."""
    
    @pytest.fixture
    def test_wav(self, tmp_path):
        """Create a test WAV file."""
        # Generate 1 second of sine wave at 440 Hz
        sample_rate = 48000
        duration = 1.0
        frequency = 440.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = np.sin(2 * np.pi * frequency * t) * 0.5  # -6 dBFS
        audio_stereo = np.stack([audio, audio], axis=1)
        
        wav_path = tmp_path / "test.wav"
        sf.write(wav_path, audio_stereo, sample_rate)
        return wav_path
    
    @pytest.fixture
    def silent_wav(self, tmp_path):
        """Create a silent WAV file."""
        sample_rate = 48000
        duration = 0.5
        audio = np.zeros((int(sample_rate * duration), 2))
        
        wav_path = tmp_path / "silent.wav"
        sf.write(wav_path, audio, sample_rate)
        return wav_path
    
    @pytest.fixture
    def clipping_wav(self, tmp_path):
        """Create a clipping WAV file."""
        sample_rate = 48000
        duration = 0.5
        audio = np.ones((int(sample_rate * duration), 2))  # 0 dBFS
        
        wav_path = tmp_path / "clipping.wav"
        sf.write(wav_path, audio, sample_rate)
        return wav_path
    
    def test_analyze_wav_returns_analysis_result(self, test_wav):
        """Test that analyze_wav returns an AnalysisResult."""
        result = analyze_wav(test_wav)
        assert hasattr(result, 'lufs_i')
        assert hasattr(result, 'peak_dbfs')
        assert hasattr(result, 'true_peak_dbtp')
    
    def test_analyze_wav_has_required_fields(self, test_wav):
        """Test that result contains required fields."""
        result = analyze_wav(test_wav)
        assert hasattr(result, 'lufs_i')
        assert hasattr(result, 'peak_dbfs')
        assert hasattr(result, 'true_peak_dbtp')
        assert hasattr(result, 'file')
        assert hasattr(result, 'sr')
    
    def test_analyze_wav_lufs_range(self, test_wav):
        """Test LUFS is in reasonable range for -6 dBFS sine wave."""
        result = analyze_wav(test_wav)
        # -6 dBFS sine wave should be around -9 to -12 LUFS
        assert -20 < result.lufs_i < 0
    
    def test_analyze_wav_peak_dbfs(self, test_wav):
        """Test peak is approximately -6 dBFS."""
        result = analyze_wav(test_wav)
        # Should be close to -6 dBFS (0.5 amplitude)
        expected_peak = 20 * np.log10(0.5)  # ~-6.02 dB
        assert abs(result.peak_dbfs - expected_peak) < 0.5
    
    def test_analyze_wav_true_peak_higher_than_peak(self, test_wav):
        """Test that true peak is typically higher than sample peak."""
        result = analyze_wav(test_wav)
        # For sine wave, true peak should be slightly higher or equal
        assert result.true_peak_dbtp >= result.peak_dbfs
    
    def test_silent_audio_lufs(self, silent_wav):
        """Test that silent audio returns very low LUFS."""
        result = analyze_wav(silent_wav)
        assert result.lufs_i < -70  # Should be extremely low
    
    def test_clipping_audio_peak(self, clipping_wav):
        """Test that clipping audio is detected at 0 dBFS."""
        result = analyze_wav(clipping_wav)
        assert result.peak_dbfs > -0.1  # Very close to 0 dBFS
    
    def test_true_peak_calculation_internal(self, test_wav):
        """Test that true peak calculation works internally."""
        result = analyze_wav(test_wav)
        # True peak should exist and be a finite number
        assert hasattr(result, 'true_peak_dbtp')
        assert -100 < result.true_peak_dbtp < 10
    
    def test_analyze_wav_with_path_string(self, test_wav):
        """Test that analyze_wav works with string path."""
        result = analyze_wav(str(test_wav))
        assert hasattr(result, 'lufs_i')
        assert hasattr(result, 'peak_dbfs')
    
    def test_analyze_wav_with_path_object(self, test_wav):
        """Test that analyze_wav works with Path object."""
        result = analyze_wav(Path(test_wav))
        assert hasattr(result, 'lufs_i')
        assert hasattr(result, 'peak_dbfs')
    
    def test_analyze_nonexistent_file(self):
        """Test that analyzing nonexistent file raises error."""
        with pytest.raises(Exception):
            analyze_wav("nonexistent.wav")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
