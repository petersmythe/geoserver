#!/usr/bin/env python3
"""
Compare WMTS, CSW, and WPS implementations against OGC specifications.
"""

import json
import sys

print("Starting compliance analysis...", flush=True)

def load_json(filepath):
    """Load JSON file."""
    print(f"Loading {filepath}...", flush=True)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_service(service_name, impl_data, spec_data):
    """Compare a service implementation against its specification."""
    
    print(f"Comparing {service_name}...", flush=True)
    
    result = {
        "service": service_name,
        "versions": {}
    }
    
    # Get implemented versions
    impl_versions = impl_data.get("versions", [])
    print(f"  Found {len(impl_versions)} implemented versions", flush=True)
    
    # Process each version
    for version in impl_versions:
        print(f"  Processing version {version}...", flush=True)
        version_result = {
            "version": version,
            "specification_url": "",
            "compliance_status": "UNKNOWN",
            "missing_required_operations": [],
            "missing_optional_operations": [],
            "extra_operations": [],
            "operation_details": []
        }
        
        # Get spec for this version
        spec_version = spec_data["services"][service_name]["versions"].get(version)
        if not spec_version:
            version_result["compliance_status"] = "NO_SPEC_FOUND"
            version_result["note"] = f"No OGC specification found for {service_name} {version}"
            result["versions"][version] = version_result
            continue
        
        version_result["specification_url"] = spec_version.get("specification_url", "")
        
        # Get implemented operations
        impl_ops = {op["name"]: op for op in impl_data.get("operations", []) 
                    if version in op.get("versions", [])}
        
        # Get required operations from spec
        spec_required_ops = {op["name"]: op for op in spec_version.get("required_operations", [])}
        spec_optional_ops = {op["name"]: op for op in spec_version.get("optional_operations", [])}
        
        print(f"    Impl ops: {len(impl_ops)}, Spec required: {len(spec_required_ops)}, Spec optional: {len(spec_optional_ops)}", flush=True)
        
        # Check for missing required operations
        for op_name in spec_required_ops:
            if op_name not in impl_ops:
                version_result["missing_required_operations"].append({
                    "operation": op_name,
                    "description": spec_required_ops[op_name].get("description", "")
                })
        
        # Check for missing optional operations
        for op_name in spec_optional_ops:
            if op_name not in impl_ops:
                version_result["missing_optional_operations"].append({
                    "operation": op_name,
                    "description": spec_optional_ops[op_name].get("description", "")
                })
        
        # Check for extra operations (vendor extensions)
        all_spec_ops = set(spec_required_ops.keys()) | set(spec_optional_ops.keys())
        for op_name in impl_ops:
            if op_name not in all_spec_ops:
                version_result["extra_operations"].append({
                    "operation": op_name,
                    "description": impl_ops[op_name].get("description", ""),
                    "vendor_extension": impl_ops[op_name].get("vendor_extension", False)
                })
        
        # Detailed parameter comparison for each operation
        for op_name, impl_op in impl_ops.items():
            op_detail = {
                "operation": op_name,
                "status": "UNKNOWN",
                "missing_required_parameters": [],
                "missing_optional_parameters": [],
                "vendor_parameters": [],
                "http_method_mismatch": False
            }
            
            # Find spec operation
            spec_op = spec_required_ops.get(op_name) or spec_optional_ops.get(op_name)
            
            if not spec_op:
                # Vendor extension operation
                op_detail["status"] = "VENDOR_EXTENSION"
                op_detail["note"] = "Operation not in OGC specification"
            else:
                # Compare parameters
                impl_params = {p["name"]: p for p in impl_op.get("parameters", [])}
                spec_required_params = {p["name"]: p for p in spec_op.get("required_parameters", [])}
                spec_optional_params = {p["name"]: p for p in spec_op.get("optional_parameters", [])}
                
                # Check for missing required parameters
                for param_name in spec_required_params:
                    if param_name not in impl_params:
                        op_detail["missing_required_parameters"].append({
                            "parameter": param_name,
                            "type": spec_required_params[param_name].get("type", ""),
                            "description": spec_required_params[param_name].get("description", "")
                        })
                
                # Check for missing optional parameters
                for param_name in spec_optional_params:
                    if param_name not in impl_params:
                        op_detail["missing_optional_parameters"].append({
                            "parameter": param_name,
                            "type": spec_optional_params[param_name].get("type", ""),
                            "description": spec_optional_params[param_name].get("description", "")
                        })
                
                # Check for vendor parameters
                all_spec_params = set(spec_required_params.keys()) | set(spec_optional_params.keys())
                for param_name in impl_params:
                    if param_name not in all_spec_params:
                        op_detail["vendor_parameters"].append({
                            "parameter": param_name,
                            "type": impl_params[param_name].get("type", ""),
                            "description": impl_params[param_name].get("description", "")
                        })
                
                # Check HTTP methods
                impl_methods = set(impl_op.get("http_methods", []))
                spec_methods = set(spec_op.get("http_methods", []))
                if impl_methods != spec_methods:
                    op_detail["http_method_mismatch"] = True
                    op_detail["impl_methods"] = list(impl_methods)
                    op_detail["spec_methods"] = list(spec_methods)
                
                # Determine status
                if op_detail["missing_required_parameters"]:
                    op_detail["status"] = "NON_COMPLIANT"
                elif (op_detail["missing_optional_parameters"] or 
                      op_detail["vendor_parameters"] or 
                      op_detail["http_method_mismatch"]):
                    op_detail["status"] = "COMPLIANT_WITH_EXTENSIONS"
                else:
                    op_detail["status"] = "FULLY_COMPLIANT"
            
            version_result["operation_details"].append(op_detail)
        
        # Determine overall compliance status
        if version_result["missing_required_operations"]:
            version_result["compliance_status"] = "NON_COMPLIANT"
        elif any(op["status"] == "NON_COMPLIANT" for op in version_result["operation_details"]):
            version_result["compliance_status"] = "NON_COMPLIANT"
        elif (version_result["missing_optional_operations"] or 
              version_result["extra_operations"] or
              any(op["status"] == "COMPLIANT_WITH_EXTENSIONS" for op in version_result["operation_details"])):
            version_result["compliance_status"] = "COMPLIANT_WITH_EXTENSIONS"
        else:
            version_result["compliance_status"] = "FULLY_COMPLIANT"
        
        result["versions"][version] = version_result
    
    return result

try:
    # Load data files
    print("Loading data files...", flush=True)
    wmts_impl = load_json("ogc/wmts-operations.json")
    csw_impl = load_json("ogc/csw-operations.json")
    wps_impl = load_json("ogc/wps-operations.json")
    spec_ref = load_json("ogc/spec-reference.json")
    
    # Compare each service
    print("\nComparing services...", flush=True)
    wmts_compliance = compare_service("WMTS", wmts_impl, spec_ref)
    csw_compliance = compare_service("CSW", csw_impl, spec_ref)
    wps_compliance = compare_service("WPS", wps_impl, spec_ref)
    
    # Combine results
    combined_result = {
        "analysis_date": "2026-02-13",
        "description": "OGC compliance analysis for WMTS, CSW, and WPS services",
        "services": {
            "WMTS": wmts_compliance,
            "CSW": csw_compliance,
            "WPS": wps_compliance
        }
    }
    
    # Save combined result
    output_file = "ogc/other-services-compliance.json"
    print(f"\nSaving results to {output_file}...", flush=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_result, f, indent=2)
    
    print(f"✓ Compliance analysis complete!", flush=True)
    
    # Print summary
    print("\n" + "="*80)
    print("COMPLIANCE SUMMARY")
    print("="*80)
    
    for service_name, service_data in combined_result["services"].items():
        print(f"\n{service_name} ({service_data['service']}):")
        for version, version_data in service_data["versions"].items():
            status = version_data["compliance_status"]
            print(f"  Version {version}: {status}")
            
            if version_data["missing_required_operations"]:
                print(f"    ⚠ Missing {len(version_data['missing_required_operations'])} required operations")
            
            if version_data["extra_operations"]:
                print(f"    + {len(version_data['extra_operations'])} vendor extension operations")
            
            non_compliant_ops = [op for op in version_data["operation_details"] 
                                if op["status"] == "NON_COMPLIANT"]
            if non_compliant_ops:
                print(f"    ⚠ {len(non_compliant_ops)} operations missing required parameters")
            
            vendor_ops = [op for op in version_data["operation_details"] 
                         if op["status"] == "VENDOR_EXTENSION"]
            if vendor_ops:
                print(f"    + {len(vendor_ops)} vendor extension operations")
    
    print("\n" + "="*80)
    print("Analysis complete!")
    
except Exception as e:
    print(f"\nERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
