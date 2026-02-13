#!/usr/bin/env python3
"""
Scan REST API source directories for Java controller files.
Identifies files containing @RestController or @Controller annotations.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Set

# Directories to scan
SCAN_DIRS = [
    "src/rest/",
    "src/restconfig/",
    "src/restconfig-wcs/",
    "src/restconfig-wfs/",
    "src/restconfig-wms/",
    "src/restconfig-wmts/",
    "src/gwc-rest/"
]

def find_java_files(directory: str) -> List[str]:
    """Find all Java files in a directory recursively."""
    java_files = []
    dir_path = Path(directory)
    
    if not dir_path.exists():
        print(f"Warning: Directory {directory} does not exist")
        return java_files
    
    for java_file in dir_path.rglob("*.java"):
        java_files.append(str(java_file))
    
    return java_files

def is_controller_file(file_path: str) -> tuple[bool, List[str]]:
    """
    Check if a Java file contains @RestController or @Controller annotations.
    Returns (is_controller, list_of_annotations_found)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Look for @RestController or @Controller annotations
        annotations_found = []
        
        if re.search(r'@RestController\b', content):
            annotations_found.append('@RestController')
        
        if re.search(r'@Controller\b', content):
            annotations_found.append('@Controller')
        
        return (len(annotations_found) > 0, annotations_found)
    
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return (False, [])

def extract_class_info(file_path: str) -> Dict:
    """Extract class name and package from Java file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract package
        package_match = re.search(r'package\s+([\w.]+)\s*;', content)
        package = package_match.group(1) if package_match else "unknown"
        
        # Extract class name (public class or public interface)
        class_match = re.search(r'public\s+(?:class|interface)\s+(\w+)', content)
        class_name = class_match.group(1) if class_match else Path(file_path).stem
        
        return {
            "package": package,
            "className": class_name,
            "fullyQualifiedName": f"{package}.{class_name}"
        }
    
    except Exception as e:
        print(f"Error extracting class info from {file_path}: {e}")
        return {
            "package": "unknown",
            "className": Path(file_path).stem,
            "fullyQualifiedName": "unknown"
        }

def scan_directories() -> Dict:
    """Scan all specified directories for controller files."""
    results = {
        "scanDate": "2026-02-12",
        "scannedDirectories": SCAN_DIRS,
        "summary": {
            "totalJavaFiles": 0,
            "totalControllerFiles": 0,
            "byDirectory": {}
        },
        "controllerFiles": []
    }
    
    all_java_files: Set[str] = set()
    controller_files_data = []
    
    for directory in SCAN_DIRS:
        print(f"Scanning {directory}...")
        
        java_files = find_java_files(directory)
        all_java_files.update(java_files)
        
        controller_count = 0
        
        for java_file in java_files:
            is_controller, annotations = is_controller_file(java_file)
            
            if is_controller:
                controller_count += 1
                class_info = extract_class_info(java_file)
                
                # Get file size
                file_size = os.path.getsize(java_file)
                
                controller_data = {
                    "filePath": java_file.replace("\\", "/"),
                    "fileName": Path(java_file).name,
                    "directory": directory,
                    "annotations": annotations,
                    "package": class_info["package"],
                    "className": class_info["className"],
                    "fullyQualifiedName": class_info["fullyQualifiedName"],
                    "fileSizeBytes": file_size
                }
                
                controller_files_data.append(controller_data)
        
        results["summary"]["byDirectory"][directory] = {
            "totalJavaFiles": len(java_files),
            "controllerFiles": controller_count
        }
        
        print(f"  Found {len(java_files)} Java files, {controller_count} controllers")
    
    results["summary"]["totalJavaFiles"] = len(all_java_files)
    results["summary"]["totalControllerFiles"] = len(controller_files_data)
    results["controllerFiles"] = sorted(controller_files_data, key=lambda x: x["filePath"])
    
    return results

def main():
    """Main execution function."""
    print("Scanning REST API source directories for controller files...")
    print("=" * 70)
    
    results = scan_directories()
    
    # Create output directory if it doesn't exist
    output_dir = Path(".kiro/api-analysis/rest")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write results to JSON file
    output_file = output_dir / "controller-files.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  Total Java files scanned: {results['summary']['totalJavaFiles']}")
    print(f"  Total controller files found: {results['summary']['totalControllerFiles']}")
    print(f"\nOutput written to: {output_file}")
    
    # Print breakdown by directory
    print(f"\nBreakdown by directory:")
    for directory, stats in results['summary']['byDirectory'].items():
        print(f"  {directory}: {stats['controllerFiles']} controllers / {stats['totalJavaFiles']} Java files")

if __name__ == "__main__":
    main()
