import numpy as np
from cryptography.hazmat.primitives import hashes
import os
import random
import struct


class AdversarialEntropySink:
    """
    Implements the Anti-Deepfake Protocol using adversarial entropy sinks.
    
    This class creates cryptographically engineered "garbage data" that mimics real patterns
    but contains trapdoor statistical flaws, making it difficult for shadow AI models
    to distinguish between real and poisoned data.
    """
    
    def __init__(self, poison_ratio=0.1, complexity_level=3):
        """
        Initialize the entropy sink generator.
        
        Args:
            poison_ratio: Ratio of poisoned data to include (0.0 to 1.0)
            complexity_level: Complexity of the Kolmogorov traps (1-5)
        """
        self.poison_ratio = poison_ratio
        self.complexity_level = min(5, max(1, complexity_level))
        self.markers = [
            b"\x00\xDE\xAD\xFA\x11",
            b"\xCA\xFE\xBA\xBE\x01",
            b"\xFE\xED\xFA\xCE\x02",
            b"\xC0\xDE\xC0\xDE\x03",
            b"\x10\xAD\xBA\x11\x04"
        ]
    
    def _generate_complexity_trap(self, seed, size=64):
        """
        Generate a Kolmogorov complexity trap of given size.
        
        Creates a byte sequence that appears random but follows a pattern
        that's difficult for ML models to discern.
        
        Args:
            seed: Seed value for the trap
            size: Size of the trap in bytes
            
        Returns:
            bytes: The complexity trap
        """
        # Seed the RNG for reproducibility
        random.seed(seed)
        
        # Generate prime numbers for the trap
        primes = []
        n = 1
        while len(primes) < size // 4:
            n += 1
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    break
            else:
                primes.append(n)
        
        # Create a sequence based on complexity level
        if self.complexity_level == 1:
            # Simple XOR pattern
            result = bytes([p ^ (seed & 0xFF) for p in primes])
        elif self.complexity_level == 2:
            # Fibonacci-like sequence
            result = bytes([(p + (p >> 1)) & 0xFF for p in primes])
        elif self.complexity_level == 3:
            # Logistic map chaotic sequence
            x = seed / 255.0
            sequence = []
            for _ in range(size):
                x = 3.9 * x * (1 - x)  # Chaotic behavior
                sequence.append(int(x * 255))
            result = bytes(sequence)
        elif self.complexity_level == 4:
            # Pseudo-random but deterministic sequence
            sequence = []
            x = seed
            for _ in range(size):
                x = (x * 1664525 + 1013904223) % 2**32
                sequence.append(x % 256)
            result = bytes(sequence)
        else:  # level 5
            # Highly complex pattern that mimics encryption
            sequence = bytearray()
            for p in primes:
                # Pack float values derived from primes
                val = float(p) / float(seed + 1)
                sequence.extend(struct.pack('!f', val))
            result = bytes(sequence[:size])
            
        return result
    
    def poison_data(self, data):
        """
        Add adversarial poisoning to data to prevent deepfakes.
        
        Args:
            data: The data to poison (bytes or string)
            
        Returns:
            bytes: The poisoned data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Generate hash of the data
        digest = hashes.Hash(hashes.BLAKE2s(32))
        digest.update(data)
        hash_val = digest.finalize()
        
        # Convert hash to integer for seeding
        seed = int.from_bytes(hash_val[:4], byteorder='big')
        
        # Generate poison based on complexity
        poison_size = int(len(data) * self.poison_ratio)
        poisoned_chunk = self._generate_complexity_trap(seed, poison_size)
        
        # Select a random marker
        marker = self.markers[seed % len(self.markers)]
        
        # Construct the final poisoned data
        if seed % 3 == 0:
            # Prepend the poison
            return poisoned_chunk + marker + data
        elif seed % 3 == 1:
            # Append the poison
            return data + marker + poisoned_chunk
        else:
            # Insert the poison at a deterministic location
            insert_point = (seed % len(data)) if len(data) > 0 else 0
            return data[:insert_point] + marker + poisoned_chunk + data[insert_point:]
    
    def check_poison(self, data):
        """
        Check if data contains poisoned markers.
        
        Args:
            data: The data to check
            
        Returns:
            bool: True if data contains poison markers
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        for marker in self.markers:
            if marker in data:
                return True
        return False


def demo():
    """Demonstrate the adversarial entropy sink functionality"""
    # Create sample data
    sample_text = """This is sample AI training data that could be used to create deepfakes.
    It contains patterns and information that might be extracted by unauthorized models."""
    
    # Create the entropy sink
    entropy_sink = AdversarialEntropySink(poison_ratio=0.2, complexity_level=3)
    
    # Poison the data
    poisoned_data = entropy_sink.poison_data(sample_text)
    
    print(f"Original data size: {len(sample_text)} bytes")
    print(f"Poisoned data size: {len(poisoned_data)} bytes")
    print(f"Poison detected: {entropy_sink.check_poison(poisoned_data)}")
    
    # Show entropy differences
    def calculate_entropy(data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Count byte frequencies
        byte_counts = {}
        for byte in data:
            if byte in byte_counts:
                byte_counts[byte] += 1
            else:
                byte_counts[byte] = 1
        
        # Calculate Shannon entropy
        probabilities = [count / len(data) for count in byte_counts.values()]
        entropy = -sum(p * np.log2(p) for p in probabilities)
        return entropy
    
    original_entropy = calculate_entropy(sample_text)
    poisoned_entropy = calculate_entropy(poisoned_data)
    
    print(f"Original data entropy: {original_entropy:.4f} bits/byte")
    print(f"Poisoned data entropy: {poisoned_entropy:.4f} bits/byte")
    print(f"Entropy increase: {poisoned_entropy - original_entropy:.4f} bits/byte")


if __name__ == "__main__":
    demo()