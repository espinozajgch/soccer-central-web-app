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
    N = len(attributes)
    theta = radar_factory(N)
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='radar'))
    plt.xticks(theta, attributes, size=12, color=TEXT_COLOR, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.plot(theta, stats, 'o-', linewidth=3, color=PRIMARY_COLOR, alpha=0.9)
    ax.fill(theta, stats, color=PRIMARY_COLOR, alpha=0.3)
    ax.set_rgrids([20, 40, 60, 80], angle=0, color=GRID_COLOR, alpha=0.5)
    
    for i, (angle, stat) in enumerate(zip(theta, stats)):
        ax.text(angle, stat + 10, str(stat), 
                horizontalalignment='center', 
                verticalalignment='center',
                fontsize=11, 
                fontweight='bold',
                color=SECONDARY_COLOR)
    
    ax.set_yticklabels([])
    plt.title('Player Skills Assessment', size=16, color=SECONDARY_COLOR, fontweight='bold', y=1.05)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    background = np.ones(N) * 100
    ax.plot(theta, background, color=GRID_COLOR, linewidth=1, linestyle='--', alpha=0.3)
    ax.fill(theta, background, color=GRID_COLOR, alpha=0.05)
    
    benchmark = np.array([70, 65, 75, 68, 72, 78])
    ax.plot(theta, benchmark, 'o--', linewidth=2, color=ACCENT_COLOR, alpha=0.7, label='League Average')
    ax.fill(theta, benchmark, color=ACCENT_COLOR, alpha=0.1)
    ax.legend(loc='upper right', frameon=True, framealpha=0.9)
    plt.tight_layout()
    
    return fig

def create_soccer_field_position_image(position):
    """Create an image of a soccer field with the player's position highlighted"""
    fig, ax = plt.subplots(figsize=(8, 5))
    field_length = 120
    field_width = 80
    
    rect = plt.Rectangle((0, 0), field_length, field_width, color='#1A8022', alpha=1.0)
    ax.add_patch(rect)
    
    num_stripes = 20
    stripe_width = field_width / num_stripes
    for i in range(0, num_stripes, 2):
        y_pos = i * stripe_width
        rect = plt.Rectangle((0, y_pos), field_length, stripe_width, color='#157F1F', alpha=0.5)
        ax.add_patch(rect)
    
    marking_color = 'white'
    line_width = 2
    
    plt.plot([0, 0, field_length, field_length, 0], [0, field_width, field_width, 0, 0], 
             color=marking_color, linewidth=line_width)
    plt.plot([field_length/2, field_length/2], [0, field_width], 
             color=marking_color, linewidth=line_width)
    
    center_circle = plt.Circle((field_length/2, field_width/2), 10, 
                               fill=False, color=marking_color, linewidth=line_width)
    ax.add_artist(center_circle)
    
    center_spot = plt.Circle((field_length/2, field_width/2), 0.8, 
                             color=marking_color, linewidth=line_width)
    ax.add_artist(center_spot)
    
    plt.plot([0, 18, 18, 0], [field_width/2 - 22, field_width/2 - 22, field_width/2 + 22, field_width/2 + 22], 
             color=marking_color, linewidth=line_width)
    plt.plot([field_length, field_length - 18, field_length - 18, field_length], 
             [field_width/2 - 22, field_width/2 - 22, field_width/2 + 22, field_width/2 + 22], 
             color=marking_color, linewidth=line_width)
    
    plt.plot([0, 6, 6, 0], [field_width/2 - 10, field_width/2 - 10, field_width/2 + 10, field_width/2 + 10], 
             color=marking_color, linewidth=line_width)
    plt.plot([field_length, field_length - 6, field_length - 6, field_length], 
             [field_width/2 - 10, field_width/2 - 10, field_width/2 + 10, field_width/2 + 10], 
             color=marking_color, linewidth=line_width)
    
    left_penalty_arc = patches.Arc((12, field_width/2), 20, 20, theta1=310, theta2=50, 
                                   color=marking_color, linewidth=line_width)
    right_penalty_arc = patches.Arc((field_length - 12, field_width/2), 20, 20, theta1=130, theta2=230, 
                                    color=marking_color, linewidth=line_width)
    ax.add_patch(left_penalty_arc)
    ax.add_patch(right_penalty_arc)
    
    left_penalty_spot = plt.Circle((12, field_width/2), 0.8, color=marking_color, linewidth=line_width)
    right_penalty_spot = plt.Circle((field_length - 12, field_width/2), 0.8, color=marking_color, linewidth=line_width)
    ax.add_artist(left_penalty_spot)
    ax.add_artist(right_penalty_spot)
    
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
    
    goal_width = 8
    goal_depth = 2
    
    plt.plot([-goal_depth, 0, 0, -goal_depth], 
             [field_width/2 - goal_width/2, field_width/2 - goal_width/2, 
              field_width/2 + goal_width/2, field_width/2 + goal_width/2], 
             color=marking_color, linewidth=line_width)
    
    plt.plot([field_length, field_length + goal_depth, field_length + goal_depth, field_length], 
             [field_width/2 - goal_width/2, field_width/2 - goal_width/2, 
              field_width/2 + goal_width/2, field_width/2 + goal_width/2], 
             color=marking_color, linewidth=line_width)
    
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
    
    default_pos = (field_length / 2, field_width / 2)
    
    if position in position_coords:
        x, y = position_coords[position]
    else:
        x, y = default_pos
        
    influence_radius = 25
    influence = plt.Circle((x, y), influence_radius, alpha=0.2, color=ACCENT_COLOR)
    ax.add_patch(influence)
    
    for r in range(15, influence_radius, 3):
        alpha = 0.15 - (r/influence_radius) * 0.1
        influence = plt.Circle((x, y), r, alpha=alpha, color=ACCENT_COLOR)
        ax.add_patch(influence)
    
    player_marker = plt.Circle((x, y), 4, color=PRIMARY_COLOR, ec=SECONDARY_COLOR, lw=2.5, alpha=0.9, zorder=10)
    ax.add_patch(player_marker)
    
    text_position = position if position in position_coords else "Position Unknown"
    plt.annotate(text_position, (x, y), xytext=(0, -10), textcoords='offset points', 
                ha='center', va='center', color='white', fontsize=14, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.5", fc=SECONDARY_COLOR, ec=ACCENT_COLOR, lw=1.5, alpha=0.9))
    
    if position in ['Striker', 'Forward', 'Center Forward']:
        plt.arrow(x+5, y, -15, 0, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
        plt.arrow(x+3, y+7, -10, -5, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
    elif 'Midfielder' in position:
        plt.arrow(x, y+10, 0, -5, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
        plt.arrow(x-10, y, 5, 0, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
        plt.arrow(x+10, y, -5, 0, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
    elif 'Back' in position or position == 'Goalkeeper':
        plt.arrow(x, y, 15, 0, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
        plt.arrow(x, y, 0, 10, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
        plt.arrow(x, y, 0, -10, head_width=3, head_length=5, fc=ACCENT_COLOR, ec=ACCENT_COLOR, alpha=0.7)
    
    plt.axis('off')
    plt.xlim(-5, field_length + 5)
    plt.ylim(-5, field_width + 5)
    
    gradient = np.linspace(0, 1, 100).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    extent = [-5, field_length + 5, -5, field_width + 5]
    plt.imshow(gradient, cmap=plt.cm.Greens, alpha=0.1, extent=extent, aspect='auto')
    
    plt.title(f'Player Position: {position}', fontsize=16, fontweight='bold', color=SECONDARY_COLOR, pad=15)
    
    ax.set_facecolor('#1A8022')
    fig.patch.set_facecolor('#1A8022')
    
    return fig

def create_performance_chart(stats, title):
    """Creates a modern horizontal bar chart for player performance stats"""
    sorted_items = sorted(stats.items(), key=lambda x: x[1])
    categories = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(categories, values, height=0.6, color=PRIMARY_COLOR, alpha=0.8)
    
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                f'{width}', ha='left', va='center', fontweight='bold', fontsize=11)
    
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    ax.set_title(title, fontsize=16, fontweight='bold', color=SECONDARY_COLOR, pad=20)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    ax.tick_params(axis='y', labelsize=12, pad=10)
    ax.tick_params(axis='x', labelsize=10)
    
    for i, category in enumerate(categories):
        if i % 2 == 0:
            ax.axhspan(i-0.4, i+0.4, color='#f2f2f2', alpha=0.5)
    
    plt.tight_layout()
    return fig

def create_progress_chart(dates, values, title, ylabel, color=PRIMARY_COLOR):
    """Creates an advanced line chart for showing player progress"""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    if not isinstance(dates[0], datetime):
        try:
            dates = [datetime.strptime(d, '%Y-%m-%d') if isinstance(d, str) else d for d in dates]
        except:
            pass
    
    ax.plot(dates, values, marker='o', linestyle='-', linewidth=3, 
            color=color, markersize=8, markerfacecolor='white', markeredgewidth=2)
    ax.fill_between(dates, 0, values, color=color, alpha=0.1)
    
    window_size = min(3, len(values))
    if window_size > 1:
        trend = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
        trend_dates = dates[window_size-1:]
        ax.plot(trend_dates, trend, '--', color=SECONDARY_COLOR, linewidth=2, alpha=0.7)
    
    for i, (x, y) in enumerate(zip(dates, values)):
        ax.text(x, y + max(values)*0.05, f'{y}', ha='center', va='bottom', 
                fontweight='bold', fontsize=10, color=TEXT_COLOR)
    
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold', color=TEXT_COLOR)
    ax.set_title(title, fontsize=16, fontweight='bold', color=SECONDARY_COLOR, pad=20)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')
    ax.spines['left'].set_color('#cccccc')
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#f8f9fa')
    fig.autofmt_xdate()
    
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
        
        fonts_dir = os.path.join(ASSETS_DIR, "fonts")
        if not os.path.exists(fonts_dir):
            os.makedirs(fonts_dir, exist_ok=True)
        
        try:
            self.add_font('Montserrat', '', os.path.join(fonts_dir, 'Montserrat-Regular.ttf'), uni=True)
            self.add_font('Montserrat', 'B', os.path.join(fonts_dir, 'Montserrat-Bold.ttf'), uni=True)
            self.add_font('Montserrat', 'I', os.path.join(fonts_dir, 'Montserrat-Italic.ttf'), uni=True)
            self.add_font('Montserrat', 'BI', os.path.join(fonts_dir, 'Montserrat-BoldItalic.ttf'), uni=True)
        except:
            pass
    
    def header(self):
        if self.page_no() == 1:
            return
        
        self.set_fill_color(26, 54, 93)
        self.rect(0, 0, 210, 20, 'F')
        
        self.set_fill_color(30, 132, 73)
        self.rect(0, 20, 210, 3, 'F')
        
        self.set_font('Arial', 'B', 14)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 10, self.academy_name, 0, 0, 'L')
        
        self.set_font('Arial', 'I', 12)
        self.set_xy(140, 6)
        self.cell(60, 10, 'PLAYER SCOUTING REPORT', 0, 0, 'R')
        
        self.ln(25)
    
    def footer(self):
        self.set_y(-15)
        
        self.set_draw_color(30, 132, 73)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        
        self.set_y(-13)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100, 100, 100)
        
        # Left-aligned academy name
        self.set_x(10)
        self.cell(70, 10, f'{self.academy_name} © {datetime.now().year}', 0, 0, 'L')
        
        # Center-aligned page number
        self.set_x(85)
        self.cell(40, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        
        # Right-aligned generation date
        self.set_x(130)
        self.cell(70, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'R')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(26, 54, 93)
        self.set_text_color(255, 255, 255)
        
        self.rounded_rect(10, self.get_y(), 190, 10, 2, 'F')
        self.set_xy(15, self.get_y() + 0.5)
        self.cell(180, 9, title, 0, 1, 'L')
        
        self.ln(5)
    
    def rounded_rect(self, x, y, w, h, r, style=''):
        k = 0.4
        self.set_line_width(0.5)
        
        self.ellipse(x, y, r*2, r*2, style)
        self.ellipse(x+w-r*2, y, r*2, r*2, style)
        self.ellipse(x, y+h-r*2, r*2, r*2, style)
        self.ellipse(x+w-r*2, y+h-r*2, r*2, r*2, style)
        
        self.rect(x+r, y, w-r*2, h, style)
        self.rect(x, y+r, w, h-r*2, style)
    
    def section_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(30, 132, 73)
        
        self.cell(0, 10, title, 0, 1, 'L')
        
        self.set_draw_color(30, 132, 73)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 80, self.get_y())
        
        self.set_draw_color(26, 54, 93)
        self.set_line_width(1.5)
        self.line(10, self.get_y()+1, 50, self.get_y()+1)
        
        self.ln(5)
    
    def field_value(self, field, value, width_field=50, width_value=140, height=8):
        self.set_font('Arial', 'B', 10)
        self.set_text_color(26, 54, 93)
        
        self.cell(width_field, height, field, 0, 0)
        
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        
        self.cell(width_value, height, str(value), 0, 1)
    
    def add_info_table(self, data, title=None):
        if title:
            self.section_title(title)
        
        self.set_font('Arial', '', 10)
        line_height = 8
        
        num_columns = len(data[0].keys())
        col_width = 190 / num_columns
        
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(26, 54, 93)
        self.set_text_color(255, 255, 255)
        
        for header in data[0].keys():
            self.cell(col_width, line_height, str(header), 1, 0, 'C', 1)
        self.ln()
        
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        
        row_colors = [(255, 255, 255), (240, 248, 245)]
        
        for i, row in enumerate(data):
            self.set_fill_color(*row_colors[i % 2])
            
            for key, value in row.items():
                self.cell(col_width, line_height, str(value), 1, 0, 'C', 1)
            self.ln()
        
        self.ln(4)
    
    def add_plot(self, fig, width=190, height=100):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.savefig(tmpfile.name, format='png', dpi=300, bbox_inches='tight', facecolor='white')
            self.image(tmpfile.name, x=10, w=width, h=height)
            self.ln(height + 10)
            plt.close(fig)
            os.unlink(tmpfile.name)
    
    def add_player_header(self, player_data):
        self.set_fill_color(26, 54, 93)
        self.rect(0, 0, 210, 60, 'F')
        
        self.set_fill_color(30, 132, 73)
        self.rect(0, 60, 210, 5, 'F')
        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 215, 0)
        self.set_xy(60, 8)
        self.cell(140, 10, self.academy_name, 0, 1, 'L')
        
        self.set_font('Arial', 'B', 26)
        self.set_text_color(255, 255, 255)
        self.set_xy(60, 22)
        self.cell(140, 10, f"{player_data['first_name']} {player_data['last_name']}".upper(), 0, 1, 'L')
        
        self.set_font('Arial', 'B', 14)
        self.set_xy(60, 35)
        self.cell(140, 8, f"{player_data['primary_position']}", 0, 1, 'L')
        
        self.set_font('Arial', '', 12)
        self.set_xy(60, 45)
        self.cell(140, 8, f"Nationality: {player_data['nationality']}", 0, 1, 'L')
        
        try:
            if player_data.get('photo_url') and player_data['photo_url'].startswith(('http://', 'https://')):
                self.set_fill_color(255, 255, 255)
                self.rounded_rect(10, 10, 45, 45, 5, 'F')
                
                response = requests.get(player_data['photo_url'])
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
                        tmpfile.write(response.content)
                        self.image(tmpfile.name, 10, 10, 45, 45)
                        os.unlink(tmpfile.name)
            elif player_data.get('photo_url'):
                self.set_fill_color(255, 255, 255)
                self.rounded_rect(10, 10, 45,45, 5, 'F')
                self.image(player_data['photo_url'], 10, 10, 45, 45)
        except Exception as e:
            self.set_fill_color(200, 200, 200)
            self.rounded_rect(10, 10, 45, 45, 5, 'F')
            self.set_font('Arial', 'B', 12)
            self.set_text_color(100, 100, 100)
            self.set_xy(15, 25)
            self.cell(35, 10, 'PHOTO', 0, 0, 'C')
        
        self.set_fill_color(30, 132, 73)
        self.rounded_rect(150, 15, 50, 35, 3, 'F')
        
        self.set_font('Arial', 'B', 10)
        self.set_text_color(255, 255, 255)
        self.set_xy(150, 15)
        self.cell(50, 8, 'KEY STATS', 0, 1, 'C')
        
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
        
        if player_data.get('number'):
            self.set_fill_color(255, 215, 0)
            self.ellipse(130, 33, 15, 15, 'F')
            self.set_font('Arial', 'B', 14)
            self.set_text_color(26, 54, 93)
            self.set_xy(130, 33)
            self.cell(15, 15, str(player_data['number']), 0, 0, 'C')
        
        self.set_y(75)
    
    def add_player_profile(self, player_data):
        self.chapter_title("PLAYER PROFILE")
        
        col_width = 90
        
        # PERSONAL INFORMATION
        self.section_title("PERSONAL INFORMATION")
        self.set_fill_color(245, 249, 246)
        y_start = self.get_y()
        self.rounded_rect(10, y_start, 190, 40, 3, 'F')

        # Columna izquierda
        y_left = y_start + 5
        self.set_xy(15, y_left)
        self.field_value("Full Name", f"{player_data['first_name']} {player_data['last_name']}", 40, 45)

        self.set_xy(15, y_left + 8)
        birth_date_str = player_data['birth_date'].strftime('%b %d, %Y') if hasattr(player_data['birth_date'], 'strftime') else str(player_data['birth_date'])
        self.field_value("Date of Birth", birth_date_str, 40, 45)

        self.set_xy(15, y_left + 16)
        self.field_value("Nationality", player_data['nationality'], 40, 45)

        # Columna derecha
        y_right = y_left
        self.set_xy(110, y_right)
        sec_position = player_data.get('secondary_position', 'N/A')
        self.field_value("Position", f"{player_data['primary_position']} / {sec_position}", 40, 45)

        self.set_xy(110, y_right + 8)
        self.field_value("Dominant Foot", player_data['dominant_foot'], 40, 45)

        self.set_xy(110, y_right + 16)
        self.field_value("Jersey Number", player_data.get('number', 'N/A'), 40, 45)

        self.set_y(y_right + 24)  # avanzar para no solaparse con siguiente sección

        
        # ACADEMY INFORMATION
        self.section_title("ACADEMY INFORMATION")
        self.set_fill_color(245, 249, 246)
        y_start = self.get_y()
        self.rounded_rect(10, y_start, 190, 40, 3, 'F')

        # Columna izquierda
        y_left = y_start + 5
        self.set_xy(15, y_left)
        self.field_value("Height", f"{player_data['height']} cm", 40, 45)

        self.set_xy(15, y_left + 8)
        self.field_value("Education", player_data.get('education_level', 'High School'), 40, 45)

        self.set_xy(15, y_left + 16)
        self.field_value("School", player_data.get('school_name', 'Soccer Central SA'), 40, 45)

        # Columna derecha
        y_right = y_left
        self.set_xy(110, y_right)
        last_team = player_data.get('last_team', 'Soccer Central SA')
        self.field_value("Current Team", last_team, 40, 45)

        self.set_xy(110, y_right + 8)
        grad_date = player_data.get('graduation_date', 'Upcoming')
        self.field_value("Graduation", grad_date, 40, 45)

        self.set_xy(110, y_right + 16)
        self.field_value("Training", player_data.get('training_location', 'Main Field'), 40, 45)

        # Espacio extra antes de la siguiente sección
        self.set_y(y_right + 24)

    
    def add_player_skills_radar(self, skills_data):
        self.section_title("SKILLS ASSESSMENT")
        
        attributes = list(skills_data.keys())
        stats = list(skills_data.values())
        
        radar_fig = create_radar_chart(stats, attributes)
        
        self.add_plot(radar_fig, width=160, height=160)
    
    def add_performance_metrics(self, metrics_data, title="PERFORMANCE METRICS"):
        self.section_title(title)
        
        fig = create_performance_chart(metrics_data, "Season Performance Stats")
        self.add_plot(fig, width=180, height=100)
    
    def add_player_position_field(self, position):
        self.section_title("FIELD POSITION & MOVEMENT")
        
        field_fig = create_soccer_field_position_image(position)
        
        self.add_plot(field_fig, width=180, height=110)
    
    def add_stats_comparison(self, player_stats, league_avg, title="PLAYER VS. LEAGUE AVERAGE"):
        col_width = 60
        row_height = 10
        header_height = 10
        footer_height = 4
        padding_bottom = 10

        # Calcular altura total necesaria
        total_rows = len(player_stats)
        required_height = header_height + total_rows * row_height + footer_height + padding_bottom

        # Si no hay suficiente espacio, bajar todo el bloque más abajo en la misma página
        if self.get_y() + required_height > 270:  # margen de seguridad (A4 = 297 mm)
            self.set_y(270 - required_height)

        self.section_title(title)

        self.set_fill_color(26, 54, 93)
        self.set_text_color(255, 255, 255)
        self.rounded_rect(10, self.get_y(), col_width*3, header_height, 2, 'F')

        self.set_font('Arial', 'B', 10)
        self.set_xy(10, self.get_y())
        self.cell(col_width, header_height, "Metric", 0, 0, 'C')
        self.cell(col_width, header_height, "Player", 0, 0, 'C')
        self.cell(col_width, header_height, "League Avg", 0, 0, 'C')
        self.ln()

        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)

        row_colors = [(255, 255, 255), (240, 249, 246)]

        i = 0
        for metric, values in player_stats.items():
            self.set_fill_color(*row_colors[i % 2])

            self.rect(10, self.get_y(), col_width*3, row_height, 'F')

            self.set_font('Arial', 'B', 10)
            self.set_text_color(26, 54, 93)
            self.set_xy(10, self.get_y())
            self.cell(col_width, row_height, metric, 0, 0, 'L')

            player_value = values['player']
            league_value = league_avg.get(metric, 0)

            if player_value > league_value:
                self.set_text_color(46, 204, 113)
            elif player_value < league_value:
                self.set_text_color(231, 76, 60)
            else:
                self.set_text_color(0, 0, 0)

            self.set_font('Arial', 'B', 10)
            self.set_xy(10 + col_width, self.get_y())
            self.cell(col_width, row_height, str(player_value), 0, 0, 'C')

            self.set_text_color(0, 0, 0)
            self.set_font('Arial', '', 10)
            self.set_xy(10 + col_width*2, self.get_y())
            self.cell(col_width, row_height, str(league_value), 0, 0, 'C')

            self.ln(row_height)
            i += 1

        self.set_fill_color(*row_colors[i % 2])
        self.rounded_rect(10, self.get_y() - 2, col_width*3, footer_height, 2, 'F')

        self.ln(padding_bottom)
    
    def add_coach_assessment(self):
        """Add a professional coach assessment section with fixed layout issues"""
        self.chapter_title("COACH ASSESSMENT")
        
        # Store initial Y position
        initial_y = self.get_y()
        
        # STRENGTHS section
        self.section_title("STRENGTHS")
        strengths_y = self.get_y()
        
        # Create strengths box with fixed height
        self.set_fill_color(240, 249, 246)
        self.set_draw_color(30, 132, 73)
        self.set_line_width(0.3)
        self.rounded_rect(10, strengths_y, 190, 40, 3, 'FD')
        
        # Add strength boxes at the same height
        for i in range(3):
            self.set_fill_color(30, 132, 73)
            self.set_draw_color(26, 54, 93)
            self.rounded_rect(15 + (i*65), strengths_y + 5, 55, 25, 2, 'FD')
            
            self.set_font('Arial', 'B', 9)
            self.set_text_color(255, 255, 255)
            strengths = ["Ball Control", "Physical Presence", "Game Vision"]
            self.set_xy(15 + (i*65), strengths_y + 7)
            self.cell(55, 5, strengths[i], 0, 1, 'C')
            
            self.set_font('Arial', '', 7)
            descriptions = [
                "Excellent dribbling and\nfirst touch skills",
                "Strong in physical duels\nand holding the ball",
                "Great passing and field\nawareness"
            ]
            self.set_xy(15 + (i*65), self.get_y())
            self.multi_cell(55, 3, descriptions[i], 0, 'C')
        
        # Reset Y position for AREAS FOR IMPROVEMENT
        self.set_y(strengths_y + 50)
        
        # AREAS FOR IMPROVEMENT section
        self.section_title("AREAS FOR IMPROVEMENT")
        improvement_y = self.get_y()
        
        # Create improvement box with same height as strengths
        self.set_fill_color(252, 243, 240)
        self.set_draw_color(231, 76, 60)
        self.set_line_width(0.3)
        self.rounded_rect(10, improvement_y, 190, 40, 3, 'FD')
        
        # Add improvement boxes at the same height
        for i in range(3):
            self.set_fill_color(231, 76, 60)
            self.set_draw_color(26, 54, 93)
            self.rounded_rect(15 + (i*65), improvement_y + 5, 55, 25, 2, 'FD')
            
            self.set_font('Arial', 'B', 9)
            self.set_text_color(255, 255, 255)
            improvements = ["Defensive Positioning", "Weaker Foot", "Decision Speed"]
            self.set_xy(15 + (i*65), improvement_y + 7)
            self.cell(55, 5, improvements[i], 0, 1, 'C')
            
            self.set_font('Arial', '', 7)
            descriptions = [
                "Needs to track back\nbetter when team loses\npossession",
                "Right foot finishing\nneeds improvement for\nversatility",
                "Sometimes holds ball\ntoo long before making\npasses"
            ]
            self.set_xy(15 + (i*65), self.get_y())
            self.multi_cell(55, 3, descriptions[i], 0, 'C')
        
        # Development Plan section with increased height
        self.ln(45)
        self.section_title("DEVELOPMENT PLAN")
        
        # Create a larger development box
        self.set_fill_color(240, 248, 255)
        self.set_draw_color(26, 54, 93)
        self.set_line_width(0.3)
        self.rounded_rect(10, self.get_y(), 190, 90, 3, 'FD')  # Increased height
        
        # Short-term objectives
        self.set_font('Arial', 'B', 10)
        self.set_text_color(26, 54, 93)
        self.set_xy(15, self.get_y() + 5)
        self.cell(180, 5, "SHORT-TERM OBJECTIVES:", 0, 1, 'L')
        
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        self.set_xy(20, self.get_y() + 2)
        self.multi_cell(175, 4, "* Focus on defensive positioning drills and tracking exercises\n* Schedule additional technical sessions to improve weaker foot\n* Work with the team on tactical sessions to enhance decision-making speed", 0, 'L')
        
        # Long-term development in the same box
        self.set_font('Arial', 'B', 10)
        self.set_text_color(26, 54, 93)
        self.set_xy(15, self.get_y() + 5)
        self.cell(180, 5, "LONG-TERM DEVELOPMENT:", 0, 1, 'L')
        
        self.set_font('Arial', '', 9)
        self.set_text_color(0, 0, 0)
        self.set_xy(20, self.get_y() + 2)
        self.multi_cell(175, 4, "* Implement structured fitness program to maintain peak physical condition\n* Develop leadership qualities through captaincy opportunities\n* Integrate video analysis sessions to improve tactical understanding", 0, 'L')
        
        self.ln(60)
        
        # Coaching signature section
        self.section_title("COACH SIGNATURE")
        
        self.set_fill_color(245, 245, 245)
        self.rounded_rect(10, self.get_y(), 190, 30, 3, 'F')
        
        self.set_font('Arial', '', 10)
        self.set_xy(15, self.get_y() + 5)
        self.cell(85, 8, "Coach Name: _____________________________", 0, 0, 'L')
        self.cell(85, 8, "Date: _________________________", 0, 1, 'L')
        
        self.set_xy(15, self.get_y() + 5)
        self.cell(180, 8, "Signature: _________________________________________________", 0, 1, 'L')
        


def generate_player_report(player_data, player_teams, player_games, player_metrics, 
                          player_evaluations, player_videos, player_documents):
    """Generate a PDF report for a player"""
    
    pdf = PlayerReportPDF()
    pdf.alias_nb_pages()
    
    if not os.path.exists(os.path.join(ASSETS_DIR, 'images')):
        os.makedirs(os.path.join(ASSETS_DIR, 'images'), exist_ok=True)
    
    pdf.add_page()
    pdf.add_player_header(player_data)
    pdf.add_player_profile(player_data)
    pdf.add_player_position_field(player_data['primary_position'])
    
    skills_data = {
        "Technical": np.random.randint(70, 98),
        "Physical": np.random.randint(70, 98),
        "Tactical": np.random.randint(70, 98),
        "Mental": np.random.randint(70, 98),
        "Attacking": np.random.randint(70, 98),
        "Defending": np.random.randint(70, 98),
    }
    
    pdf.add_player_skills_radar(skills_data)
    
    pdf.add_page()
    pdf.chapter_title("PERFORMANCE STATISTICS")
    
    performance_metrics = {
        "Games Played": 22,
        "Goals": 8,
        "Assists": 6,
        "Minutes": 1820,
        "Pass Accuracy": 87,
        "Tackles": 45
    }
    
    pdf.add_performance_metrics(performance_metrics)
    
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
    
    months = ["Jan", "Feb", "Mar", "Apr", "May"]
    performance_values = [65, 70, 68, 75, 82]
    
    progress_fig = create_progress_chart(months, performance_values, 
                                        "Performance Progress", "Performance Rating")
    pdf.add_plot(progress_fig)
    
    pdf.add_page()
    pdf.add_coach_assessment()
    
    pdf_output = pdf.output(dest='S').encode('latin1')
    buffer = BytesIO(pdf_output)
    return buffer