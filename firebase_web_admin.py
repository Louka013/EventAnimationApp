#!/usr/bin/env python3
"""
Firebase Web SDK wrapper for Python scripts
No service account needed - uses same credentials as web interface
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class FirebaseWebClient:
    def __init__(self):
        self.project_id = "data-base-test-6ef5f"
        self.api_key = "AIzaSyAWGEHQK8f61d4OCgreDRu0fXUjt_sG14w"
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"
    
    def _make_request(self, method: str, url: str, data: Optional[Dict] = None) -> requests.Response:
        """Make authenticated request to Firestore REST API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        params = {"key": self.api_key}
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, params=params, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, params=params, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    
    def _convert_to_firestore_value(self, value: Any) -> Dict[str, Any]:
        """Convert Python value to Firestore value format"""
        if isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, int):
            return {"integerValue": str(value)}
        elif isinstance(value, float):
            return {"doubleValue": value}
        elif isinstance(value, bool):
            return {"booleanValue": value}
        elif isinstance(value, list):
            return {"arrayValue": {"values": [self._convert_to_firestore_value(item) for item in value]}}
        elif isinstance(value, dict):
            return {"mapValue": {"fields": {k: self._convert_to_firestore_value(v) for k, v in value.items()}}}
        elif value is None:
            return {"nullValue": None}
        else:
            return {"stringValue": str(value)}
    
    def _convert_from_firestore_value(self, firestore_value: Dict[str, Any]) -> Any:
        """Convert Firestore value format to Python value"""
        if "stringValue" in firestore_value:
            return firestore_value["stringValue"]
        elif "integerValue" in firestore_value:
            return int(firestore_value["integerValue"])
        elif "doubleValue" in firestore_value:
            return firestore_value["doubleValue"]
        elif "booleanValue" in firestore_value:
            return firestore_value["booleanValue"]
        elif "arrayValue" in firestore_value:
            return [self._convert_from_firestore_value(item) for item in firestore_value["arrayValue"].get("values", [])]
        elif "mapValue" in firestore_value:
            return {k: self._convert_from_firestore_value(v) for k, v in firestore_value["mapValue"].get("fields", {}).items()}
        elif "nullValue" in firestore_value:
            return None
        else:
            return str(firestore_value)
    
    def set_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> bool:
        """Set a document in Firestore"""
        url = f"{self.base_url}/{collection}/{document_id}"
        
        # Convert data to Firestore format
        firestore_data = {
            "fields": {k: self._convert_to_firestore_value(v) for k, v in data.items()}
        }
        
        response = self._make_request("PATCH", url, firestore_data)
        return response.status_code == 200
    
    def add_document(self, collection: str, data: Dict[str, Any]) -> Optional[str]:
        """Add a document to Firestore collection"""
        url = f"{self.base_url}/{collection}"
        
        # Convert data to Firestore format
        firestore_data = {
            "fields": {k: self._convert_to_firestore_value(v) for k, v in data.items()}
        }
        
        response = self._make_request("POST", url, firestore_data)
        if response.status_code == 200:
            result = response.json()
            # Extract document ID from the response
            document_path = result.get("name", "")
            return document_path.split("/")[-1]
        return None
    
    def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore"""
        url = f"{self.base_url}/{collection}/{document_id}"
        
        response = self._make_request("GET", url)
        if response.status_code == 200:
            result = response.json()
            if "fields" in result:
                return {k: self._convert_from_firestore_value(v) for k, v in result["fields"].items()}
        return None
    
    def list_documents(self, collection: str) -> list:
        """List all documents in a collection"""
        url = f"{self.base_url}/{collection}"
        
        response = self._make_request("GET", url)
        if response.status_code == 200:
            result = response.json()
            documents = []
            for doc in result.get("documents", []):
                doc_id = doc["name"].split("/")[-1]
                doc_data = {k: self._convert_from_firestore_value(v) for k, v in doc.get("fields", {}).items()}
                documents.append({"id": doc_id, "data": doc_data})
            return documents
        return []
    
    def update_document(self, collection: str, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update specific fields in a document"""
        return self.set_document(collection, document_id, updates)
    
    def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document from Firestore"""
        url = f"{self.base_url}/{collection}/{document_id}"
        
        response = self._make_request("DELETE", url)
        return response.status_code == 200
    
    def query_documents(self, collection: str, field: str, operator: str, value: Any) -> list:
        """Query documents with simple field filter"""
        # For this implementation, we'll list all documents and filter client-side
        # This is less efficient but works without complex query syntax
        documents = self.list_documents(collection)
        
        filtered_docs = []
        for doc in documents:
            doc_value = doc["data"].get(field)
            if operator == "==" and doc_value == value:
                filtered_docs.append(doc)
            elif operator == "!=" and doc_value != value:
                filtered_docs.append(doc)
            # Add more operators as needed
        
        return filtered_docs
    
    def set_document_at_path(self, path: str, data: Dict[str, Any]) -> bool:
        """Set a document at a specific path (supports subcollections)"""
        # Path format: "collection/doc/subcollection/subdoc"
        url = f"{self.base_url}/{path}"
        
        # Convert data to Firestore format
        firestore_data = {
            "fields": {k: self._convert_to_firestore_value(v) for k, v in data.items()}
        }
        
        response = self._make_request("PATCH", url, firestore_data)
        return response.status_code == 200
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat() + "Z"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format (internal method)"""
        return self.get_current_timestamp()