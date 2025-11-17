#!/usr/bin/env python3
"""
Build Sphinx documentation for ebay_rest.

This script:
1. Reads source code from the repo (src/ebay_rest/)
2. Generates RST files automatically to docs/source/
3. Creates Sphinx configuration
4. Builds HTML documentation
5. Outputs to docs/build/
"""

import os
import re
import sys
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace


def get_project_root():
    """Get the project root directory."""
    # This script is in docs/, so go up one level
    return Path(__file__).parent.parent.absolute()


def get_api_file_path(project_root):
    """Get the path to the API file in the repo."""
    api_path = project_root / "src" / "ebay_rest" / "a_p_i.py"
    if not api_path.exists():
        raise FileNotFoundError(f"API file not found at {api_path}")
    return api_path


def create_conf_py(docs_dir, project_root):
    """Create the Sphinx conf.py file from template."""
    # Calculate relative path from source_dir to src
    source_dir = docs_dir / "source"
    src_path = project_root / "src"
    rel_path = os.path.relpath(src_path, source_dir)

    # Read template file
    template_path = docs_dir / "conf.py.template"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        conf_content = f.read().format(src_path=rel_path)

    # conf.py must be in the source directory for Sphinx
    conf_path = docs_dir / "source" / "conf.py"
    with open(conf_path, "w", encoding="utf-8") as f:
        f.write(conf_content)
    print(f"✓ Created {conf_path}")


def extract_methods(api_path):
    """Extract all public methods from the API class."""
    with open(api_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find all method definitions in the API class
    methods = []
    in_api_class = False
    api_class_indent = None

    for i, line in enumerate(lines):
        # Check if we're entering the API class
        if re.match(r"^class\s+API\s*\(", line):
            in_api_class = True
            # Get the indentation level (should be 0, but check anyway)
            api_class_indent = len(line) - len(line.lstrip())
            continue

        # Check if we're leaving the API class (another class definition at same or less indent)
        if in_api_class:
            stripped = line.lstrip()
            if stripped and not stripped.startswith("#"):
                current_indent = len(line) - len(stripped)
                # If we hit a class definition at same or less indent, we've left API class
                if current_indent <= api_class_indent and re.match(
                    r"^class\s+\w+", stripped
                ):
                    break

        if in_api_class:
            # Look for method definitions (4 spaces indent for class methods)
            match = re.match(r"^\s{4}def\s+([a-z_][a-z0-9_]*)\s*\(", line)
            if match:
                method_name = match.group(1)
                # Include all methods (including __init__), skip truly private ones
                if not method_name.startswith("_") or method_name == "__init__":
                    methods.append(method_name)

    return methods


def group_methods(methods):
    """Group methods by their prefix (e.g., buy_browse, sell_inventory)."""
    groups = {}
    for method in methods:
        if method == "__init__":
            groups["__init__"] = [method]
            continue

        # Extract prefix (first two parts: buy_browse, sell_inventory, etc.)
        parts = method.split("_")
        if len(parts) >= 2:
            prefix = "_".join(parts[:2])
        else:
            prefix = parts[0]

        if prefix not in groups:
            groups[prefix] = []
        groups[prefix].append(method)

    return groups


def generate_rst_files(docs_dir, method_groups, project_root=None):
    """Generate RST files for the documentation from templates."""
    if project_root is None:
        project_root = docs_dir.parent
    source_dir = docs_dir / "source"
    api_dir = source_dir / "api"
    api_dir.mkdir(parents=True, exist_ok=True)

    # Read templates
    api_template_path = docs_dir / "api.rst.template"
    group_template_path = docs_dir / "api_group.rst.template"
    index_rst_path = docs_dir / "index.rst"

    if not api_template_path.exists():
        raise FileNotFoundError(f"Template not found: {api_template_path}")
    if not group_template_path.exists():
        raise FileNotFoundError(f"Template not found: {group_template_path}")
    if not index_rst_path.exists():
        raise FileNotFoundError(f"Template not found: {index_rst_path}")

    with open(api_template_path, "r", encoding="utf-8") as f:
        api_template = f.read()
    with open(group_template_path, "r", encoding="utf-8") as f:
        group_template = f.read()
    with open(index_rst_path, "r", encoding="utf-8") as f:
        index_content = f.read()

    # Generate API group entries for main API index
    api_groups = []

    # Generate RST files for each method group
    for prefix, methods in sorted(method_groups.items()):
        if prefix == "__init__":
            continue

        # Add to main API index
        api_groups.append(f"   api/{prefix}")

        # Create group RST file
        group_title = " ".join(word.capitalize() for word in prefix.split("_"))
        group_title_underline = "=" * len(group_title)

        # Generate method entries
        method_entries = "\n".join(
            f".. automethod:: ebay_rest.API.{method}\n" for method in sorted(methods)
        )

        group_rst_content = group_template.format(
            group_title=group_title,
            group_title_underline=group_title_underline,
            methods=method_entries,
        )

        group_file = api_dir / f"{prefix}.rst"
        with open(group_file, "w", encoding="utf-8") as f:
            f.write(group_rst_content)
        print(f"✓ Generated {group_file}")

    # Write main API index
    api_rst_content = api_template.format(api_groups="\n".join(api_groups))
    api_rst_file = source_dir / "api.rst"
    with open(api_rst_file, "w", encoding="utf-8") as f:
        f.write(api_rst_content)
    print(f"✓ Generated {api_rst_file}")

    # Copy README.md to source directory
    readme_path = project_root / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

        readme_md_dest = source_dir / "readme.md"
        with open(readme_md_dest, "w", encoding="utf-8") as f:
            f.write(readme_content)
        print(f"✓ Copied README.md to {readme_md_dest}")
    else:
        print(f"⚠ Warning: README.md not found at {readme_path}")

    # Copy main index (static file, not a template)
    index_file = source_dir / "index.rst"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_content)
    print(f"✓ Generated {index_file}")


def create_directories(docs_dir):
    """Create necessary directories."""
    (docs_dir / "source" / "api").mkdir(parents=True, exist_ok=True)
    print("✓ Created directory structure")


def build_documentation(docs_dir):
    """Build the HTML documentation using Sphinx."""
    build_dir = docs_dir / "build"
    source_dir = docs_dir / "source"
    doctree_dir = docs_dir / "build" / ".doctrees"

    print("\nBuilding documentation...")
    try:
        with docutils_namespace():
            app = Sphinx(
                srcdir=str(source_dir),
                confdir=str(source_dir),
                outdir=str(build_dir),
                doctreedir=str(doctree_dir),
                buildername="html",
                confoverrides={},
                status=None,  # Use default status output
                warning=None,  # Use default warning output
                freshenv=False,
                warningiserror=False,
                tags=None,
                verbosity=1,
                parallel=0,  # 0 = auto-detect
            )
            app.build()

        print("✓ Documentation built successfully!")
        print(f"✓ Output available at: {build_dir / 'index.html'}")
        return True
    except Exception as e:
        print(f"✗ Error building documentation:")
        print(f"  {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False


def generate_documentation_source(docs_dir=None, project_root=None):
    """
    Generate documentation source files (RST and conf.py) without building.
    """
    if project_root is None:
        project_root = get_project_root()
    if docs_dir is None:
        docs_dir = project_root / "docs"

    docs_dir.mkdir(exist_ok=True)

    # Get API file path from repo
    api_path = get_api_file_path(project_root)
    print(f"✓ Found API file: {api_path}")

    # Extract methods
    print("\nExtracting methods from API class...")
    methods = extract_methods(api_path)
    print(f"✓ Found {len(methods)} methods")

    # Group methods
    method_groups = group_methods(methods)
    print(f"✓ Grouped into {len(method_groups)} categories")

    # Create directories
    print("\nCreating directory structure...")
    create_directories(docs_dir)

    # Generate configuration
    print("\nGenerating Sphinx configuration...")
    create_conf_py(docs_dir, project_root)

    # Generate RST files
    print("\nGenerating RST files...")
    generate_rst_files(docs_dir, method_groups, project_root)

    print("\n✓ Documentation source files generated successfully!")
    return True


def main():
    """Main function to build documentation."""
    print("Building ebay_rest documentation...\n")

    project_root = get_project_root()
    docs_dir = project_root / "docs"

    # Generate source files
    if not generate_documentation_source(docs_dir, project_root):
        sys.exit(1)

    # Build documentation
    print("\n" + "=" * 50)
    success = build_documentation(docs_dir)

    if success:
        print("\n" + "=" * 50)
        print("\nDocumentation build complete!")
    else:
        print("\nDocumentation build failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
