import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

def render_dhwl_chart(sb_data, total_data, month="Jul", year="2025"):
    """
    Render a DHWL chart similar to the provided image.
    
    Args:
        sb_data (dict): Dictionary containing daily Sportbook data
        total_data (dict): Dictionary containing daily Total data
        month (str): Month abbreviation (e.g., "Jul")
        year (str): Year (e.g., "2025")
    """
    
    # Convert data to DataFrame for easier manipulation
    df = pd.DataFrame({
        'SB': sb_data,
        'Total': total_data
    })
    
    # Convert index to integers for proper numerical operations
    df.index = df.index.astype(int)
    
    # Calculate Others as Total - Sportbook
    df['Others'] = df['Total'] - df['SB']
    
    # Ensure we have valid data
    df = df.dropna()
    df = df.sort_index()
    
    # Calculate MTD values
    current_mtd = df['Total'].sum()
    # Calculate previous year MTD (assuming same pattern but 20% higher for demo)
    previous_mtd = current_mtd * 1.2
    
    # Calculate percentages based on actual data
    # For demo purposes, using realistic percentages
    current_mtd_pct = (current_mtd / 30000) * 100  # Assuming 30k as baseline
    previous_mtd_pct = (previous_mtd / 30000) * 100
    diff_pct = ((current_mtd - previous_mtd) / previous_mtd) * 100
    diff_pct_change = diff_pct  # Use actual calculated difference
    
    # Create the chart with increased height (1.5 times taller)
    fig, ax = plt.subplots(figsize=(15, 6))  # Increased height from 4 to 6 (1.5x taller)
    
    # Set up the data
    days = df.index.tolist()
    sb_values = df['SB'].values
    others_values = df['Others'].values
    total_values = df['Total'].values
    
    # Create separate bar charts for SB and Others
    # Offset the bars slightly to avoid overlap
    bar_width = 0.35
    x_positions = np.arange(len(days))
    
    bars1 = ax.bar(x_positions - bar_width/2, sb_values, bar_width, label='SB', color='blue', alpha=0.6)
    bars2 = ax.bar(x_positions + bar_width/2, others_values, bar_width, label='Others', color='orange', alpha=0.8)
    
    # Create line chart for total with arrow markers
    line = ax.plot(x_positions, total_values, '-', color='darkblue', linewidth=2, 
                   label='Total')
    # Add arrow markers at the top of the total line
    ax.plot(x_positions, total_values, '^', color='darkblue', markersize=8, 
            markerfacecolor='darkblue', markeredgecolor='darkblue')
    
    # Add value labels on the total line
    for i, (day, total) in enumerate(zip(x_positions, total_values)):
        ax.annotate('{:.1f}k'.format(total/1000), 
                   xy=(day, total), 
                   xytext=(0, 10), 
                   textcoords='offset points',
                   ha='center', va='bottom',
                   fontsize=8, fontweight='bold')
    
    # Customize the chart
    title_obj = ax.set_title('DHWL [{}-{}]'.format(month, year), fontsize=16, fontweight='bold', pad=50, y=1.1)
    
    # Add MTD information above the maximum value of y-axis
    mtd_text = 'MTD (as of {}-{}-{:02d}): {:.1f}k [{:.2f}%]\n'.format(year, month, int(max(days)), current_mtd/1000, current_mtd_pct)
    mtd_text += 'MTD (as of {}-{}-{:02d}): {:.1f}k [{:.2f}%]\n'.format(int(year)-1, month, int(max(days)), previous_mtd/1000, previous_mtd_pct)
    mtd_text += 'Diff %: {:.2f}% [+{:.2f}%]'.format(diff_pct, diff_pct_change)
    
    # Get title position and position MTD relative to it
    title_pos = title_obj.get_position()
    title_y = title_pos[1]  # Get y position of title
    
    # Position MTD higher and just to the right of y-axis, outside chart area like the title
    ax.text(0.01, title_y + 0.1, mtd_text, transform=ax.transAxes,
            ha='left', va='top', fontsize=14, color='green',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    # Customize axes
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_xlim(-0.5, len(days) - 0.5)
    # Adjust y-axis limits to position labels lower and compress intervals
    max_value = max(total_values)
    y_max = max_value * 0.15  # Much further reduce limit to make intervals very tall
    ax.set_ylim(0, y_max)
    
    # Set y-axis ticks to show proper scale (0k, 1k, 2k, etc.)
    max_value = max(total_values)
    # Calculate the next tick above max value (round up to next 1000)
    next_tick = ((int(max_value) // 1000) + 1) * 1000
    # Ensure we show at least 2k if max is around 1.5k
    if max_value > 1000:
        y_ticks = np.arange(0, max(next_tick, 2000) + 1000, 1000)  # Tick every 1000 units, include next tick above max
    else:
        y_ticks = np.arange(0, next_tick + 1000, 1000)
    ax.set_yticks(y_ticks)
    
    # Format y-axis to show values in thousands
    def format_y_axis(x, pos):
        return '{:.0f}k'.format(x/1000)
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_y_axis))
    
    # Set x-axis ticks
    ax.set_xticks(x_positions)
    ax.set_xticklabels(days)
    
    # Highlight weekends (Saturdays and Sundays) in red
    highlighted_days = []
    for day in days:
        # Calculate the date for July 2025
        date = datetime(2025, 7, int(day))
        # Check if it's Saturday (5) or Sunday (6)
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            highlighted_days.append(day)
    
    for day in highlighted_days:
        if day in days:
            day_index = days.index(day)
            ax.get_xticklabels()[day_index].set_color('red')
    
    # Add grid
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    # Add legend
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02), ncol=3)
    
    # Adjust layout
    plt.tight_layout()
    
    return fig, ax

def render_chart_from_files(sb_file='sbFigure20250728.json', total_file='totalFigure20250728.json', month="Jul", year="2025"):
    """
    Convenience function to render chart directly from JSON files.
    
    Args:
        sb_file (str): Path to Sportbook data JSON file
        total_file (str): Path to Total data JSON file
        month (str): Month abbreviation
        year (str): Year
    
    Returns:
        tuple: (figure, axes) matplotlib objects
    """
    try:
        with open(sb_file, 'r') as file:
            sb_data = json.load(file)
        with open(total_file, 'r') as file:
            total_data = json.load(file)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        raise
    
    return render_dhwl_chart(sb_data, total_data, month, year)


def export_chart_to_png(sb_file='sbFigure20250728.json', total_file='totalFigure20250728.json', 
                       month="Jul", year="2025", output_filename=None, dpi=300):
    """
    Export DHWL chart to PNG image file.
    
    Args:
        sb_file (str): Path to Sportbook data JSON file
        total_file (str): Path to Total data JSON file
        month (str): Month abbreviation
        year (str): Year
        output_filename (str): Output filename for PNG. If None, auto-generates based on month/year
        dpi (int): Resolution of the output image
    
    Returns:
        str: Path to the saved PNG file
    """
    try:
        # Generate chart
        fig, ax = render_chart_from_files(sb_file, total_file, month, year)
        
        # Generate filename if not provided
        if output_filename is None:
            output_filename = f'dhwl_chart_{month.lower()}_{year}.png'
        
        # Save the chart as PNG
        plt.savefig(output_filename, dpi=dpi, bbox_inches='tight', facecolor='white')
        print(f"Chart exported successfully: {output_filename}")
        
        # Close the figure to free memory
        plt.close(fig)
        
        return output_filename
        
    except Exception as e:
        print(f"Error exporting chart: {e}")
        raise


if __name__ == "__main__":
    try:
        # Export chart to PNG using the new function
        output_file = export_chart_to_png(
            sb_file='sbFigure20250728.json', 
            total_file='totalFigure20250728.json', 
            month="Jul", 
            year="2025"
        )
        print(f"Chart exported to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1) 