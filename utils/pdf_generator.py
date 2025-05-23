import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from fpdf import FPDF
from io import BytesIO
import matplotlib as mpl
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
import tempfile
import requests
import io

# Set style for all plots
plt.style.use('ggplot')
sns.set_palette("viridis")
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.sans-serif'] = ['Verdana', 'Arial', 'Helvetica', 'DejaVu Sans']
mpl.rcParams['axes.labelsize'] = 10
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['xtick.labelsize'] = 8
mpl.rcParams['ytick.labelsize'] = 8

# Get the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Colors - Professional Soccer Theme
PRIMARY_COLOR = "#1E8449"  # Forest Green
SECONDARY_COLOR = "#1A365D"  # Deep Navy
ACCENT_COLOR = "#FFD700"  # Gold
BACKGROUND_COLOR = "#F5F9F6"
TEXT_COLOR = "#333333"
GRID_COLOR = "#DDDDDD"
HIGHLIGHT_COLOR = "#E74C3C"  # Red accent
SUCCESS_COLOR = "#2ECC71"  # Bright green
WARNING_COLOR = "#F39C12"  # Amber

# Create a custom radar chart projection
def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes."""
    
    # Calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
    
    class RadarAxes(PolarAxes):
        name = 'radar'
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')
            
        def fill(self, *args, **kwargs):
            """Override fill to handle closed polygon"""
            return super().fill(*args, closed=True, **kwargs)
            
        def plot(self, *args, **kwargs):
            """Override plot to handle closed polygon"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)
            return lines
            
        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)
                
        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)
            
        def _gen_axes_patch(self):
            return plt.Circle((0.5, 0.5), 0.5)
            
    register_projection(RadarAxes)
    return theta


def create_radar_chart(stats, attributes):
    """Creates a radar chart for player attributes"""
    # Number of variables
    N = len(attributes)
    
    # Create the radar factory
    theta = radar_factory(N)
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='radar'))
    
    # Draw one axis per variable and add labels
    plt.xticks(theta, attributes, size=12, color=TEXT_COLOR, fontweight='bold')
    
    # Draw the outline of the chart
    ax.set_ylim(0, 100)
    
    # Plot the player stats
    ax.plot(theta, stats, 'o-', linewidth=3, color=PRIMARY_COLOR, alpha=0.9)
    ax.fill(theta, stats, color=PRIMARY_COLOR, alpha=0.3)
    
    # Add background grid with semi-transparent concentric circles
    ax.set_rgrids([20, 40, 60, 80], angle=0, color=GRID_COLOR, alpha=0.5)
    
    # Add values to the plot
    for i, (angle, stat) in enumerate(zip(theta, stats)):
        ax.text(angle, stat + 10, str(stat), 
                horizontalalignment='center', 
                verticalalignment='center',
                fontsize=11, 
                fontweight='bold',
                color=SECONDARY_COLOR)
    
    # Remove the radial labels
    ax.set_yticklabels([])
    
    # Add a title
    plt.title('Player Skills Assessment', size=16, color=SECONDARY_COLOR, fontweight='bold', y=1.05)
    
    # Set the background color
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Add a grey polygon for the background grid
    background = np.ones(N) * 100
    ax.plot(theta, background, color=GRID_COLOR, linewidth=1, linestyle='--', alpha=0.3)
    ax.fill(theta, background, color=GRID_COLOR, alpha=0.05)
    
    # Add benchmark comparison data
    benchmark = np.array([70, 65, 75, 68, 72, 78])  # Example league average
    ax.plot(theta, benchmark, 'o--', linewidth=2, color=ACCENT_COLOR, alpha=0.7, label='League Average')
    ax.fill(theta, benchmark, color=ACCENT_COLOR, alpha=0.1)
    
    # Add legend
    ax.legend(loc='upper right', frameon=True, framealpha=0.9)
    
    plt.tight_layout()
    
    return fig


def create_soccer_field_position_image(position):
    """Create an image of a soccer field with the player's position highlighted"""
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Draw soccer field
    # Field dimensions (in yards)
    field_length = 120
    field_width = 80
    
    # Field background (grass color) with texture
    rect = plt.Rectangle((0, 0), field_length, field_width, 
                          color='#1A8022', alpha=1.0)
    ax.add_patch(rect)
    
    # Add field texture (stripes)
    num_stripes = 20
    stripe_width = field_width / num_stripes
    
    for i in range(0, num_stripes, 2):
        y_pos = i * stripe_width
        rect = plt.Rectangle((0, y_pos), field_length, stripe_width, 
                            color='#157F1F', alpha=0.5)
        ax.add_patch(rect)
    
    # Field markings (white)
    marking_color = 'white'
    line_width = 2
    
    # Draw the field outline
    plt.plot([0, 0, field_length, field_length, 0], [0, field_width, field_width, 0, 0], 
             color=marking_color, linewidth=line_width)
    
    # Draw the center line
    plt.plot([field_length/2, field_length/2], [0, field_width], 
             color=marking_color, linewidth=line_width)
    
    # Draw the center circle
    center_circle = plt.Circle((field_length/2, field_width/2), 10, 
                               fill=False, color=marking_color, linewidth=line_width)
    ax.add_artist(center_circle)
    
    # Draw the center spot
    center_spot = plt.Circle((field_length/2, field_width/2), 0.8, 
                             color=marking_color, linewidth=line_width)
    ax.add_artist(center_spot)
    
    # Draw the penalty boxes
    # Left penalty box
    plt.plot([0, 18, 18, 0], [field_width/2 - 22, field_width/2 - 22, field_width/2 + 22, field_width/2 + 22], 
             color=marking_color, linewidth=line_width)
    
    # Right penalty box
    plt.plot([field_length, field_length - 18, field_length - 18, field_length], 
             [field_width/2 - 22, field_width/2 - 22, field_width/2 + 22, field_width/2 + 22], 
             color=marking_color, linewidth=line_width)
    
    # Draw the goal boxes
    # Left goal box
    plt.plot([0, 6, 6, 0], [field_width/2 - 10, field_width/2 - 10, field_width/2 + 10, field_width/2 + 10], 
             color=marking_color, linewidth=line_width)
    
    # Right goal box
    plt.plot([field_length, field_length - 6, field_length - 6, field_length], 
             [field_width/2 - 10, field_width/2 - 10, field_width/2 + 10, field_width/2 + 10], 
             color=marking_color, linewidth=line_width)
    
    # Draw the penalty arcs
    left_penalty_arc = patches.Arc((12, field_width/2), 20, 20, theta1=310, theta2=50, 
                                   color=marking_color, linewidth=line_width)
    right_penalty_arc = patches.Arc((field_length - 12, field_width/2), 20, 20, theta1=130, theta2=230, 
                                    color=marking_color, linewidth=line_width)
    ax.add_patch(left_penalty_arc)
    ax.add_patch(right_penalty_arc)
    
    # Draw the penalty spots
    left_penalty_spot = plt.Circle((12, field_width/2), 0.8, 
                                  color=marking_color, linewidth=line_width)
    right_penalty_spot = plt.Circle((field_length - 12, field_width/2), 0.8, 
                                   color=marking_color, linewidth=line_width)
    ax.add_artist(left_penalty_spot)
    ax.add_artist(right_penalty_spot)
    
    # Draw the corner arcs
    corner_radius = 2
    top_left_corner = patches.Arc((0, field_width), corner_radius, corner_radius, 
                                  theta1=0, theta2=90, color=marking_color, linewidth=line_width)
    top_right_corner = patches.Arc((field_length, field_width), corner_radius, corner_radius, 
                                   theta1=90, theta2=180, color=marking_color, linewidth=line_width)
    bottom_left_corner = patches.Arc((0, 0), corner_radius, corner_radius, 
                                     theta1=270, theta2=360, color=marking_color, linewidth=line_width)
    bottom_right_corner = patches.Arc((field_length, 0), corner_radius, corner_radius, 
                                      theta1=180, theta2=270, color=marking_color, linewidth=line_width)
    ax.add_patch(top_left_corner)
    ax.add_patch(top_right_corner)
    ax.add_patch(bottom_left_corner)
    ax.add_patch(bottom_right_corner)
    
    # Draw the goals
    goal_width = 8
    goal_depth = 2
    
    # Left goal
    plt.plot([-goal_depth, 0, 0, -goal_depth], 
             [field_width/2 - goal_width/2, field_width/2 - goal_width/2, 
              field_width/2 + goal_width/2, field_width/2 + goal_width/2], 
             color=marking_color, linewidth=line_width)
    
    # Right goal
    plt.plot([field_length, field_length + goal_depth, field_length + goal_depth, field_length], 
             [field_width/2 - goal_width/2, field_width/2 - goal_width/2, 
              field_width/2 + goal_width/2, field_width/2 + goal_width/2], 
             color=marking_color, linewidth=line_width)
    
    # Determine position coordinates (x, y)
    position_coords = {
        'Goalkeeper': (field_length - 3, field_width / 2),
        'Center Back': (field_length - 20, field_width / 2),
        'Left Back': (field_length - 20, field_width / 4),
        'Right Back': (field_length - 20, 3 * field_width / 4),
        'Defensive Midfielder': (field_length - 40, field_width / 2),
        'Midfielder': (field_length / 2, field_width / 2),
        'Left Wing': (field_length / 2, field_width / 4),
        'Right Wing': (field_length / 2, 3 * field_width / 4),
        'Forward': (20, field_width / 2),
        'Striker': (10, field_width / 2),
        'Left Midfielder': (field_length / 2, field_width / 3),
        'Right Midfielder': (field_length / 2, 2 * field_width / 3),
        'Center Forward': (15, field_width / 2),
    }
    
    # Default position if not in our map
    default_pos = (field_length / 2, field_width / 2)
    
    # Highlight player's position
    if position in position_coords:
        x, y = position_coords[position]
    else:
        x, y = default_pos
        
    # Add influence zone (heat map)
    influence_radius = 25
    influence = plt.Circle((x, y), influence_radius, alpha=0.2, color=ACCENT_COLOR)
    ax.add_patch(influence)
    
    # Add secondary influence zone with gradient
    for r in range(15, influence_radius, 3):
        alpha = 0.15 - (r/influence_radius) * 0.1
        influence = plt.Circle((x, y), r, alpha=alpha, color=ACCENT_COLOR)
        ax.add_patch(influence)
    
    # Player marker with gradient fill
    player_marker = plt.Circle((x, y), 4, color=PRIMARY_COLOR, ec=SECONDARY_COLOR, lw=2.5, alpha=0.9, zorder=10)
    ax.add_patch(player_marker)
    
    # Add position label with professional styling
    text_position = position if position in position_coords else "Position Unknown"
    plt.annotate(text_position, (x, y), xytext=(0, -10), textcoords='offset points', 
                ha='center', va='center', color='white', fontsize=14, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", fc=SECONDARY_COLOR, ec=ACCENT_COLOR, lw=1.5, alpha=0.9))
    
    # Add player movement lines/arrows based on position
    if position in ['Striker', 'Forward', 'Center Forward']:
        # Attackers make forward runs
        plt.arrow(x+5, y, -15, 0, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
        plt.arrow(x+3, y+7, -10, -5, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
    elif 'Midfielder' in position:
        # Midfielders move in multiple directions
        plt.arrow(x, y+10, 0, -5, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
        plt.arrow(x-10, y, 5, 0, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
        plt.arrow(x+10, y, -5, 0, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
    elif 'Back' in position or position == 'Goalkeeper':
        # Defenders make sideways and forward passes
        plt.arrow(x, y, 15, 0, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
        plt.arrow(x, y, 0, 10, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
        plt.arrow(x, y, 0, -10, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
    
    # Remove axes and set limits
    plt.axis('off')
    plt.xlim(-5, field_length + 5)
    plt.ylim(-5, field_width + 5)
    
    # Add field gradient overlay for aesthetics
    gradient = np.linspace(0, 1, 100).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    extent = [-5, field_length + 5, -5, field_width + 5]
    plt.imshow(gradient, cmap=plt.cm.Greens, alpha=0.1, extent=extent, aspect='auto')
    
    # Add a title to the field
    plt.title(f'Player Position: {position}', fontsize=16, fontweight='bold', color=SECONDARY_COLOR, pad=15)
    
    # Set dark green background
    ax.set_facecolor('#1A8022')
    fig.patch.set_facecolor('#1A8022')
    
    # Return the figure
    return fig


def create_performance_chart(stats, title):
    """Creates a modern horizontal bar chart for player performance stats"""
    
    # Sort stats by value
    sorted_items = sorted(stats.items(), key=lambda x: x[1])
    categories = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot horizontal bars
    bars = ax.barh(categories, values, height=0.6, color=PRIMARY_COLOR, alpha=0.8)
    
    # Add data labels on each bar
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                f'{width}', ha='left', va='center', fontweight='bold', fontsize=11)
    
    # Add a subtle grid
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    
    # Style the chart
    ax.set_title(title, fontsize=16, fontweight='bold', color=SECONDARY_COLOR, pad=20)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')
    
    # Remove the frame
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Set y-axis labels styling
    ax.tick_params(axis='y', labelsize=12, pad=10)
    ax.tick_params(axis='x', labelsize=10)
    
    # Add a subtle background color to alternate rows
    for i, category in enumerate(categories):
        if i % 2 == 0:
            ax.axhspan(i-0.4, i+0.4, color='#f2f2f2', alpha=0.5)
    
    plt.tight_layout()
    return fig


def create_progress_chart(dates, values, title, ylabel, color=PRIMARY_COLOR):
    """Creates an advanced line chart for showing player progress"""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Ensure dates are properly formatted
    if not isinstance(dates[0], datetime):
        try:
            dates = [datetime.strptime(d, '%Y-%m-%d') if isinstance(d, str) else d for d in dates]
        except:
            pass
    
    # Plot the main line with markers
    ax.plot(dates, values, marker='o', linestyle='-', linewidth=3, 
            color=color, markersize=8, markerfacecolor='white', markeredgewidth=2)
    
    # Add area fill below the line
    ax.fill_between(dates, 0, values, color=color, alpha=0.1)
    
    # Add trend line (simple moving average)
    window_size = min(3, len(values))
    if window_size > 1:
        trend = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
        trend_dates = dates[window_size-1:]
        ax.plot(trend_dates, trend, '--', color=SECONDARY_COLOR, linewidth=2, alpha=0.7)
    
    # Add data labels
    for i, (x, y) in enumerate(zip(dates, values)):
        ax.text(x, y + max(values)*0.05, f'{y}', ha='center', va='bottom', 
                fontweight='bold', fontsize=10, color=TEXT_COLOR)
    
    # Style the chart
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold', color=TEXT_COLOR)
    ax.set_title(title, fontsize=16, fontweight='bold', color=SECONDARY_COLOR, pad=20)
    
    # Add a subtle grid
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Remove the top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Style the remaining spines
    ax.spines['bottom'].set_color('#cccccc')
    ax.spines['left'].set_color('#cccccc')
    
    # Set background color
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')
    
    # Format x-axis dates
    fig.autofmt_xdate()
    
    # Add a subtle annotation explaining the trend
    if len(values) > 1:
        overall_trend = "improving" if values[-1] > values[0] else "declining"
        trend_color = SUCCESS_COLOR if values[-1] > values[0] else HIGHLIGHT_COLOR
        ax.annotate(f'Overall trend: {overall_trend}', 
                    xy=(0.02, 0.95), xycoords='axes fraction',
                    fontsize=10, fontweight='bold', color=trend_color,
                    bbox=dict(boxstyle="round,pad=0.3", fc='white', ec=trend_color, alpha=0.8))
    
    plt.tight_layout()
    return fig


class PlayerReportPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=15)
        self.academy_name = "SOCCER CENTRAL SA"
        
        # Check if fonts directory exists
        fonts_dir = os.path.join(ASSETS_DIR, "fonts")
        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir, exist_ok=True)
        
        # Add fonts - using standard fonts as fallback
        try:
            self.add_font('Montserrat', '', os.path.join(fonts_dir, 'Montserrat-Regular.ttf'), uni=True)
            self.add_font('Montserrat', 'B', os.path.join(fonts_dir, 'Montserrat-Bold.ttf'), uni=True)
            self.add_font('Montserrat', 'I', os.path.join(fonts_dir, 'Montserrat-Italic.ttf'), uni=True)
            self.add_font('Montserrat', 'BI', os.path.join(fonts_dir, 'Montserrat-BoldItalic.ttf'), uni=True)
        except:
            # If Montserrat is not available, use standard fonts
            pass
    
    def header(self):
        # If on the first page, don't add the standard header
        if self.page_no() == 1:
            return
        
        # Header background
        self.set_fill_color(26, 54, 93)  # Navy blue (SECONDARY_COLOR)
        self.rect(0, 0, 210, 20, 'F')
        
        # Green accent bar
        self.set_fill_color(30, 132, 73)  # Green (PRIMARY_COLOR)
        self.rect(0, 20, 210, 3, 'F')
        
        # Academy name
        self.set_font('Arial', 'B', 14)
        self.set_text_color(255, 255, 255)  # White
        self.set_xy(10, 6)
        self.cell(0, 10, self.academy_name, 0, 0, 'L')
        
        # Report type
        self.set_font('Arial', 'I', 12)
        self.set_xy(140, 6)
        self.cell(60, 10, 'PLAYER SCOUTING REPORT', 0, 0, 'R')
        
        # Reset position
        self.ln(25)
    
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        
        # Add a line
        self.set_draw_color(30, 132, 73)  # Green
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        
        # Footer text
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'{self.academy_name} © {datetime.now().year}', 0, 0, 'L')
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'R')
    
    def chapter_title(self, title):
        # Set font
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(26, 54, 93)  # Navy blue
        self.set_text_color(255, 255, 255)  # White
        
        # Add title with rounded corners
        self.rounded_rect(10, self.get_y(), 190, 10, 2, 'F')
        self.set_xy(15, self.get_y() + 0.5)
        self.cell(180, 9, title, 0, 1, 'L')
        
        # Line break
        self.ln(5)
    
    def rounded_rect(self, x, y, w, h, r, style=''):
        """Draw a rectangle with rounded corners"""
        k = 0.4  # Curvature factor
        self.set_line_width(0.5)
        
        # Draw the rectangle with rounded corners
        self.ellipse(x, y, r*2, r*2, style)
        self.ellipse(x+w-r*2, y, r*2, r*2, style)
        self.ellipse(x, y+h-r*2, r*2, r*2, style)
        self.ellipse(x+w-r*2, y+h-r*2, r*2, r*2, style)
        
        self.rect(x+r, y, w-r*2, h, style)
        self.rect(x, y+r, w, h-r*2, style)
    
    def section_title(self, title):
        # Set font
        self.set_font('Arial', 'B', 14)
        self.set_text_color(30, 132, 73)  # Green
        
        # Add title
        self.cell(0, 10, title, 0, 1, 'L')
        
        # Add a styled underline
        self.set_draw_color(30, 132, 73)  # Green
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 80, self.get_y())
        
        # Add a secondary accent line
        self.set_draw_color(26, 54, 93)  # Navy blue
        self.set_line_width(1.5)
        self.line(10, self.get_y()+1, 50, self.get_y()+1)
        
        # Line break
        self.ln(5)
    
    def field_value(self, field, value, width_field=50, width_value=140, height=8):
        # Set font for field
        self.set_font('Arial', 'B', 10)
        self.set_text_color(26, 54, 93)  # Navy blue
        
        # Add field
        self.cell(width_field, height, field, 0, 0)
        
        # Set font for value
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)  # Black
        
        # Add value
        self.cell(width_value, height, str(value), 0, 1)
    
    def add_info_table(self, data, title=None):
        if title:
            self.section_title(title)
        
        self.set_font('Arial', '', 10)
        line_height = 8
        
        # Calculate column width dynamically based on the number of columns
        num_columns = len(data[0].keys())
        col_width = 190 / num_columns  # 190mm is the approximate width of the page
        
        # Table header
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(26, 54, 93)  # Navy blue
        self.set_text_color(255, 255, 255)  # White
        
        for header in data[0].keys():
            self.cell(col_width, line_height, str(header), 1, 0, 'C', 1)
        self.ln()
        
        # Table data
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)  # Black
        
        # Alternate row colors for better readability
        row_colors = [(255, 255, 255), (240, 248, 245)]  # White and light green
        
        for i, row in enumerate(data):
            # Set row color
            self.set_fill_color(*row_colors[i % 2])
            
            for key, value in row.items():
                self.cell(col_width, line_height, str(value), 1, 0, 'C', 1)
            self.ln()
        
        self.ln(4)
    
    def add_plot(self, fig, width=190, height=100):
        """Add a matplotlib figure to the PDF"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.savefig(tmpfile.name, format='png', dpi=300, bbox_inches='tight', facecolor='white')
            self.image(tmpfile.name, x=10, w=width, h=height)
            self.ln(height + 10)  # Line break after image
            plt.close(fig)
            os.unlink(tmpfile.name)  # Clean up temporary file
    
    def add_player_header(self, player_data):
        """Add a professional player header with photo and key info"""
        # Create a gradient header background
        self.set_fill_color(26, 54, 93)  # Navy blue (SECONDARY_COLOR)
        self.rect(0, 0, 210, 60, 'F')
        
        # Add green accent bar at the bottom of the header
        self.set_fill_color(30, 132, 73)  # Green (PRIMARY_COLOR)
        self.rect(0, 60, 210, 5, 'F')
        
        # Add academy name
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 215, 0)  # Gold (ACCENT_COLOR)
        self.set_xy(60, 8)
        self.cell(140, 10, self.academy_name, 0, 1, 'L')
        
        # Add player name
        self.set_font('Arial', 'B', 26)
        self.set_text_color(255, 255, 255)  # White
        self.set_xy(60, 22)
        self.cell(140, 10, f"{player_data['first_name']} {player_data['last_name']}".upper(), 0, 1, 'L')
        
        # Add player position with icon
        self.set_font('Arial', 'B', 14)
        self.set_xy(60, 35)
        self.cell(140, 8, f"{player_data['primary_position']}", 0, 1, 'L')
        
        # Add nationality with flag placeholder
        self.set_font('Arial', '', 12)
        self.set_xy(60, 45)
        self.cell(140, 8, f"Nationality: {player_data['nationality']}", 0, 1, 'L')
        
        # Try to add player photo
        try:
            # Check if photo_url is a web URL
            if player_data.get('photo_url') and player_data['photo_url'].startswith(('http://', 'https://')):
                # Create a circular mask effect by drawing a rounded rectangle
                self.set_fill_color(255, 255, 255)  # White background for photo
                self.rounded_rect(10, 10, 45, 45, 5, 'F')
                
                # Download the image from URL to a temporary file
                response = requests.get(player_data['photo_url'])
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
                        tmpfile.write(response.content)
                        self.image(tmpfile.name, 10, 10, 45, 45)
                        os.unlink(tmpfile.name)  # Clean up temporary file
            # Local file path
            elif player_data.get('photo_url'):
                self.set_fill_color(255, 255, 255)  # White background for photo
                self.rounded_rect(10, 10, 45, 45, 5, 'F')
                self.image(player_data['photo_url'], 10, 10, 45, 45)
        except Exception as e:
            # If image loading fails, add a placeholder
            self.set_fill_color(200, 200, 200)  # Light grey
            self.rounded_rect(10, 10, 45, 45, 5, 'F')
            self.set_font('Arial', 'B', 12)
            self.set_text_color(100, 100, 100)
            self.set_xy(15, 25)
            self.cell(35, 10, 'PHOTO', 0, 0, 'C')
        
        # Add key stats in the right side
        # Background rectangle for stats
        self.set_fill_color(30, 132, 73)  # Green
        self.rounded_rect(150, 15, 50, 35, 3, 'F')
        
        # Add stats title
        self.set_font('Arial', 'B', 10)
        self.set_text_color(255, 255, 255)
        self.set_xy(150, 15)
        self.cell(50, 8, 'KEY STATS', 0, 1, 'C')
        
        # Add stats
        self.set_font('Arial', '', 9)
        self.set_xy(155, 25)
        self.cell(20, 6, 'Age:', 0, 0, 'L')
        self.set_font('Arial', 'B', 9)
        age = datetime.now().year - player_data['birth_date'].year
        self.cell(20, 6, f"{age}", 0, 1, 'R')
        
        self.set_font('Arial', '', 9)
        self.set_xy(155, 32)
        self.cell(20, 6, 'Height:', 0, 0, 'L')
        self.set_font('Arial', 'B', 9)
        self.cell(20, 6, f"{player_data['height']} cm", 0, 1, 'R')
        
        self.set_font('Arial', '', 9)
        self.set_xy(155, 39)
        self.cell(20, 6, 'Foot:', 0, 0, 'L')
        self.set_font('Arial', 'B', 9)
        self.cell(20, 6, f"{player_data['dominant_foot']}", 0, 1, 'R')
        
        # Add Jersey Number in a circle
        if player_data.get('number'):
            self.set_fill_color(255, 215, 0)  # Gold
            self.ellipse(130, 25, 15, 15, 'F')
            self.set_font('Arial', 'B', 14)
            self.set_text_color(26, 54, 93)  # Navy blue
            self.set_xy(130, 25)
            self.cell(15, 15, str(player_data['number']), 0, 0, 'C')
        
        # Reset position for next content
        self.set_y(75)
    
    def add_player_profile(self, player_data):
        """Add detailed player profile section"""
        self.chapter_title("PLAYER PROFILE")
        
        # Create a two-column layout for player info
        col_width = 90  # Width for each column
        
        # Personal Information Section
        self.section_title("PERSONAL INFORMATION")
        
        # Add a modern profile box with light background
        self.set_fill_color(245, 249, 246)  # Light green-gray
        self.rounded_rect(10, self.get_y(), 190, 40, 3, 'F')
        
        # Left column
        self.set_xy(15, self.get_y() + 5)
        self.field_value("Full Name", f"{player_data['first_name']} {player_data['last_name']}", 40, 45)
        
        self.set_xy(15, self.get_y() + 2)
        birth_date_str = player_data['birth_date'].strftime('%b %d, %Y') if hasattr(player_data['birth_date'], 'strftime') else str(player_data['birth_date'])
        self.field_value("Date of Birth", birth_date_str, 40, 45)
        
        self.set_xy(15, self.get_y() + 2)
        self.field_value("Nationality", player_data['nationality'], 40, 45)
        
        # Right column
        self.set_xy(110, self.get_y() - 20)
        sec_position = player_data.get('secondary_position', 'N/A')
        self.field_value("Position", f"{player_data['primary_position']} / {sec_position}", 40, 45)
        
        self.set_xy(110, self.get_y() + 2)
        self.field_value("Dominant Foot", player_data['dominant_foot'], 40, 45)
        
        self.set_xy(110, self.get_y() + 2)
        self.field_value("Jersey Number", player_data.get('number', 'N/A'), 40, 45)
        
        # Reset position
        self.set_y(self.get_y() + 15)
        
        # Academy Information Section
        self.section_title("ACADEMY INFORMATION")
        
        # Add a modern info box with light background
        self.set_fill_color(245, 249, 246)  # Light green-gray
        self.rounded_rect(10, self.get_y(), 190, 40, 3, 'F')
        
        # Left column
        self.set_xy(15, self.get_y() + 5)
        self.field_value("Height", f"{player_data['height']} cm", 40, 45)
        
        self.set_xy(15, self.get_y() + 2)
        self.field_value("Education", player_data.get('education_level', 'High School'), 40, 45)
        
        self.set_xy(15, self.get_y() + 2)
        self.field_value("School", player_data.get('school_name', 'Soccer Central SA'), 40, 45)
        
        # Right column
        self.set_xy(110, self.get_y() - 20)
        last_team = player_data.get('last_team', 'Soccer Central SA')
        self.field_value("Current Team", last_team, 40, 45)
        
        self.set_xy(110, self.get_y() + 2)
        grad_date = player_data.get('graduation_date', 'Upcoming')
        self.field_value("Graduation", grad_date, 40, 45)
        
        self.set_xy(110, self.get_y() + 2)
        self.field_value("Training", player_data.get('training_location', 'Main Field'), 40, 45)
        
        # Reset position
        self.set_y(self.get_y() + 15)
    
    def add_player_skills_radar(self, skills_data):
        """Add a radar chart showing the player's skills"""
        # Set title for the section
        self.section_title("SKILLS ASSESSMENT")
        
        # Create the radar chart
        attributes = list(skills_data.keys())
        stats = list(skills_data.values())
        
        radar_fig = create_radar_chart(stats, attributes)
        
        # Add the plot to the PDF
        self.add_plot(radar_fig, width=160, height=160)
    
    def add_performance_metrics(self, metrics_data, title="PERFORMANCE METRICS"):
        """Add a table of performance metrics"""
        self.section_title(title)
        
        # Create a professional metrics visualization
        fig = create_performance_chart(metrics_data, "Season Performance Stats")
        self.add_plot(fig, width=180, height=100)
    
    def add_player_position_field(self, position):
        """Add a field diagram showing the player's position"""
        self.section_title("FIELD POSITION & MOVEMENT")
        
        # Create field position visualization
        field_fig = create_soccer_field_position_image(position)
        
        # Add the plot to the PDF
        self.add_plot(field_fig, width=180, height=110)
    
    def add_stats_comparison(self, player_stats, league_avg, title="PLAYER VS. LEAGUE AVERAGE"):
        """Add a comparison between player stats and league average"""
        self.section_title(title)
        
        # Calculate column width
        col_width = 60
        
        # Draw header row with rounded corners at top
        self.set_fill_color(26, 54, 93)  # Navy blue
        self.set_text_color(255, 255, 255)  # White
        self.rounded_rect(10, self.get_y(), col_width*3, 10, 2, 'F')
        
        # Draw header text
        self.set_font('Arial', 'B', 10)
        self.set_xy(10, self.get_y())
        self.cell(col_width, 10, "Metric", 0, 0, 'C')
        self.cell(col_width, 10, "Player", 0, 0, 'C')
        self.cell(col_width, 10, "League Avg", 0, 0, 'C')
        self.ln()
        
        # Draw data rows
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)  # Black
        
        row_colors = [(255, 255, 255), (240, 249, 246)]  # White and light green
        
        i = 0
        for metric, values in player_stats.items():
            # Set row color
            self.set_fill_color(*row_colors[i % 2])
            
            # Create row rectangle
            self.rect(10, self.get_y(), col_width*3, 10, 'F')
            
            # Draw metric name
            self.set_font('Arial', 'B', 10)
            self.set_text_color(26, 54, 93)  # Navy blue
            self.set_xy(10, self.get_y())
            self.cell(col_width, 10, metric, 0, 0, 'L')
            
            # Draw player value
            player_value = values['player']
            league_value = league_avg.get(metric, 0)
            
            # Set color based on comparison
            if player_value > league_value:
                self.set_text_color(46, 204, 113)  # Green for better than average
            elif player_value < league_value:
                self.set_text_color(231, 76, 60)  # Red for worse than average
            else:
                self.set_text_color(0, 0, 0)  # Black for equal
            
            self.set_font('Arial', 'B', 10)
            self.set_xy(10 + col_width, self.get_y())
            self.cell(col_width, 10, str(player_value), 0, 0, 'C')
            
            # Reset color for league average
            self.set_text_color(0, 0, 0)
            self.set_font('Arial', '', 10)
            self.set_xy(10 + col_width*2, self.get_y())
            self.cell(col_width, 10, str(league_value), 0, 0, 'C')
            
            self.ln(10)
            i += 1
        
        # Add a rounded corner at the bottom
        self.set_fill_color(*row_colors[i % 2])
        self.rounded_rect(10, self.get_y()-2, col_width*3, 4, 2, 'F')
        
        self.ln(10)
    
    def add_coach_assessment(self):
        """Add a professional coach assessment section"""
        self.chapter_title("COACH ASSESSMENT")
        
        # Create modern assessment sections
        self.section_title("STRENGTHS")
        
        # Create a stylish strengths box
        self.set_fill_color(240, 249, 246)  # Light green
        self.set_draw_color(30, 132, 73)  # Green
        self.set_line_width(0.3)
        self.rounded_rect(10, self.get_y(), 190, 35, 3, 'FD')
        
        # Add strength icons
        for i in range(3):
            self.set_fill_color(30, 132, 73)  # Green
            self.set_draw_color(26, 54, 93)  # Navy blue
            self.rounded_rect(15 + (i*65), self.get_y() + 5, 55, 25, 2, 'FD')
            
            # Add strength text
            self.set_font('Arial', 'B', 9)
            self.set_text_color(255, 255, 255)  # White
            strengths = ["Ball Control", "Physical Presence", "Game Vision"]
            self.set_xy(15 + (i*65), self.get_y() + 7)
            self.cell(55, 5, strengths[i], 0, 1, 'C')
            
            # Add strength descriptions
            self.set_font('Arial', '', 7)
            descriptions = [
                "Excellent dribbling and\nfirst touch skills",
                "Strong in physical duels\nand holding the ball",
                "Great passing and field\nawareness"
            ]
            self.set_xy(15 + (i*65), self.get_y())
            self.multi_cell(55, 3, descriptions[i], 0, 'C')
        
        self.ln(45)
        
        self.section_title("AREAS FOR IMPROVEMENT")
        
        # Create a stylish improvement box
        self.set_fill_color(252, 243, 240)  # Light red/orange
        self.set_draw_color(231, 76, 60)  # Red
        self.set_line_width(0.3)
        self.rounded_rect(10, self.get_y(), 190, 35, 3, 'FD')
        
        # Add improvement icons
        for i in range(3):
            self.set_fill_color(231, 76, 60)  # Red
            self.set_draw_color(26, 54, 93)  # Navy blue
            self.rounded_rect(15 + (i*65), self.get_y() + 5, 55, 25, 2, 'FD')
            
            # Add improvement text
            self.set_font('Arial', 'B', 9)
            self.set_text_color(255, 255, 255)  # White
            improvements = ["Defensive Positioning", "Weaker Foot", "Decision Speed"]
            self.set_xy(15 + (i*65), self.get_y() + 7)
            self.cell(55, 5, improvements[i], 0, 1, 'C')
            
            # Add improvement descriptions
            self.set_font('Arial', '', 7)
            descriptions = [
                "Needs to track back\nbetter when team loses\npossession",
                "Right foot finishing\nneeds improvement for\nversatility",
                "Sometimes holds ball\ntoo long before making\npasses"
            ]
            self.set_xy(15 + (i*65), self.get_y())
            self.multi_cell(55, 3, descriptions[i], 0, 'C')
        
        self.ln(45)
        
        self.section_title("DEVELOPMENT PLAN")
        
        # Create a stylish development box
        self.set_fill_color(240, 248, 255)  # Light blue
        self.set_draw_color(26, 54, 93)  # Navy blue
        self.set_line_width(0.3)
        self.rounded_rect(10, self.get_y(), 190, 50, 3, 'FD')
        
        # Add development content with modern formatting
        self.set_font('Arial', 'B', 10)
        self.set_text_color(26, 54, 93)  # Navy blue
        self.set_xy(15, self.get_y() + 5)
        self.cell(180, 5, "SHORT-TERM OBJECTIVES:", 0, 1, 'L')
        
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)  # Black
        self.set_xy(20, self.get_y() + 2)
        self.multi_cell(175, 4, "* Focus on defensive positioning drills and tracking exercises\n* Schedule additional technical sessions to improve weaker foot\n* Work with the team on tactical sessions to enhance decision-making speed", 0, 'L')
        
        self.set_font('Arial', 'B', 10)
        self.set_text_color(26, 54, 93)  # Navy blue
        self.set_xy(15, self.get_y() + 5)
        self.cell(180, 5, "LONG-TERM DEVELOPMENT:", 0, 1, 'L')
        
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)  # Black
        self.set_xy(20, self.get_y() + 2)
        self.multi_cell(175, 4, "* Implement structured fitness program to maintain peak physical condition\n* Develop leadership qualities through captaincy opportunities\n* Integrate video analysis sessions to improve tactical understanding", 0, 'L')
        
        self.ln(60)
        
        # Coaching signature section
        self.section_title("COACH SIGNATURE")
        
        # Create signature box with modern styling
        self.set_fill_color(245, 245, 245)  # Light gray
        self.rounded_rect(10, self.get_y(), 190, 30, 3, 'F')
        
        # Add signature lines with styling
        self.set_font('Arial', '', 10)
        self.set_xy(15, self.get_y() + 5)
        self.cell(85, 8, "Coach Name: _____________________________", 0, 0, 'L')
        self.cell(85, 8, "Date: _________________________", 0, 1, 'L')
        
        self.set_xy(15, self.get_y() + 5)
        self.cell(180, 8, "Signature: _________________________________________________", 0, 1, 'L')
        
        # Add academy stamp placeholder
        self.set_xy(140, self.get_y() - 15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(50, 8, "Academy Stamp", 0, 1, 'C')
        
        # Draw a circular stamp outline
        self.set_draw_color(128, 128, 128)
        self.set_line_width(0.2)
        self.ellipse(150, self.get_y() - 20, 30, 15, 'D')


def generate_player_report(player_data, player_teams, player_games, player_metrics, 
                          player_evaluations, player_videos, player_documents):
    """Generate a PDF report for a player"""
    
    # Create FPDF object
    pdf = PlayerReportPDF()
    pdf.alias_nb_pages()
    
    # Ensure assets directory exists
    if not os.path.exists(os.path.join(ASSETS_DIR, 'images')):
        os.makedirs(os.path.join(ASSETS_DIR, 'images'), exist_ok=True)
    
    # Create first page with player details
    pdf.add_page()
    
    # Add professional header with player info
    pdf.add_player_header(player_data)
    
    # Add player profile section
    pdf.add_player_profile(player_data)
    
    # Add player position field visualization
    pdf.add_player_position_field(player_data['primary_position'])
    
    # Add player skills radar
    # Generate sample skills data if not provided
    skills_data = {
        "Technical": np.random.randint(70, 98),
        "Physical": np.random.randint(70, 98),
        "Tactical": np.random.randint(70, 98),
        "Mental": np.random.randint(70, 98),
        "Attacking": np.random.randint(70, 98),
        "Defending": np.random.randint(70, 98),
    }
    
    pdf.add_player_skills_radar(skills_data)
    
    # Add a new page for performance statistics
    pdf.add_page()
    pdf.chapter_title("PERFORMANCE STATISTICS")
    
    # Add performance metrics
    # Generate sample performance metrics if not provided
    performance_metrics = {
        "Games Played": 22,
        "Goals": 8,
        "Assists": 6,
        "Minutes": 1820,
        "Pass Accuracy": 87,
        "Tackles": 45
    }
    
    pdf.add_performance_metrics(performance_metrics)
    
    # Add player vs. league comparison
    player_comparison = {
        "Goals per 90 min": {"player": 0.4},
        "Passing Accuracy %": {"player": 87},
        "Tackles per Game": {"player": 2.1},
        "Distance Covered (km)": {"player": 10.3},
        "Successful Dribbles": {"player": 3.2}
    }
    
    league_average = {
        "Goals per 90 min": 0.2,
        "Passing Accuracy %": 82,
        "Tackles per Game": 1.8,
        "Distance Covered (km)": 9.8,
        "Successful Dribbles": 2.1
    }
    
    pdf.add_stats_comparison(player_comparison, league_average)
    
    # Add seasonal progress chart
    months = ["Jan", "Feb", "Mar", "Apr", "May"]
    performance_values = [65, 70, 68, 75, 82]
    
    progress_fig = create_progress_chart(months, performance_values, 
                                        "Performance Progress", "Performance Rating")
    pdf.add_plot(progress_fig)
    
    # Add coach assessment page
    pdf.add_page()
    pdf.add_coach_assessment()
    

    # Create PDF in memory buffer using dest='S'
    pdf_output = pdf.output(dest='S').encode('latin1')
    buffer = BytesIO(pdf_output)
    return buffer