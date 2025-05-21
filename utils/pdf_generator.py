from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import numpy as np
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

class PlayerReportPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font('Montserrat', '', os.path.join(ASSETS_DIR, 'Montserrat-Regular.ttf'), uni=True)
        self.add_font('Montserrat', 'B', os.path.join(ASSETS_DIR, 'Montserrat-Bold.ttf'), uni=True)
        self.add_font('Montserrat', 'I', os.path.join(ASSETS_DIR, 'Montserrat-Italic.ttf'), uni=True)
        self.add_font('Montserrat', 'BI', os.path.join(ASSETS_DIR, 'Montserrat-BoldItalic.ttf'), uni=True)
        
    def header(self):
        # Logo
        try:
            self.image('assets/logo.png', 10, 8, 30)
        except:
            # If logo doesn't exist, just add text
            self.set_font('Montserrat', 'B', 16)
            self.set_text_color(29, 42, 87)  # Navy blue
            self.cell(0, 10, '360° SOCCER PLAYER REPORT', 0, 0, 'R')
            
        # Add a line
        self.line(10, 20, 200, 20)
        
        # Reset position
        self.ln(20)
    
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        
        # Add a line
        self.line(10, self.get_y(), 200, self.get_y())
        
        # Footer text
        self.set_font('Montserrat', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
        self.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d")}', 0, 0, 'R')
    
    def chapter_title(self, title):
        # Set font
        self.set_font('Montserrat', 'B', 16)
        self.set_fill_color(59, 125, 74)  # Green
        self.set_text_color(255, 255, 255)  # White
        
        # Add title
        self.cell(0, 10, title, 0, 1, 'L', 1)
        
        # Line break
        self.ln(4)
    
    def section_title(self, title):
        # Set font
        self.set_font('Montserrat', 'B', 14)
        self.set_text_color(29, 42, 87)  # Navy blue
        
        # Add title
        self.cell(0, 10, title, 0, 1, 'L')
        
        # Line break
        self.ln(2)
    
    def field_value(self, field, value, width_field=50, width_value=140):
        # Set font for field
        self.set_font('Montserrat', 'B', 10)
        self.set_text_color(59, 125, 74)  # Green
        
        # Add field
        self.cell(width_field, 8, field, 0, 0)
        
        # Set font for value
        self.set_font('Montserrat', '', 10)
        self.set_text_color(0, 0, 0)  # Black
        
        # Add value
        self.cell(width_value, 8, str(value), 0, 1)
    
    def add_info_table(self, data, title=None):
        if title:
            self.section_title(title)
        
        self.set_font('Montserrat', '', 10)
        line_height = 8
        col_width = 40
        
        # Table header
        self.set_font('Montserrat', 'B', 10)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        
        for header in data[0].keys():
            self.cell(col_width, line_height, str(header), 1, 0, 'C', 1)
        self.ln()
        
        # Table data
        self.set_font('Montserrat', '', 9)
        self.set_fill_color(255, 255, 255)
        
        for row in data:
            for key, value in row.items():
                self.cell(col_width, line_height, str(value), 1, 0, 'C')
            self.ln()
        
        self.ln(4)
    
    def add_plot(self, fig, width=190, height=100):
        """Add a matplotlib figure to the PDF"""
        # Save the figure to a BytesIO object
        img_bytes = BytesIO()
        fig.savefig(img_bytes, format='png', dpi=300, bbox_inches='tight')
        img_bytes.seek(0)
        
        # Add the image to the PDF
        self.image(img_bytes, x=10, w=width, h=height)
        self.ln(height + 10)  # Line break after image
        
        # Close figure to free memory
        plt.close(fig)


def generate_player_report(player_data, player_teams, player_games, player_metrics, 
                          player_evaluations, player_videos, player_documents):
    """Generate a PDF report for a player"""
    
    # Create FPDF object
    pdf = PlayerReportPDF()
    pdf.alias_nb_pages()
    
    # Ensure assets directory exists
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Create first page with player details
    pdf.add_page()
    
    # Report Title
    pdf.set_font('Montserrat', 'B', 20)
    pdf.set_text_color(29, 42, 87)  # Navy blue
    pdf.cell(0, 10, f"Player Report: {player_data['first_name']} {player_data['last_name']}", 0, 1, 'C')
    pdf.ln(5)
    
    # Player photo (if available)
    try:
        # Check if photo_url exists and is not empty
        if player_data.get('photo_url'):
            # Calculate position to center the image
            pdf.image(player_data['photo_url'], x=85, y=40, w=40, h=40)
    except:
        # If loading the image fails, use a placeholder or just skip
        pass
    
    pdf.ln(50)  # Space for the image
    
    # Player details in two columns
    pdf.chapter_title("Personal Information")
    
    col_width = 95  # Width for each column
    
    # First row
    pdf.set_font('Montserrat', 'B', 10)
    pdf.set_text_color(59, 125, 74)  # Green
    pdf.cell(col_width, 8, "Full Name", 0, 0)
    pdf.set_font('Montserrat', '', 10)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.cell(0, 8, f"{player_data['first_name']} {player_data['last_name']}", 0, 1)
    
    # Second row
    pdf.set_font('Montserrat', 'B', 10)
    pdf.set_text_color(59, 125, 74)  # Green
    pdf.cell(col_width, 8, "Date of Birth", 0, 0)
    pdf.set_font('Montserrat', '', 10)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.cell(0, 8, f"{player_data['birth_date']}", 0, 1)
    
    # More rows
    pdf.field_value("Nationality", player_data['nationality'])
    pdf.field_value("Position", f"{player_data['primary_position']} / {player_data['secondary_position']}")
    pdf.field_value("Jersey Number", player_data['number'])
    pdf.field_value("Dominant Foot", player_data['dominant_foot'])
    pdf.field_value("Height", f"{player_data['height']} cm")
    pdf.field_value("Education", player_data['education_level'])
    pdf.field_value("School", player_data['school_name'])
    
    # Add player notes if available
    if player_data.get('notes'):
        pdf.ln(5)
        pdf.section_title("Notes")
        pdf.set_font('Montserrat', 'I', 10)
        pdf.multi_cell(0, 8, player_data['notes'])
    
    # Add activity history if available
    if player_data.get('player_activity_history'):
        pdf.ln(5)
        pdf.section_title("Activity History")
        pdf.set_font('Montserrat', '', 10)
        pdf.multi_cell(0, 8, player_data['player_activity_history'])
    
    # Team history page
    if not player_teams.empty:
        pdf.add_page()
        pdf.chapter_title("Team History")
        
        # Create table data
        team_data = []
        for _, team in player_teams.iterrows():
            team_data.append({
                'Team': team['team_name'],
                'Start Date': team['start_date'],
                'End Date': team['end_date']
            })
        
        pdf.add_info_table(team_data)
        
        # Create team timeline visualization
        if len(team_data) > 0:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Convert data for plotting
            teams = player_teams['team_name'].tolist()
            start_dates = pd.to_datetime(player_teams['start_date'])
            end_dates = pd.to_datetime(player_teams['end_date'])
            
            # Plot horizontal bars for each team
            for i, (team, start, end) in enumerate(zip(teams, start_dates, end_dates)):
                ax.barh(i, (end - start).days, left=start, height=0.5, 
                       color=plt.cm.viridis(i / len(teams)), alpha=0.8)
                ax.text(start, i, team, va='center', ha='right', 
                       fontweight='bold', color='black', fontsize=8)
            
            ax.set_yticks([])
            ax.set_title('Team Timeline', fontsize=12, fontweight='bold')
            ax.grid(axis='x', linestyle='--', alpha=0.7)
            
            # Format x-axis as dates
            plt.gcf().autofmt_xdate()
            
            # Add the plot to the PDF
            pdf.add_plot(fig)
    
    # Game statistics page
    if not player_games.empty:
        pdf.add_page()
        pdf.chapter_title("Game Statistics")
        
        # Calculate statistics
        total_games = len(player_games)
        total_goals = player_games['goals'].sum()
        games_as_starter = player_games['starter'].sum()
        total_minutes = player_games['minutes_played'].sum()
        
        # Create summary
        pdf.section_title("Summary")
        pdf.field_value("Total Games", total_games)
        pdf.field_value("Goals Scored", total_goals)
        pdf.field_value("Games as Starter", games_as_starter)
        pdf.field_value("Total Minutes Played", total_minutes)
        pdf.field_value("Goals per Game", f"{total_goals/total_games:.2f}" if total_games > 0 else "0")
        pdf.field_value("Minutes per Game", f"{total_minutes/total_games:.2f}" if total_games > 0 else "0")
        
        # Create goals chart
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Convert match dates for plotting
        match_dates = pd.to_datetime(player_games['match_date'])
        
        # Sort data by date
        sorted_indices = match_dates.argsort()
        sorted_dates = match_dates.iloc[sorted_indices]
        sorted_goals = player_games['goals'].iloc[sorted_indices]
        
        # Plot goals
        ax.bar(sorted_dates, sorted_goals, color='#3B7D4A', alpha=0.8)
        ax.set_xlabel('Match Date')
        ax.set_ylabel('Goals')
        ax.set_title('Goals per Game', fontsize=12, fontweight='bold')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Format x-axis as dates
        plt.gcf().autofmt_xdate()
        
        # Add the plot to the PDF
        pdf.add_plot(fig)
        
        # Create minutes played chart
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Plot minutes played
        sorted_minutes = player_games['minutes_played'].iloc[sorted_indices]
        ax.plot(sorted_dates, sorted_minutes, marker='o', linestyle='-', color='#1A2A57')
        ax.set_xlabel('Match Date')
        ax.set_ylabel('Minutes')
        ax.set_title('Minutes Played per Game', fontsize=12, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Format x-axis as dates
        plt.gcf().autofmt_xdate()
        
        # Add the plot to the PDF
        pdf.add_plot(fig)
        
        # Create starter vs. substitute pie chart
        fig, ax = plt.subplots(figsize=(8, 8))
        
        starter_counts = player_games['starter'].value_counts()
        labels = ['Starter', 'Substitute']
        sizes = [starter_counts.get(True, 0), starter_counts.get(False, 0)]
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#3B7D4A', '#1A2A57'], 
              wedgeprops={'edgecolor': 'w', 'linewidth': 1})
        ax.set_title('Starter vs. Substitute', fontsize=12, fontweight='bold')
        
        # Add the plot to the PDF
        pdf.add_plot(fig, width=120, height=120)
        
        # Add detailed game statistics table
        pdf.ln(5)
        pdf.section_title("Game Details")
        
        # Create table data
        game_data = []
        for _, game in player_games.iterrows():
            game_data.append({
                'Date': game['match_date'],
                'Score': game['final_score'],
                'Starter': 'Yes' if game['starter'] else 'No',
                'Goals': game['goals'],
                'Minutes': game['minutes_played']
            })
        
        pdf.add_info_table(game_data)
    
    # Training metrics page
    if not player_metrics.empty:
        pdf.add_page()
        pdf.chapter_title("Training Metrics")
        
        # Group metrics by type
        metric_types = player_metrics['type'].unique()
        
        for metric_type in metric_types:
            pdf.section_title(f"{metric_type} Metrics")
            
            # Filter metrics by type
            filtered_metrics = player_metrics[player_metrics['type'] == metric_type]
            
            # Calculate average metrics
            avg_reaction_time = filtered_metrics['avg_reaction_time'].mean() if 'avg_reaction_time' in filtered_metrics.columns else None
            avg_hits = filtered_metrics['hits'].mean() if 'hits' in filtered_metrics.columns else None
            avg_misses = filtered_metrics['misses'].mean() if 'misses' in filtered_metrics.columns else None
            
            # Display averages
            if avg_reaction_time is not None:
                pdf.field_value("Average Reaction Time", f"{avg_reaction_time:.2f} seconds")
            
            if avg_hits is not None and avg_misses is not None:
                total_attempts = avg_hits + avg_misses
                accuracy = (avg_hits / total_attempts * 100) if total_attempts > 0 else 0
                pdf.field_value("Average Accuracy", f"{accuracy:.1f}%")
            
            # Create reaction time chart if available
            if 'avg_reaction_time' in filtered_metrics.columns:
                fig, ax = plt.subplots(figsize=(10, 5))
                
                # Convert dates for plotting
                training_dates = pd.to_datetime(filtered_metrics['training_date'])
                
                # Sort data by date
                sorted_indices = training_dates.argsort()
                sorted_dates = training_dates.iloc[sorted_indices]
                sorted_reaction_times = filtered_metrics['avg_reaction_time'].iloc[sorted_indices]
                
                # Plot reaction times
                ax.plot(sorted_dates, sorted_reaction_times, marker='o', linestyle='-', color='#D4AF37')
                ax.set_xlabel('Training Date')
                ax.set_ylabel('Reaction Time (s)')
                ax.set_title('Average Reaction Time', fontsize=12, fontweight='bold')
                ax.grid(True, linestyle='--', alpha=0.7)
                
                # Format x-axis as dates
                plt.gcf().autofmt_xdate()
                
                # Add the plot to the PDF
                pdf.add_plot(fig)
            
            # Create hits vs. misses chart if available
            if 'hits' in filtered_metrics.columns and 'misses' in filtered_metrics.columns:
                fig, ax = plt.subplots(figsize=(10, 5))
                
                # Convert dates for plotting
                training_dates = pd.to_datetime(filtered_metrics['training_date'])
                
                # Sort data by date
                sorted_indices = training_dates.argsort()
                sorted_dates = training_dates.iloc[sorted_indices]
                sorted_hits = filtered_metrics['hits'].iloc[sorted_indices]
                sorted_misses = filtered_metrics['misses'].iloc[sorted_indices]
                
                # Plot hits and misses
                ax.bar(sorted_dates, sorted_hits, color='#3B7D4A', label='Hits', alpha=0.8)
                ax.bar(sorted_dates, sorted_misses, bottom=sorted_hits, color='#D4AF37', 
                      label='Misses', alpha=0.8)
                ax.set_xlabel('Training Date')
                ax.set_ylabel('Count')
                ax.set_title('Training Accuracy', fontsize=12, fontweight='bold')
                ax.legend()
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                
                # Format x-axis as dates
                plt.gcf().autofmt_xdate()
                
                # Add the plot to the PDF
                pdf.add_plot(fig)
            
            # Show training details in a table
            if not filtered_metrics.empty:
                # Create table data
                metrics_data = []
                for _, metric in filtered_metrics.iterrows():
                    metrics_data.append({
                        'Date': metric['training_date'],
                        'Program': metric['program'],
                        'Level': metric['level'],
                        'Time': f"{metric['total_time']} sec",
                        'Goal': metric['goal']
                    })
                
                pdf.add_info_table(metrics_data, title="Training Sessions")
            
            pdf.ln(5)
    
    # Evaluations page
    if not player_evaluations.empty:
        pdf.add_page()
        pdf.chapter_title("Player Evaluations")
        
        # Group evaluations by category
        categories = player_evaluations['category'].unique()
        
        for category in categories:
            pdf.section_title(f"{category.title()} Evaluations")
            
            # Filter evaluations by category
            category_evals = player_evaluations[player_evaluations['category'] == category]
            
            # Create table data
            eval_data = []
            for _, eval_row in category_evals.iterrows():
                eval_data.append({
                    'Date': eval_row['evaluation_date'],
                    'Metric': eval_row['metric_name'],
                    'Value': eval_row['value'],
                    'Notes': eval_row['notes'][:20] + '...' if len(eval_row['notes']) > 20 else eval_row['notes']
                })
            
            pdf.add_info_table(eval_data)
    
    # Videos page
    if not player_videos.empty:
        pdf.add_page()
        pdf.chapter_title("Video Highlights")
        
        for _, video in player_videos.iterrows():
            pdf.section_title(video['description'][:50] + '...' if len(video['description']) > 50 else video['description'])
            pdf.field_value("URL", video['url'])
            pdf.field_value("Match Date", video['match_date'] if 'match_date' in video else 'N/A')
            pdf.ln(5)
    
    # Documents page
    if not player_documents.empty:
        pdf.add_page()
        pdf.chapter_title("Player Documents")
        
        # Group documents by status
        statuses = player_documents['status'].unique()
        
        for status in statuses:
            pdf.section_title(f"{status.title()} Documents")
            
            # Filter documents by status
            status_docs = player_documents[player_documents['status'] == status]
            
            # Create table data
            doc_data = []
            for _, doc in status_docs.iterrows():
                doc_data.append({
                    'Type': doc['document_type'],
                    'Date': doc['uploaded_at'],
                    'Description': doc['description'][:20] + '...' if len(doc['description']) > 20 else doc['description'],
                    'Status': doc['status']
                })
            
            pdf.add_info_table(doc_data)
    
    # Coaching notes and recommendations page
    pdf.add_page()
    pdf.chapter_title("Coaching Notes & Recommendations")
    
    # Create templates for coaches to fill in
    pdf.section_title("Strengths")
    pdf.set_font('Montserrat', '', 10)
    pdf.cell(0, 10, "___________________________________________________________________", 0, 1)
    pdf.cell(0, 10, "___________________________________________________________________", 0, 1)
    pdf.cell(0, 10, "___________________________________________________________________", 0, 1)
    
    pdf.ln(5)
    pdf.section_title("Areas for Improvement")
    pdf.set_font('Montserrat', '', 10)
    pdf.cell(0, 10, "___________________________________________________________________", 0, 1)
    pdf.cell(0, 10, "___________________________________________________________________", 0, 1)
    pdf.cell(0, 10, "___________________________________________________________________", 0, 1)
    
    pdf.ln(5)
    pdf.section_title("Development Plan")
    pdf.set_font('Montserrat', '', 10)
    pdf.cell(0, 10, "___________________________________________________________________", 0, 1)
    pdf.cell(0, 10, "___________________________________________________________________", 0, 1)
    pdf.cell(0, 10, "___________________________________________________________________", 0, 1)
    
    pdf.ln(5)
    pdf.section_title("Coach Signature")
    pdf.set_font('Montserrat', '', 10)
    pdf.cell(0, 10, "Name: _________________________ Date: _________________________", 0, 1)
    pdf.cell(0, 10, "Signature: _________________________________________________", 0, 1)
    
    # Save the PDF
    pdf_buffer = BytesIO()
    pdf_bytes = pdf.output(dest="S").encode("latin1")  # FPDF genera str con codificación latin1
    pdf_buffer = BytesIO(pdf_bytes)
    return pdf_buffer

def create_soccer_field_position_image(position):
    """Create an image of a soccer field with the player's position highlighted"""
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Draw soccer field
    # Field dimensions (in yards)
    field_length = 120
    field_width = 80
    
    # Draw the field outline
    plt.plot([0, 0, field_length, field_length, 0], [0, field_width, field_width, 0, 0], 'g-', lw=2)
    
    # Draw the center line and circle
    plt.plot([field_length/2, field_length/2], [0, field_width], 'w-', lw=2)
    center_circle = plt.Circle((field_length/2, field_width/2), 10, fill=False, color='w', lw=2)
    ax.add_artist(center_circle)
    
    # Draw the penalty boxes
    # Left penalty box
    plt.plot([0, 18, 18, 0], [field_width/2 - 22, field_width/2 - 22, field_width/2 + 22, field_width/2 + 22], 'w-', lw=2)
    # Right penalty box
    plt.plot([field_length, field_length - 18, field_length - 18, field_length], 
           [field_width/2 - 22, field_width/2 - 22, field_width/2 + 22, field_width/2 + 22], 'w-', lw=2)
    
    # Draw the goal boxes
    # Left goal box
    plt.plot([0, 6, 6, 0], [field_width/2 - 10, field_width/2 - 10, field_width/2 + 10, field_width/2 + 10], 'w-', lw=2)
    # Right goal box
    plt.plot([field_length, field_length - 6, field_length - 6, field_length], 
           [field_width/2 - 10, field_width/2 - 10, field_width/2 + 10, field_width/2 + 10], 'w-', lw=2)
    
    # Draw the goals
    # Left goal
    plt.plot([-2, 0, 0, -2], [field_width/2 - 6, field_width/2 - 6, field_width/2 + 6, field_width/2 + 6], 'w-', lw=2)
    # Right goal
    plt.plot([field_length + 2, field_length, field_length, field_length + 2], 
           [field_width/2 - 6, field_width/2 - 6, field_width/2 + 6, field_width/2 + 6], 'w-', lw=2)
    
    # Set field color
    ax.set_facecolor('#1A8022')
    
    # Determine position coordinates
    position_coords = {
        'Goalkeeper': (field_length - 3, field_width / 2),
        'Center Back': (field_length - 20, field_width / 2),
        'Left Back': (field_length - 20, field_width / 4),
        'Right Back': (field_length - 20, 3 * field_width / 4),
        'Defensive Midfielder': (field_length - 40, field_width / 2),
        'Midfielder': (field_length / 2, field_width / 2),
        'Left Wing': (field_length / 2, field_width / 4),
        'Right Wing': (field_length / 2, 3 * field_width / 4),
        'Forward': (20, field_width / 2)
    }
    
    # Highlight player's position
    if position in position_coords:
        x, y = position_coords[position]
        plt.scatter(x, y, s=300, color='red', edgecolor='white', linewidth=2, zorder=5)
        plt.annotate(position, (x, y), xytext=(0, 7), textcoords='offset points', 
                    ha='center', va='center', color='white', fontsize=12, fontweight='bold')
    
    # Remove axes and set limits
    plt.axis('off')
    plt.xlim(-5, field_length + 5)
    plt.ylim(-5, field_width + 5)
    
    # Return the figure
    return fig