"""
Checksum Manager for Delta Mode Operations
Tracks data changes to minimize API usage in subsequent runs
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

from utils.logging import setup_logging

logger = setup_logging(__name__)


class ChecksumManager:
    """Manages checksums for delta mode operations."""
    
    def __init__(self, state_dir: Path = Path(".state")):
        """Initialize checksum manager."""
        self.state_dir = state_dir
        self.checksums_file = state_dir / "seeder_checksums.json"
        self.checksums: Dict[str, Dict[str, str]] = {}
        
        # Ensure state directory exists
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing checksums
        self._load_checksums()
    
    def _load_checksums(self):
        """Load existing checksums from file."""
        try:
            if self.checksums_file.exists():
                with open(self.checksums_file, 'r') as f:
                    self.checksums = json.load(f)
                logger.info(f"Loaded {len(self.checksums)} checksum entries")
            else:
                self.checksums = {}
                logger.info("No existing checksums found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading checksums: {e}")
            self.checksums = {}
    
    def _save_checksums(self):
        """Save checksums to file."""
        try:
            with open(self.checksums_file, 'w') as f:
                json.dump(self.checksums, f, indent=2)
            logger.info(f"Saved {len(self.checksums)} checksum entries")
        except Exception as e:
            logger.error(f"Error saving checksums: {e}")
    
    def _compute_row_hash(self, row: Dict[str, Any], key_fields: List[str]) -> str:
        """Compute hash for a row based on key fields."""
        hash_data = {}
        for field in key_fields:
            if field in row:
                hash_data[field] = str(row[field])
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _compute_batch_hash(self, rows: List[Dict[str, Any]], key_fields: List[str]) -> str:
        """Compute hash for a batch of rows."""
        if not rows:
            return hashlib.md5(b"").hexdigest()
        
        # Sort rows by key fields for consistent hashing
        sorted_rows = sorted(rows, key=lambda x: tuple(str(x.get(field, '')) for field in key_fields))
        
        # Compute hash of all rows
        hash_data = []
        for row in sorted_rows:
            row_hash = self._compute_row_hash(row, key_fields)
            hash_data.append(row_hash)
        
        combined_hash = "|".join(hash_data)
        return hashlib.md5(combined_hash.encode()).hexdigest()
    
    def get_changed_rows(self, object_name: str, rows: List[Dict[str, Any]], 
                        key_fields: List[str]) -> List[Dict[str, Any]]:
        """Get rows that have changed since last run."""
        if not rows:
            return []
        
        # Get previous checksum for this object
        previous_hash = self.checksums.get(object_name, {}).get('batch_hash', '')
        
        # Compute current checksum
        current_hash = self._compute_batch_hash(rows, key_fields)
        
        if previous_hash == current_hash:
            logger.info(f"No changes detected for {object_name} (hash: {current_hash[:8]}...)")
            return []
        
        logger.info(f"Changes detected for {object_name}: {len(rows)} rows (hash: {current_hash[:8]}...)")
        
        # For now, return all rows if hash changed
        # In a more sophisticated implementation, you could track individual row changes
        return rows
    
    def update_checksum(self, object_name: str, rows: List[Dict[str, Any]], 
                       key_fields: List[str]):
        """Update checksum for an object after processing."""
        current_hash = self._compute_batch_hash(rows, key_fields)
        
        if object_name not in self.checksums:
            self.checksums[object_name] = {}
        
        self.checksums[object_name].update({
            'batch_hash': current_hash,
            'row_count': len(rows),
            'last_updated': datetime.now().isoformat(),
            'key_fields': key_fields
        })
        
        logger.info(f"Updated checksum for {object_name}: {current_hash[:8]}... ({len(rows)} rows)")
        self._save_checksums()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all checksums."""
        summary = {
            'total_objects': len(self.checksums),
            'objects': {}
        }
        
        for object_name, data in self.checksums.items():
            summary['objects'][object_name] = {
                'row_count': data.get('row_count', 0),
                'last_updated': data.get('last_updated', 'Unknown'),
                'hash': data.get('batch_hash', '')[:8] + '...'
            }
        
        return summary
    
    def clear_checksums(self):
        """Clear all checksums."""
        self.checksums = {}
        if self.checksums_file.exists():
            self.checksums_file.unlink()
        logger.info("Cleared all checksums")
    
    def get_object_info(self, object_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific object."""
        return self.checksums.get(object_name)
