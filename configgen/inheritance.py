"""
Inheritance Engine Module

Handles configuration inheritance and merging.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from copy import deepcopy


logger = logging.getLogger(__name__)


class InheritanceEngine:
    """
    Handles configuration inheritance with:
    - Parent chain resolution
    - Deep merging
    - Override/extend semantics
    - Conflict detection
    """
    
    def __init__(self):
        self._parents: List[Dict[str, Any]] = []
        self._override_keys: Set[str] = set()
        self._merge_strategy: str = 'deep'
    
    def add_parent(self, parent: Dict[str, Any]) -> "InheritanceEngine":
        """
        Add a parent configuration.
        
        Args:
            parent: Parent configuration dictionary.
            
        Returns:
            Self for method chaining.
        """
        self._parents.append(deepcopy(parent))
        return self
    
    def add_parent_override(self, key: str) -> "InheritanceEngine":
        """
        Mark a key as override-only (don't merge arrays/dicts).
        
        Args:
            key: Dot-notation key path.
            
        Returns:
            Self for method chaining.
        """
        self._override_keys.add(key)
        return self
    
    def set_merge_strategy(self, strategy: str) -> "InheritanceEngine":
        """
        Set the merge strategy.
        
        Args:
            strategy: 'deep' (default), 'shallow', or 'replace'.
            
        Returns:
            Self for method chaining.
        """
        self._merge_strategy = strategy
        return self
    
    def merge_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge variables with parent configurations.
        
        Args:
            variables: Child variables to merge.
            
        Returns:
            Merged variables dictionary.
        """
        result = {}
        
        for parent in self._parents:
            self._deep_merge(result, parent)
        
        self._deep_merge(result, variables)
        
        return result
    
    def _deep_merge(
        self,
        target: Dict[str, Any],
        source: Dict[str, Any],
        path: str = ""
    ) -> None:
        """Deep merge source into target."""
        for key, value in source.items():
            current_path = f"{path}.{key}" if path else key
            
            if current_path in self._override_keys or self._merge_strategy == 'replace':
                target[key] = deepcopy(value)
                continue
            
            if key not in target:
                target[key] = deepcopy(value)
                continue
            
            target_value = target[key]
            
            if isinstance(target_value, dict) and isinstance(value, dict):
                self._deep_merge(target_value, value, current_path)
            elif isinstance(target_value, list) and isinstance(value, list):
                if self._merge_strategy == 'shallow':
                    target[key] = value
                else:
                    target[key] = self._merge_lists(target_value, value)
            else:
                target[key] = deepcopy(value)
    
    def _merge_lists(self, base: List, override: List) -> List:
        """Merge two lists with smart deduplication."""
        result = list(base)
        
        for item in override:
            if item not in result:
                result.append(item)
        
        return result
    
    def resolve_inheritance_chain(self) -> List[Dict[str, Any]]:
        """
        Get the full inheritance chain.
        
        Returns:
            List of parent configurations.
        """
        return [deepcopy(p) for p in self._parents]
    
    def clear(self) -> "InheritanceEngine":
        """
        Clear all parent configurations.
        
        Returns:
            Self for method chaining.
        """
        self._parents.clear()
        self._override_keys.clear()
        return self
    
    def detect_conflicts(
        self,
        parent: Dict[str, Any],
        child: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Detect conflicting keys between parent and child.
        
        Args:
            parent: Parent configuration.
            child: Child configuration.
            
        Returns:
            List of conflict descriptions.
        """
        conflicts = []
        
        for key in child:
            if key in parent:
                parent_val = parent[key]
                child_val = child[key]
                
                if type(parent_val) != type(child_val):
                    conflicts.append({
                        'key': key,
                        'parent_type': type(parent_val).__name__,
                        'child_type': type(child_val).__name__,
                    })
        
        return conflicts
