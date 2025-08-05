import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import io
from pydantic import BaseModel
from typing import Dict, Union

# Pydantic model for DHWL chart request
class DHWLChartRequest(BaseModel):
    sb_data: Dict[str, float]
    total_data: Dict[str, float]
    month: str = "Jul"
    year: Union[str, int] = "2025"

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
    
    # Calculate chart size based on number of figures
    numberOfFigure = len(df)
    height = 900
    if numberOfFigure <= 9:
        width = 650
    else:
        width = (numberOfFigure * 1920 / 31) + 50
    
    # Create the chart with calculated dimensions
    fig, ax = plt.subplots(figsize=(width/100, height/100))  # Convert pixels to inches (assuming 100 DPI for calculation)
    
    # Set up the data
    days = df.index.tolist()
    sb_values = df['SB'].values
    others_values = df['Others'].values
    total_values = df['Total'].values
    
    # Create separate bar charts for SB and Others
    # Offset the bars slightly to avoid overlap
    bar_width = 0.35
    x_positions = np.arange(len(days))
    
    bars1 = ax.bar(x_positions - bar_width/2, sb_values, bar_width, label='SB', color=(133/255, 184/255, 253/255), alpha=1)
    bars2 = ax.bar(x_positions + bar_width/2, others_values, bar_width, label='Others', color=(251/255, 180/255, 64/255), alpha=1)
    
    # Add value labels on the SB bars
    for i, (day, sb_value) in enumerate(zip(x_positions, sb_values)):
        if sb_value > 0:  # Only show label if value is greater than 0
            ax.annotate('{:.1f}k'.format(sb_value/1000), 
                       xy=(day - bar_width/2, sb_value), 
                       xytext=(0, 5), 
                       textcoords='offset points',
                       ha='center', va='bottom',
                       fontsize=14, fontweight='normal', fontfamily='Tahoma')
    
    # Add value labels on the Others bars
    for i, (day, others_value) in enumerate(zip(x_positions, others_values)):
        if others_value > 0:  # Only show label if value is greater than 0
            ax.annotate('{:.1f}k'.format(others_value/1000), 
                       xy=(day + bar_width/2, others_value), 
                       xytext=(0, 5), 
                       textcoords='offset points',
                       ha='center', va='bottom',
                       fontsize=14, fontweight='normal', fontfamily='Tahoma')
    
    # Create line chart for total with arrow markers
    line = ax.plot(x_positions, total_values, '-', color=(0/255, 69/255, 134/255), linewidth=2, 
                   label='Total')
    # Add arrow markers at the top of the total line
    ax.plot(x_positions, total_values, '^', color=(0/255, 69/255, 134/255), markersize=8, 
            markerfacecolor=(0/255, 69/255, 134/255), markeredgecolor=(0/255, 69/255, 134/255))
    
    # Add value labels on the total line
    for i, (day, total) in enumerate(zip(x_positions, total_values)):
        ax.annotate('{:.1f}k'.format(total/1000), 
                   xy=(day, total), 
                   xytext=(0, 10), 
                   textcoords='offset points',
                   ha='center', va='bottom',
                   fontsize=14, fontweight='normal', fontfamily='Tahoma')
    
    # Customize the chart
    title_obj = ax.set_title('DHWL [{}-{}]'.format(month, year), fontsize=19, fontweight='bold', fontfamily='Tahoma', pad=50, y=1.1)
    
    # Add MTD information above the maximum value of y-axis
    mtd_text = 'MTD (as of {}-{}-{:02d}): {:.1f}k [{:.2f}%]\n'.format(year, month, int(max(days)), current_mtd/1000, current_mtd_pct)
    mtd_text += 'MTD (as of {}-{}-{:02d}): {:.1f}k [{:.2f}%]\n'.format(int(year)-1, month, int(max(days)), previous_mtd/1000, previous_mtd_pct)
    mtd_text += 'Diff %: {:.2f}% [+{:.2f}%]'.format(diff_pct, diff_pct_change)
    
    # Get title position and position MTD relative to it
    title_pos = title_obj.get_position()
    title_y = title_pos[1]  # Get y position of title
    
    # Position MTD higher and just to the right of y-axis, outside chart area like the title
    ax.text(0.01, 1.17, mtd_text, transform=ax.transAxes,
            ha='left', va='top', fontsize=19, fontweight='bold', fontfamily='Tahoma', color=(44/255, 185/255, 91/255))
    
    # Adjust the chart position to be 50 pixels below MTD text
    # Convert 50 pixels to figure coordinates (assuming 300 DPI)
    pixel_to_fig = 50 / (fig.get_dpi() * fig.get_figheight())
    ax.set_position([ax.get_position().x0, 
                    ax.get_position().y0 - pixel_to_fig, 
                    ax.get_position().width, 
                    ax.get_position().height])
    
    # Customize axes
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('', fontsize=12)
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
        y_ticks = np.arange(0, max(next_tick, 2000) + 2000, 1000)  # Tick every 1000 units, include next tick above max
    else:
        y_ticks = np.arange(0, next_tick + 2000, 1000)
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
    ax.grid(True, alpha=1)
    ax.set_axisbelow(True)
    
    # Add legend with custom order: SB, Others, Total
    handles, labels = ax.get_legend_handles_labels()
    # Reorder the handles and labels to match desired order: SB, Others, Total
    order = ['SB', 'Others', 'Total']
    handles_ordered = []
    labels_ordered = []
    for label in order:
        if label in labels:
            idx = labels.index(label)
            handles_ordered.append(handles[idx])
            labels_ordered.append(labels[idx])
    ax.legend(handles_ordered, labels_ordered, loc='upper center', bbox_to_anchor=(0.5, 1.02), ncol=3)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure to a bytes buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    
    # Get the byte content
    image_bytes = buffer.getvalue()
    
    # Close the figure to free memory
    plt.close(fig)
    
    return image_bytes