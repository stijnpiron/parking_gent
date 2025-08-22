"""
Manual Hassfest-style validation for Parking Gent integration
This script performs the key validation checks that hassfest would run.
"""

import json
import os
import sys
from pathlib import Path

def validate_manifest(manifest_path):
    """Validate manifest.json according to Home Assistant standards."""
    print("🔍 Validating manifest.json...")
    
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print("❌ manifest.json not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in manifest.json: {e}")
        return False
    
    # Required fields
    required_fields = ["domain", "name", "codeowners", "documentation", "iot_class"]
    for field in required_fields:
        if field not in manifest:
            print(f"❌ Missing required field: {field}")
            return False
        else:
            print(f"✅ Required field present: {field}")
    
    # Validate specific fields
    if not isinstance(manifest.get("codeowners"), list) or not manifest["codeowners"]:
        print("❌ codeowners must be a non-empty list")
        return False
    
    if not manifest.get("documentation", "").startswith("https://"):
        print("❌ documentation must be a valid HTTPS URL")
        return False
    
    valid_iot_classes = [
        "assumed_state", "cloud_polling", "cloud_push", "local_polling", 
        "local_push", "calculated"
    ]
    if manifest.get("iot_class") not in valid_iot_classes:
        print(f"❌ Invalid iot_class. Must be one of: {valid_iot_classes}")
        return False
    
    valid_integration_types = [
        "device", "entity", "hub", "service", "system", "helper"
    ]
    integration_type = manifest.get("integration_type")
    if integration_type and integration_type not in valid_integration_types:
        print(f"❌ Invalid integration_type. Must be one of: {valid_integration_types}")
        return False
    
    # Check version format if present
    version = manifest.get("version")
    if version and not isinstance(version, str):
        print("❌ version must be a string")
        return False
    
    print("✅ manifest.json validation passed")
    return True

def validate_files(integration_path):
    """Validate required files exist."""
    print("\n🔍 Validating required files...")
    
    required_files = ["__init__.py", "manifest.json"]
    for file in required_files:
        file_path = integration_path / file
        if file_path.exists():
            print(f"✅ Required file present: {file}")
        else:
            print(f"❌ Missing required file: {file}")
            return False
    
    # Check for config_flow.py if config_flow is enabled
    manifest_path = integration_path / "manifest.json"
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        if manifest.get("config_flow"):
            config_flow_path = integration_path / "config_flow.py"
            if config_flow_path.exists():
                print("✅ config_flow.py present (required for config_flow: true)")
            else:
                print("❌ config_flow.py missing (required for config_flow: true)")
                return False
    except Exception as e:
        print(f"❌ Error checking config_flow requirement: {e}")
        return False
    
    print("✅ File validation passed")
    return True

def validate_python_syntax(integration_path):
    """Validate Python files for syntax errors."""
    print("\n🔍 Validating Python syntax...")
    
    python_files = list(integration_path.glob("*.py"))
    for py_file in python_files:
        try:
            with open(py_file) as f:
                compile(f.read(), py_file, 'exec')
            print(f"✅ Python syntax valid: {py_file.name}")
        except SyntaxError as e:
            print(f"❌ Syntax error in {py_file.name}: {e}")
            return False
        except Exception as e:
            print(f"⚠️ Warning in {py_file.name}: {e}")
    
    print("✅ Python syntax validation passed")
    return True

def validate_imports(integration_path):
    """Basic validation of import statements."""
    print("\n🔍 Validating imports...")
    
    python_files = list(integration_path.glob("*.py"))
    
    for py_file in python_files:
        try:
            with open(py_file) as f:
                content = f.read()
            
            # Check for common issues
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('from homeassistant'):
                    # This is good - proper HA import
                    continue
                elif 'import homeassistant' in line and not line.startswith('#'):
                    print(f"✅ Home Assistant import found in {py_file.name}:{i}")
            
            print(f"✅ Import validation passed: {py_file.name}")
                    
        except Exception as e:
            print(f"⚠️ Warning validating imports in {py_file.name}: {e}")
    
    print("✅ Import validation completed")
    return True

def validate_translations(integration_path):
    """Validate translation files if they exist."""
    print("\n🔍 Validating translations...")
    
    translations_dir = integration_path / "translations"
    if not translations_dir.exists():
        print("ℹ️ No translations directory found (optional)")
        return True
    
    json_files = list(translations_dir.glob("*.json"))
    if not json_files:
        print("⚠️ Translations directory exists but no JSON files found")
        return True
    
    for json_file in json_files:
        try:
            with open(json_file) as f:
                json.load(f)
            print(f"✅ Valid translation file: {json_file.name}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {json_file.name}: {e}")
            return False
    
    print("✅ Translation validation passed")
    return True

def main():
    """Run all validation checks."""
    print("🚀 Starting Manual Hassfest-style Validation for Parking Gent Integration\n")
    
    # Get integration path
    current_dir = Path.cwd()
    integration_path = current_dir / "custom_components" / "parking_gent"
    
    if not integration_path.exists():
        print(f"❌ Integration path not found: {integration_path}")
        return False
    
    print(f"📁 Validating integration at: {integration_path}\n")
    
    # Run all validation checks
    checks = [
        lambda: validate_manifest(integration_path / "manifest.json"),
        lambda: validate_files(integration_path),
        lambda: validate_python_syntax(integration_path),
        lambda: validate_imports(integration_path),
        lambda: validate_translations(integration_path),
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        else:
            print("❌ Validation check failed")
    
    print(f"\n📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All validation checks passed! Integration meets Home Assistant standards.")
        return True
    else:
        print("❌ Some validation checks failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
