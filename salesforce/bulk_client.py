"""
Salesforce Bulk API Client Wrapper
Handles bulk operations with job management, batching, and error handling
"""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Iterator
import csv
import io

from simple_salesforce import Salesforce
from simple_salesforce.bulk import SFBulkHandler

from utils.logging import setup_logging

logger = setup_logging(__name__)


class BulkJobResult:
    """Result of a bulk job operation."""
    
    def __init__(self, operation: str, object_name: str):
        self.operation = operation
        self.object_name = object_name
        self.total_records = 0
        self.successful_records = 0
        self.failed_records = 0
        self.failed_rows: List[Dict[str, Any]] = []
        self.created_ids: List[str] = []
        self.completed = False
        self.error_message: Optional[str] = None


class SalesforceBulkClient:
    """Client for Salesforce Bulk API operations."""
    
    def __init__(self, sf_client: Salesforce):
        """Initialize bulk client with Salesforce connection."""
        self.sf = sf_client
        
        # Get session info for bulk handler
        session_id = sf_client.session_id
        bulk_url = sf_client.bulk_url
        
        self.bulk = SFBulkHandler(session_id, bulk_url)
        
        # Configuration
        self.default_batch_size_insert = 5000
        self.default_batch_size_update = 2000
        self.throttle_ms = 100
        self.max_retries = 3
        self.retry_delay_base = 1.0  # seconds
        
        # State directory for failed rows
        self.state_dir = Path(".state")
        self.failed_dir = self.state_dir / "failed"
        self.failed_dir.mkdir(parents=True, exist_ok=True)
    
    def _hash_row(self, row: Dict[str, Any], key_fields: List[str]) -> str:
        """Generate hash for a row based on key fields."""
        hash_data = {}
        for field in key_fields:
            if field in row:
                hash_data[field] = str(row[field])
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _get_existing_records(self, object_name: str, name_prefix: str) -> Dict[str, str]:
        """Query existing records by name prefix to support upserts."""
        try:
            query = f"SELECT Id, Name FROM {object_name} WHERE Name LIKE '{name_prefix}%'"
            result = self.sf.query(query)
            
            existing_records = {}
            for record in result.get('records', []):
                name = record.get('Name', '')
                if name.startswith(name_prefix):
                    existing_records[name] = record['Id']
            
            logger.info(f"Found {len(existing_records)} existing {object_name} records with prefix '{name_prefix}'")
            return existing_records
            
        except Exception as e:
            logger.error(f"Error querying existing {object_name} records: {e}")
            return {}
    
    def _split_upsert_data(self, rows: List[Dict[str, Any]], object_name: str, 
                          name_prefix: str) -> Tuple[List[Dict], List[Dict]]:
        """Split data into inserts vs updates for upsert operations."""
        existing_records = self._get_existing_records(object_name, name_prefix)
        
        inserts = []
        updates = []
        
        for row in rows:
            name = row.get('Name', '')
            if name in existing_records:
                # Update existing record
                row['Id'] = existing_records[name]
                updates.append(row)
            else:
                # Insert new record
                inserts.append(row)
        
        logger.info(f"Split {len(rows)} {object_name} records: {len(inserts)} inserts, {len(updates)} updates")
        return inserts, updates
    
    async def bulk_insert(self, object_name: str, rows: List[Dict[str, Any]], 
                         batch_size: Optional[int] = None) -> BulkJobResult:
        """Perform bulk insert operation."""
        if not rows:
            logger.warning(f"No rows to insert for {object_name}")
            return BulkJobResult("insert", object_name)
        
        batch_size = batch_size or self.default_batch_size_insert
        result = BulkJobResult("insert", object_name)
        result.total_records = len(rows)
        
        try:
            logger.info(f"Starting bulk insert for {object_name}: {len(rows)} records")
            
            # Use the submit_dml method for insert
            bulk_result = self.bulk.submit_dml(
                object_name=object_name,
                dml='insert',
                data=rows,
                batch_size=batch_size,
                include_detailed_results=True
            )
            
            # Process results
            if isinstance(bulk_result, list):
                for record_result in bulk_result:
                    if record_result.get('success', False):
                        result.successful_records += 1
                        # Store the created ID if available
                        if 'id' in record_result and record_result['id']:
                            result.created_ids.append(record_result['id'])
                    else:
                        result.failed_records += 1
                        error_msg = record_result.get('errors', ['Unknown error'])
                        failed_row = {
                            'error': error_msg[0] if error_msg else 'Unknown error',
                            'row_data': record_result
                        }
                        result.failed_rows.append(failed_row)
            else:
                # Handle case where result is not a list
                result.successful_records = len(rows)
            
            logger.info(f"Bulk insert completed: {result.successful_records} successful, {result.failed_records} failed")
            
        except Exception as e:
            logger.error(f"Error in bulk insert for {object_name}: {e}")
            result.error_message = str(e)
            result.failed_records = len(rows)
        
        # Save failed rows
        self.save_failed_rows(result)
        
        return result
    
    async def bulk_update(self, object_name: str, rows: List[Dict[str, Any]], 
                         batch_size: Optional[int] = None) -> BulkJobResult:
        """Perform bulk update operation."""
        if not rows:
            logger.warning(f"No rows to update for {object_name}")
            return BulkJobResult("update", object_name)
        
        batch_size = batch_size or self.default_batch_size_update
        result = BulkJobResult("update", object_name)
        result.total_records = len(rows)
        
        try:
            logger.info(f"Starting bulk update for {object_name}: {len(rows)} records")
            
            # Use the submit_dml method for update
            bulk_result = self.bulk.submit_dml(
                object_name=object_name,
                dml='update',
                data=rows,
                batch_size=batch_size,
                include_detailed_results=True
            )
            
            # Process results
            if isinstance(bulk_result, list):
                for record_result in bulk_result:
                    if record_result.get('success', False):
                        result.successful_records += 1
                    else:
                        result.failed_records += 1
                        error_msg = record_result.get('errors', ['Unknown error'])
                        failed_row = {
                            'error': error_msg[0] if error_msg else 'Unknown error',
                            'row_data': record_result
                        }
                        result.failed_rows.append(failed_row)
            else:
                # Handle case where result is not a list
                result.successful_records = len(rows)
            
            logger.info(f"Bulk update completed: {result.successful_records} successful, {result.failed_records} failed")
            
        except Exception as e:
            logger.error(f"Error in bulk update for {object_name}: {e}")
            result.error_message = str(e)
            result.failed_records = len(rows)
        
        # Save failed rows
        self.save_failed_rows(result)
        
        return result
    
    async def bulk_upsert(self, object_name: str, rows: List[Dict[str, Any]], 
                         name_prefix: str, batch_size_insert: Optional[int] = None,
                         batch_size_update: Optional[int] = None) -> Tuple[BulkJobResult, BulkJobResult]:
        """Perform bulk upsert operation by splitting into inserts and updates."""
        if not rows:
            logger.warning(f"No rows to upsert for {object_name}")
            empty_result = BulkJobResult("upsert", object_name)
            return empty_result, empty_result
        
        # Split into inserts and updates
        inserts, updates = self._split_upsert_data(rows, object_name, name_prefix)
        
        # Perform inserts and updates
        insert_result = await self.bulk_insert(object_name, inserts, batch_size_insert)
        update_result = await self.bulk_update(object_name, updates, batch_size_update)
        
        return insert_result, update_result
    
    def save_failed_rows(self, result: BulkJobResult):
        """Save failed rows to file for debugging."""
        if not result.failed_rows:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{result.object_name}_{timestamp}.json"
        filepath = self.failed_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(result.failed_rows, f, indent=2)
            
            logger.info(f"Saved {len(result.failed_rows)} failed rows to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving failed rows: {e}")
