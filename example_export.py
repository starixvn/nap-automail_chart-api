#!/usr/bin/env python3
"""
Example script demonstrating how to use the export_chart_to_png function.
"""

from chart_renderer import export_chart_to_png

def main():
    """Demonstrate different ways to export charts to PNG."""
    
    print("=== DHWL Chart Export Examples ===\n")
    
    # Example 1: Basic export with default settings
    print("1. Exporting with default settings...")
    output_file = export_chart_to_png()
    print(f"   Result: {output_file}\n")
    
    # Example 2: Custom filename and DPI
    print("2. Exporting with custom filename and high DPI...")
    output_file = export_chart_to_png(
        output_filename="my_custom_chart.png",
        dpi=600
    )
    print(f"   Result: {output_file}\n")
    
    # Example 3: Different month and year
    print("3. Exporting for different month/year...")
    output_file = export_chart_to_png(
        month="Aug",
        year="2025",
        output_filename="august_2025_chart.png"
    )
    print(f"   Result: {output_file}\n")
    
    # Example 4: Using different data files (if they exist)
    print("4. Exporting with different data files...")
    try:
        output_file = export_chart_to_png(
            sb_file="sbFigure20250728.json",
            total_file="totalFigure20250728.json",
            output_filename="july_2025_final.png"
        )
        print(f"   Result: {output_file}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
    
    print("=== Export Examples Complete ===")

if __name__ == "__main__":
    main() 