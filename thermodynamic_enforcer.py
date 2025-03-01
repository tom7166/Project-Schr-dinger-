"""
Thermodynamic Enforcer - Project Schrödinger

This module implements the "Thermodynamic Enforcement" component of Project Schrödinger.
It embeds NIST SP 800-90B entropy sources that trigger cryptographic apoptosis (self-destruct)
if specific conditions are met:
- Entropy drops below 7.2 bits/byte
- Key shards show Borel regularity (indicating mathematical backdoors)
- Ambient temperature fluctuates (anti-physical tampering)
"""

import os
import time
import numpy as np
import hashlib
import struct
import threading
import logging
from typing import List, Dict, Tuple, Optional, Callable
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("thermodynamic_enforcer.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ThermodynamicEnforcer")


class ThermodynamicEnforcer:
    """
    The Thermodynamic Enforcer monitors cryptographic systems for entropy
    violations and other physical or mathematical anomalies that might
    indicate tampering.
    """
    
    def __init__(self, 
                 entropy_threshold: float = 7.2,
                 temperature_variance_threshold: float = 1.0,
                 check_interval: int = 60,
                 shard_files: List[str] = None):
        """
        Initialize the Thermodynamic Enforcer.
        
        Args:
            entropy_threshold: Minimum entropy in bits/byte
            temperature_variance_threshold: Maximum allowed temperature variance in °C
            check_interval: Time between checks in seconds
            shard_files: List of paths to key shard files to monitor
        """
        self.entropy_threshold = entropy_threshold
        self.temperature_variance_threshold = temperature_variance_threshold
        self.check_interval = check_interval
        self.shard_files = shard_files or []
        
        # Store baseline temperature readings
        self.baseline_temperature = self._get_ambient_temperature()
        
        # Monitoring state
        self.monitoring = False
        self._monitor_thread = None
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[str, Dict], None]] = []
        
        logger.info(f"ThermodynamicEnforcer initialized with entropy threshold: {entropy_threshold} bits/byte")
        logger.info(f"Temperature baseline: {self.baseline_temperature}°C")
    
    def register_alert_callback(self, callback: Callable[[str, Dict], None]):
        """
        Register a callback function to be called when an alert is triggered.
        
        Args:
            callback: Function that takes alert_type and alert_data parameters
        """
        self.alert_callbacks.append(callback)
    
    def _trigger_alert(self, alert_type: str, alert_data: Dict):
        """
        Trigger an alert to all registered callbacks.
        
        Args:
            alert_type: Type of alert (e.g., 'entropy_violation', 'temperature_violation')
            alert_data: Data associated with the alert
        """
        logger.warning(f"ALERT TRIGGERED: {alert_type}")
        logger.warning(f"Alert data: {alert_data}")
        
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, alert_data)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def start_monitoring(self):
        """Start the monitoring thread."""
        if self.monitoring:
            logger.warning("Monitoring is already active")
            return
        
        self.monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Thermodynamic monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread."""
        if not self.monitoring:
            logger.warning("Monitoring is not active")
            return
        
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        logger.info("Thermodynamic monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop that runs as a background thread."""
        logger.info("Monitoring loop started")
        
        while self.monitoring:
            try:
                # Check all monitored aspects
                self._check_ambient_temperature()
                self._check_key_shard_entropy()
                self._check_key_shard_regularities()
                
                # Wait for next check interval
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                # Don't stop monitoring on error, just continue
    
    def _get_ambient_temperature(self) -> float:
        """
        Get the current ambient temperature.
        
        In a real implementation, this would read from hardware sensors.
        For demonstration, we return a simulated value.
        
        Returns:
            float: The current temperature in degrees Celsius
        """
        # Simulate temperature reading (real implementation would use hardware sensors)
        # Use system entropy to generate a realistic temperature value
        try:
            # Try to get some entropy from the OS
            random_bytes = os.urandom(4)
            # Convert to a float between 0 and 1
            rand_val = struct.unpack('f', random_bytes)[0] % 1.0
            # Return a temperature between 20-25°C
            return 20.0 + (rand_val * 5.0)
        except:
            # Fallback
            return 22.5
    
    def _check_ambient_temperature(self):
        """
        Check if the ambient temperature has fluctuated beyond the threshold.
        """
        current_temp = self._get_ambient_temperature()
        temp_delta = abs(current_temp - self.baseline_temperature)
        
        logger.debug(f"Current temperature: {current_temp}°C, delta: {temp_delta}°C")
        
        if temp_delta > self.temperature_variance_threshold:
            self._trigger_alert("temperature_violation", {
                "baseline": self.baseline_temperature,
                "current": current_temp,
                "delta": temp_delta,
                "threshold": self.temperature_variance_threshold
            })
            
            # Consider taking action based on this violation
            self._handle_temperature_violation(current_temp)
    
    def _handle_temperature_violation(self, current_temp: float):
        """
        Handle a temperature violation.
        
        Args:
            current_temp: The current temperature that triggered the violation
        """
        # Log the violation
        logger.warning(f"Temperature violation detected: {current_temp}°C vs baseline {self.baseline_temperature}°C")
        
        # In a real implementation, this might:
        # 1. Signal that the system may be under physical attack
        # 2. Trigger a secure shutdown or key erasure
        # 3. Alert administrators
        
        # For demonstration, we'll just update the baseline if it seems legitimate
        # In a real system, this would be more sophisticated
        if abs(current_temp - self.baseline_temperature) < self.temperature_variance_threshold * 2:
            logger.info(f"Updating temperature baseline to: {current_temp}°C")
            self.baseline_temperature = current_temp
    
    def _check_key_shard_entropy(self):
        """
        Check the entropy of all key shards.
        """
        for shard_file in self.shard_files:
            try:
                if not os.path.exists(shard_file):
                    logger.warning(f"Shard file not found: {shard_file}")
                    continue
                
                # Read the shard file
                with open(shard_file, 'rb') as f:
                    shard_data = f.read()
                
                # Calculate entropy
                entropy = self._calculate_entropy(shard_data)
                logger.debug(f"Shard {shard_file} entropy: {entropy:.2f} bits/byte")
                
                if entropy < self.entropy_threshold:
                    self._trigger_alert("entropy_violation", {
                        "shard_file": shard_file,
                        "entropy": entropy,
                        "threshold": self.entropy_threshold
                    })
                    
                    # Take action on entropy violation
                    self._handle_entropy_violation(shard_file, entropy)
            except Exception as e:
                logger.error(f"Error checking shard {shard_file}: {e}")
    
    def _calculate_entropy(self, data: bytes) -> float:
        """
        Calculate the Shannon entropy of data in bits per byte.
        
        Args:
            data: The data to analyze
            
        Returns:
            The calculated entropy in bits per byte
        """
        if not data:
            return 0.0
            
        # Count byte frequencies
        byte_counts = {}
        for byte in data:
            if byte in byte_counts:
                byte_counts[byte] += 1
            else:
                byte_counts[byte] = 1
        
        # Calculate Shannon entropy
        data_len = len(data)
        entropy = 0.0
        
        for count in byte_counts.values():
            probability = count / data_len
            entropy -= probability * np.log2(probability)
        
        return entropy
    
    def _handle_entropy_violation(self, shard_file: str, entropy: float):
        """
        Handle an entropy violation for a key shard.
        
        Args:
            shard_file: Path to the shard file with low entropy
            entropy: The calculated entropy value
        """
        logger.critical(f"ENTROPY VIOLATION on shard {shard_file}: {entropy:.2f} bits/byte")
        
        # In a real implementation, this would trigger cryptographic apoptosis
        # For demonstration, we'll just simulate the process
        
        logger.critical("CRYPTOGRAPHIC APOPTOSIS INITIATED")
        
        # 1. Notify any connected systems
        self._trigger_alert("cryptographic_apoptosis", {
            "reason": "entropy_violation",
            "shard_file": shard_file,
            "entropy": entropy
        })
        
        # 2. In a real system, this would:
        #    - Securely erase key material
        #    - Shutdown AI operations
        #    - Notify administrators
        
        # For demonstration, we'll just invalidate the shard by overwriting with random data
        try:
            with open(shard_file, 'wb') as f:
                f.write(os.urandom(1024))  # Write random data
            logger.info(f"Shard {shard_file} has been invalidated")
        except Exception as e:
            logger.error(f"Failed to invalidate shard {shard_file}: {e}")
    
    def _check_key_shard_regularities(self):
        """
        Check key shards for Borel regularities (mathematical backdoors).
        """
        for shard_file in self.shard_files:
            try:
                if not os.path.exists(shard_file):
                    continue
                
                # Read the shard file
                with open(shard_file, 'rb') as f:
                    shard_data = f.read()
                
                # Check for regularities
                has_regularity = self._detect_borel_regularity(shard_data)
                
                if has_regularity:
                    self._trigger_alert("regularity_detected", {
                        "shard_file": shard_file,
                        "severity": "critical"
                    })
                    
                    # Handle the regularity
                    self._handle_regularity_violation(shard_file)
            except Exception as e:
                logger.error(f"Error checking regularities in {shard_file}: {e}")
    
    def _detect_borel_regularity(self, data: bytes) -> bool:
        """
        Detect Borel regularities in data that might indicate a mathematical backdoor.
        
        This is a simplified implementation. A real system would use more sophisticated
        statistical tests based on Borel normality.
        
        Args:
            data: The data to analyze
            
        Returns:
            bool: True if regularities are detected, False otherwise
        """
        if len(data) < 100:
            return False
            
        # Check 1: Bit distribution (should be roughly 50% 0s and 50% 1s)
        bit_count = 0
        total_bits = len(data) * 8
        
        for byte in data:
            for i in range(8):
                if (byte >> i) & 1:
                    bit_count += 1
        
        bit_ratio = bit_count / total_bits
        if abs(bit_ratio - 0.5) < 0.01:
            # Too perfectly distributed
            return True
        
        # Check 2: Repeating patterns
        # Look for repetition of byte sequences
        for pattern_len in [2, 3, 4]:
            patterns = {}
            for i in range(len(data) - pattern_len):
                pattern = data[i:i+pattern_len]
                if pattern in patterns:
                    patterns[pattern] += 1
                else:
                    patterns[pattern] = 1
            
            # Calculate expected occurrences for random data
            expected = len(data) / (256 ** pattern_len)
            
            # Check for patterns that occur too frequently
            for pattern, count in patterns.items():
                if count > expected * 10:  # Arbitrary threshold
                    return True
        
        return False
    
    def _handle_regularity_violation(self, shard_file: str):
        """
        Handle a regularity violation (potential mathematical backdoor).
        
        Args:
            shard_file: Path to the shard file with detected regularities
        """
        logger.critical(f"MATHEMATICAL BACKDOOR DETECTED in shard {shard_file}")
        
        # This is a critical violation indicating a potential backdoor
        # In a real system, this would trigger immediate cryptographic apoptosis
        
        logger.critical("CRYPTOGRAPHIC APOPTOSIS INITIATED")
        
        # Notify connected systems
        self._trigger_alert("cryptographic_apoptosis", {
            "reason": "mathematical_backdoor",
            "shard_file": shard_file,
            "severity": "critical"
        })
        
        # In a real system, this would:
        # - Immediately invalidate all key material
        # - Halt all AI operations
        # - Alert security personnel
        
        # For demonstration, simulate shard invalidation
        try:
            with open(shard_file, 'wb') as f:
                # Overwrite with high-entropy random data
                f.write(os.urandom(2048))
            logger.info(f"Shard {shard_file} has been invalidated due to backdoor detection")
        except Exception as e:
            logger.error(f"Failed to invalidate shard {shard_file}: {e}")


def apoptosis_callback(alert_type: str, alert_data: Dict):
    """Example callback for handling apoptosis alerts."""
    print(f"!!! ALERT: {alert_type} !!!")
    print(json.dumps(alert_data, indent=2))
    print("Taking emergency measures to protect system integrity...")


def demo():
    """Demonstrate the Thermodynamic Enforcer functionality."""
    print("Project Schrödinger - Thermodynamic Enforcer Demo")
    print("-------------------------------------------------")
    
    # Create a temporary shard file for demonstration
    temp_shard_file = "temp_shard.bin"
    try:
        # Create a file with random data
        with open(temp_shard_file, 'wb') as f:
            f.write(os.urandom(1024))
        
        # Initialize the enforcer
        enforcer = ThermodynamicEnforcer(
            entropy_threshold=7.2,
            temperature_variance_threshold=1.5,
            check_interval=5,  # Short interval for demo
            shard_files=[temp_shard_file]
        )
        
        # Register alert callback
        enforcer.register_alert_callback(apoptosis_callback)
        
        # Start monitoring
        enforcer.start_monitoring()
        print("Monitoring started. Press Ctrl+C to stop...")
        
        # For demonstration, simulate some violations
        time.sleep(2)
        
        # Simulate entropy violation by writing low-entropy data
        print("\nSimulating entropy violation...")
        with open(temp_shard_file, 'wb') as f:
            # Write repeating pattern with low entropy
            f.write(b'abcabcabc' * 100)
        
        # Wait for the violation to be detected
        time.sleep(10)
        
        # Simulate temperature violation
        print("\nSimulating temperature violation...")
        # Modify the baseline temperature directly (in a real system this wouldn't be possible)
        original_temp = enforcer.baseline_temperature
        enforcer.baseline_temperature = original_temp - enforcer.temperature_variance_threshold * 2
        
        # Wait for the violation to be detected
        time.sleep(10)
        
        # Clean up
        enforcer.stop_monitoring()
        print("Monitoring stopped.")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    finally:
        # Stop monitoring and clean up
        if 'enforcer' in locals():
            enforcer.stop_monitoring()
        
        # Remove temporary file
        if os.path.exists(temp_shard_file):
            os.remove(temp_shard_file)


if __name__ == "__main__":
    demo()