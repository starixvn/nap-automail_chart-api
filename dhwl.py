import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import io
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Union
from datetime import datetime
import math

# Constants
SCALE = 1000

# Pydantic model for DHWL chart request
class DHWLChartRequest(BaseModel):
    sb_data: Dict[str, float] = Field(..., alias="SbData")
    total_data: Dict[str, float] = Field(..., alias="TotalData")
    mtd: float = Field(..., alias="Mtd")
    previous_mtd: float = Field(..., alias="PreviousMtd")
    diff_mtd: str = Field(..., alias="DiffMtd")
    margin: float = Field(..., alias="Margin")
    previous_margin: float = Field(..., alias="PreviousMargin")
    diff_margin: str = Field(..., alias="DiffMargin")
    title: str = Field(..., alias="Title")
    mtd_date: str = Field(..., alias="MtdDate")
    previous_mtd_date: str = Field(..., alias="PreviousMtdDate")

    model_config = ConfigDict(populate_by_name=True)

def render_dhwl_chart(request: DHWLChartRequest):
    """
    Render a DHWL chart similar to the provided image.
        
    """
    sb_data = request.sb_data
    total_data = request.total_data
    
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
    
    # Calculate percentages based on actual data    
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
    if len(days) == 1:
        bar_width = 0.2
    elif len(days) == 2:
        bar_width = 0.28
    elif len(days) == 3:
        bar_width = 0.31
    elif len(days) == 4:
        bar_width = 0.34
    
    x_positions = np.arange(len(days))
    
    bars1 = ax.bar(x_positions - bar_width/2, sb_values, bar_width, label='SB', color=(133/255, 184/255, 253/255), alpha=1)
    bars2 = ax.bar(x_positions + bar_width/2, others_values, bar_width, label='Others', color=(251/255, 180/255, 64/255), alpha=1)
    
    # Create line chart for total with arrow markers
    truncate_total_values = [truncate(total/SCALE, 1)*SCALE for total in total_values]
    line = ax.plot(x_positions, truncate_total_values, '-', color=(0/255, 69/255, 134/255), linewidth=2, 
                   label='Total')
    # Add arrow markers at the top of the total line
    ax.plot(x_positions, truncate_total_values, '^', color=(0/255, 69/255, 134/255), markersize=8, 
            markerfacecolor=(0/255, 69/255, 134/255), markeredgecolor=(0/255, 69/255, 134/255))
        
    # Add value labels on the total line
    
    for i, (day, total) in enumerate(zip(x_positions, truncate_total_values)):
        ax.annotate('{:.1f}k'.format(total/SCALE), 
                   xy=(day, total), 
                   xytext=(0, 10), 
                   textcoords='offset points',
                   ha='center', va='bottom',
                   fontsize=14, fontweight='normal', fontfamily='Tahoma')
    
    # Customize the chart
    title_obj = ax.set_title(request.title, fontsize=19, fontweight='bold', fontfamily='Tahoma', pad=50, y=1.1)
    
    # Add MTD information above the maximum value of y-axis
    
    mtd_text = 'MTD (as of {}): {:.1f}k [{:.2f}%]\n'.format(request.mtd_date, request.mtd / SCALE, request.margin)
    mtd_text += 'MTD (as of {}): {:.1f}k [{:.2f}%]\n'.format(request.previous_mtd_date, request.previous_mtd / SCALE, request.previous_margin)
    mtd_text += 'Diff %: {} [{}]'.format(request.diff_mtd, request.diff_margin)
    
    # Get title position and position MTD relative to it
    title_pos = title_obj.get_position()
    title_y = title_pos[1]  # Get y position of title
    
    # Position MTD higher and just to the right of y-axis, outside chart area like the title
    mtd_text_x = 0.01

    ax.text(mtd_text_x, 1.17, mtd_text, transform=ax.transAxes,
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
    next_tick = ((int(max_value) // SCALE) + 1) * SCALE
    # Ensure we show at least 2k if max is around 1.5k
    if max_value > SCALE:        
        decimal_part = max_value % SCALE
        more_tick = 2 if decimal_part > 500 else 1
        y_ticks = np.arange(0, max(next_tick, 2 * SCALE) + more_tick * SCALE, SCALE)  # Tick every 1000 units, include next tick above max
    else:
        y_ticks = np.arange(0, next_tick + 2 * SCALE, SCALE)
    ax.set_yticks(y_ticks)
        
    # Format y-axis to show values in thousands
    def format_y_axis(x, pos):
        return '{:.0f}k'.format(x/SCALE)
    
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
    ax.legend(handles_ordered, labels_ordered, loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=3, frameon=False)
    
    # Adjust layout
    plt.tight_layout()
    
    # Calculate DPI to ensure image height is always 900 pixels
    target_height = 915
    current_height_inches = fig.get_figheight()
    dpi_for_target_height = target_height / current_height_inches
    
    # Save the figure to a bytes buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', dpi=dpi_for_target_height, bbox_inches='tight')
    buffer.seek(0)
    
    # Get the byte content
    image_bytes = buffer.getvalue()
    
    # Close the figure to free memory
    plt.close(fig)
    
    return image_bytes


def safe_render_dhwl_chart(request: DHWLChartRequest):
    """
    Safely render a DHWL chart with proper error handling and cleanup.
    
    Returns:
        bytes: Image bytes if successful, None if failed
    """
    try:
        return render_dhwl_chart(request)
    except Exception as e:
        print(f"Error rendering DHWL chart: {e}")
        return None
    finally:
        # Ensure all matplotlib figures are closed
        plt.close('all')

def truncate(value, precision):
    """
    Truncates a floating-point number to a specified number of decimal places.
    """
    step = math.pow(10, precision)
    tmp = math.trunc(step * value)
    return tmp / step