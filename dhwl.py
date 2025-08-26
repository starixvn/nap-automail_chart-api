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

def prepare_data(request: DHWLChartRequest) -> pd.DataFrame:
    """
    Prepare and process the data for chart rendering.
    
    Args:
        request: DHWLChartRequest object containing the data
        
    Returns:
        pd.DataFrame: Processed data with SB, Total, and Others columns
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
    
    return df

def calculate_chart_dimensions(df: pd.DataFrame) -> tuple[int, int]:
    """
    Calculate chart dimensions based on the number of data points.
    
    Args:
        df: DataFrame containing the chart data
        
    Returns:
        tuple: (width, height) in pixels
    """
    numberOfFigure = len(df)
    height = 900    
    if numberOfFigure <= 9:
        width = 650
    else:
        width = (numberOfFigure * 1920 / 31) + 50
    
    return width, height

def calculate_bar_width(days_count: int) -> float:
    """
    Calculate appropriate bar width based on number of days.
    
    Args:
        days_count: Number of days in the data
        
    Returns:
        float: Bar width value
    """
    if days_count == 1:
        return 0.2
    elif days_count == 2:
        return 0.28
    elif days_count == 3:
        return 0.31
    elif days_count == 4:
        return 0.34
    else:
        return 0.35

def create_bars_and_line(ax, df: pd.DataFrame, x_positions: np.ndarray, bar_width: float):
    """
    Create the bars and line chart elements.
    
    Args:
        ax: Matplotlib axes object
        df: DataFrame containing the chart data
        x_positions: Array of x positions for bars
        bar_width: Width of the bars
    """
    sb_values = df['SB'].values
    others_values = df['Others'].values
    total_values = df['Total'].values
    
    # Create bars for SB and Others
    bars1 = ax.bar(x_positions - bar_width/2, sb_values, bar_width, label='SB', color=(133/255, 184/255, 253/255), alpha=1)
    bars2 = ax.bar(x_positions + bar_width/2, others_values, bar_width, label='Others', color=(251/255, 180/255, 64/255), alpha=1)
    
    # Create line chart for total with arrow markers
    truncate_total_values = [truncate(total/SCALE, 1)*SCALE for total in total_values]
    line = ax.plot(x_positions, truncate_total_values, '-', color=(0/255, 69/255, 134/255), linewidth=2, label='Total')
    
    # Add arrow markers at the top of the total line
    ax.plot(x_positions, truncate_total_values, '^', color=(0/255, 69/255, 134/255), markersize=8, 
            markerfacecolor=(0/255, 69/255, 134/255), markeredgecolor=(0/255, 69/255, 134/255))
    
    return truncate_total_values

def add_value_labels(ax, x_positions: np.ndarray, truncate_total_values: list):
    """
    Add value labels on the total line.
    
    Args:
        ax: Matplotlib axes object
        x_positions: Array of x positions
        truncate_total_values: List of truncated total values
    """
    for i, (day, total) in enumerate(zip(x_positions, truncate_total_values)):
        ax.annotate('{:.1f}k'.format(total/SCALE), 
                   xy=(day, total), 
                   xytext=(0, 10), 
                   textcoords='offset points',
                   ha='center', va='bottom',
                   fontsize=14, fontweight='normal', fontfamily='Tahoma')

def add_title_and_mtd_info(ax, request: DHWLChartRequest, fig):
    """
    Add title and MTD information to the chart.
    
    Args:
        ax: Matplotlib axes object
        request: DHWLChartRequest object
        fig: Matplotlib figure object
    """
    # Add title
    title_obj = ax.set_title(request.title, fontsize=19, fontweight='bold', fontfamily='Tahoma', pad=50, y=1.1)
    
    # Add MTD information
    mtd_text = 'MTD (as of {}): {:.1f}k [{:.2f}%]\n'.format(request.mtd_date, request.mtd / SCALE, request.margin)
    mtd_text += 'MTD (as of {}): {:.1f}k [{:.2f}%]\n'.format(request.previous_mtd_date, request.previous_mtd / SCALE, request.previous_margin)
    mtd_text += 'Diff %: {} [{}]'.format(request.diff_mtd, request.diff_margin)
    
    # Position MTD text
    mtd_text_x = 0.01
    ax.text(mtd_text_x, 1.17, mtd_text, transform=ax.transAxes,
            ha='left', va='top', fontsize=19, fontweight='bold', fontfamily='Tahoma', color=(44/255, 185/255, 91/255))
    
    # Adjust chart position
    pixel_to_fig = 50 / (fig.get_dpi() * fig.get_figheight())
    ax.set_position([ax.get_position().x0, 
                    ax.get_position().y0 - pixel_to_fig, 
                    ax.get_position().width, 
                    ax.get_position().height])

def configure_axes(ax, days: list, total_values: list):
    """
    Configure axes properties including labels, limits, and ticks.
    
    Args:
        ax: Matplotlib axes object
        days: List of day values
        total_values: List of total values
    """
    # Set labels
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('', fontsize=12)
    
    # Set x-axis limits and ticks
    ax.set_xlim(-0.5, len(days) - 0.5)
    ax.set_xticks(range(len(days)))
    ax.set_xticklabels(days)
    
    # Set y-axis limits and ticks
    max_value = max(total_values) if total_values.size > 0 else 0
    min_value = min(total_values) if total_values.size > 0 else 0

    y_upper = max_value * 1.15 if max_value >= 0 else max_value * 0.85
    y_lower = min_value * 1.15 if min_value < 0 else 0
    
    if y_upper == 0 and y_lower == 0 and total_values.size > 0:
        y_upper = max(total_values) * 1.15 if max(total_values) > 0 else 1

    ax.set_ylim(y_lower, y_upper)

    # Calculate y-axis ticks
    start_tick = math.floor(y_lower / SCALE) * SCALE
    
    next_tick = ((int(max_value) // SCALE) + 1) * SCALE
    if max_value > SCALE:
        decimal_part = max_value % SCALE
        more_tick = 2 if decimal_part > 500 else 1
        end_tick = max(next_tick, 2 * SCALE) + more_tick * SCALE
    else:
        end_tick = next_tick + 2 * SCALE

    end_tick = max(end_tick, y_upper)
    y_ticks = np.arange(start_tick, end_tick, SCALE)
    ax.set_yticks(y_ticks)
    
    # Format y-axis to show values in thousands
    def format_y_axis(x, pos):
        return '{:.0f}k'.format(x/SCALE)
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_y_axis))

def highlight_weekends(ax, days: list, mtd_date_str: str):
    """
    Highlight weekend days in red on the x-axis.
    
    Args:
        ax: Matplotlib axes object
        days: List of day values
        mtd_date_str: MTD date string
    """
    mtd_date = datetime.strptime(mtd_date_str, '%Y-%m-%d')    
    highlighted_days = []
    for day in days:
        # Calculate the date for the month
        date = datetime(mtd_date.year, mtd_date.month, int(day))        
        # Check if it's Saturday (5) or Sunday (6)
        if date.weekday() >= 5:
            highlighted_days.append(day)
    
    for day in highlighted_days:
        if day in days:
            day_index = days.index(day)
            ax.get_xticklabels()[day_index].set_color('red')

def add_grid_and_legend(ax):
    """
    Add grid and legend to the chart.
    
    Args:
        ax: Matplotlib axes object
    """
    # Add grid
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    # Add legend with custom order: SB, Others, Total
    handles, labels = ax.get_legend_handles_labels()
    order = ['SB', 'Others', 'Total']
    handles_ordered = []
    labels_ordered = []
    for label in order:
        if label in labels:
            idx = labels.index(label)
            handles_ordered.append(handles[idx])
            labels_ordered.append(labels[idx])
    ax.legend(handles_ordered, labels_ordered, loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=3, frameon=False)

def save_chart_to_bytes(fig) -> bytes:
    """
    Save the chart to bytes buffer.
    
    Args:
        fig: Matplotlib figure object
        
    Returns:
        bytes: Image bytes
    """
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

def render_dhwl_chart(request: DHWLChartRequest):
    """
    Render a DHWL chart similar to the provided image.
    """
    # Prepare data
    df = prepare_data(request)
    
    # Calculate dimensions
    width, height = calculate_chart_dimensions(df)
    
    # Create the chart with calculated dimensions
    fig, ax = plt.subplots(figsize=(width/100, height/100))
    
    # Set up the data
    days = df.index.tolist()
    total_values = df['Total'].values
    
    # Calculate bar width
    bar_width = calculate_bar_width(len(days))
    x_positions = np.arange(len(days))
    
    # Create bars and line
    truncate_total_values = create_bars_and_line(ax, df, x_positions, bar_width)
    
    # Add value labels
    add_value_labels(ax, x_positions, truncate_total_values)
    
    # Add title and MTD info
    add_title_and_mtd_info(ax, request, fig)
    
    # Configure axes
    configure_axes(ax, days, total_values)
    
    # Highlight weekends
    highlight_weekends(ax, days, request.mtd_date)
    
    # Add grid and legend
    add_grid_and_legend(ax)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save and return
    return save_chart_to_bytes(fig)


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