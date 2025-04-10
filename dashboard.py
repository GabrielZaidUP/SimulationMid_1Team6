"""
Digital Watch Factory Dashboard - Visualization Tool for Factory Simulation Data.

This module provides a comprehensive dashboard for analyzing and visualizing
simulation data from a digital watch manufacturing process. It displays key
performance indicators, station metrics, material usage, and correlation analyses
to help factory managers make informed decisions.

The dashboard features multiple visualization tabs, interactive filtering, and
data-driven recommendations based on the factory's performance metrics.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import numpy as np

class FactoryDashboard:
    """
    A dashboard application for visualizing digital watch factory simulation data.
    
    This class creates an interactive dashboard with scrollable content that displays
    production metrics, station performance, material usage, and correlation analyses.
    It provides filtering capabilities for time granularity and station selection.
    
    Attributes:
        root (tk.Tk): The root Tkinter window.
        data_dir (str): Directory containing simulation CSV files.
        canvas (tk.Canvas): Canvas for scrollable content.
        scrollable_frame (ttk.Frame): Frame that holds dashboard content.
        filter_frame (ttk.LabelFrame): Frame containing filter controls.
        time_var (tk.StringVar): Selected time granularity.
        station_var (tk.StringVar): Selected station filter.
        production_data (pd.DataFrame): Production metrics data.
        station_data (pd.DataFrame): Station performance data.
        material_data (pd.DataFrame): Material usage data.
    """
    
    def __init__(self, root):
        """
        Initialize the dashboard application.
        
        Args:
            root (tk.Tk): The root Tkinter window.
        """
        # Initialize the dashboard window
        self.root = root
        self.root.title("Digital Watch Factory Dashboard")
        self.root.geometry("900x700")
        
        # Data directory
        self.data_dir = "dashboard_data"
        
        # Create main container with scrolling capability
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill='both', expand=True)
        
        # Add a canvas for scrolling
        self.canvas = tk.Canvas(self.main_container)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Create filter panel (fixed at top)
        self.create_filters()
        
        # Load data and create the dashboard
        self.load_data()
        
    def _on_mousewheel(self, event):
        """
        Handle mouse wheel scrolling events.
        
        Args:
            event: The mouse wheel event.
        """
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_filters(self):
        """
        Create filter controls at the top of the dashboard.
        
        Creates comboboxes for time period and station selection, along with buttons
        for applying filters and refreshing data.
        """
        self.filter_frame = ttk.LabelFrame(self.scrollable_frame, text="Dashboard Controls")
        self.filter_frame.pack(fill='x', padx=10, pady=5)
        
        # Time granularity options
        time_periods = ['Daily', 'Weekly', 'Monthly', 'Quarterly']
        self.time_var = tk.StringVar(value='Daily')
        
        # Create filter widgets
        ttk.Label(self.filter_frame, text='Time Period:').grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(self.filter_frame, values=time_periods, textvariable=self.time_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        # Station filter if we have stations
        self.station_var = tk.StringVar(value='All Stations')
        ttk.Label(self.filter_frame, text='Station:').grid(row=0, column=2, padx=5, pady=5)
        self.station_combo = ttk.Combobox(self.filter_frame, textvariable=self.station_var, width=15)
        self.station_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Apply button
        ttk.Button(self.filter_frame, text="Apply Filters", command=self.update_dashboard).grid(row=0, column=4, padx=10, pady=5)
        ttk.Button(self.filter_frame, text="Refresh Data", command=self.load_data).grid(row=0, column=5, padx=10, pady=5)
    
    def load_data(self):
        """
        Load simulation data from CSV files.
        
        Reads production, station, and material data from CSV files in the data_dir.
        Adds time granularity columns to production data for filtering.
        Updates station filter dropdown with available stations.
        Creates the dashboard visualizations if data is successfully loaded.
        
        Returns:
            bool: True if data was successfully loaded, False otherwise.
        """
        try:
            if not os.path.exists(self.data_dir):
                messagebox.showwarning("Warning", "Data directory not found. Please run simulation first.")
                return False
                
            # Load data files
            self.production_data = pd.read_csv(os.path.join(self.data_dir, "production_data.csv"), parse_dates=['date'])
            self.station_data = pd.read_csv(os.path.join(self.data_dir, "station_data.csv"))
            self.material_data = pd.read_csv(os.path.join(self.data_dir, "material_data.csv"))
            
            # Add time granularity columns
            self.production_data['week'] = pd.to_datetime(self.production_data['date']).dt.to_period('W').dt.start_time
            self.production_data['month'] = pd.to_datetime(self.production_data['date']).dt.to_period('M').dt.start_time
            self.production_data['quarter'] = pd.to_datetime(self.production_data['date']).dt.to_period('Q').dt.start_time
            
            # Update station filter with available stations
            if 'station_name' in self.station_data.columns:
                stations = ['All Stations'] + sorted(self.station_data['station_name'].unique().tolist())
                self.station_combo['values'] = stations
            
            # Create dashboard
            self.create_dashboard()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            return False
    
    def update_dashboard(self):
        """
        Update dashboard visualizations based on current filter settings.
        
        Clears existing widgets (except filter frame) and recreates the dashboard
        with the current time period and station filter settings.
        """
        # Clear existing widgets except the filter frame
        for widget in self.scrollable_frame.winfo_children():
            if widget != self.filter_frame:
                widget.destroy()
        
        # Recreate dashboard
        self.create_dashboard()
    
    def create_dashboard(self):
        """
        Create the main dashboard layout and visualizations.
        
        Populates the dashboard with executive summary, station analysis,
        material analysis, and correlation analysis sections.
        Displays a message if no data is available.
        """
        if not hasattr(self, 'production_data'):
            ttk.Label(self.scrollable_frame, text="No data available. Run simulation first.", 
                     font=('Arial', 12, 'bold')).pack(pady=50)
            return
        
        # 1. Executive Summary (Company Level)
        self.create_executive_summary()
        
        # 2. Station Analysis (Workstation Level)
        self.create_station_analysis()
        
        # 3. Material & Supply Chain
        self.create_material_analysis()
        
        # 4. Advanced Analysis with Correlations
        self.create_correlation_analysis()
    
    def create_executive_summary(self):
        """
        Create company-level executive summary section.
        
        Displays key performance indicators, production trend chart, and
        data-driven insights for factory management.
        """
        # Create summary frame
        summary_frame = ttk.LabelFrame(self.scrollable_frame, text="Executive Summary")
        summary_frame.pack(fill='x', padx=10, pady=5)
        
        # Calculate KPIs
        total_production = self.production_data['production'].sum()
        total_faulty = self.production_data['faulty'].sum() 
        fault_rate = (total_faulty / total_production) if total_production > 0 else 0
        avg_production_time = self.production_data['avg_production_time'].mean() if 'avg_production_time' in self.production_data.columns else 0
        
        # Create KPI display
        kpi_frame = ttk.Frame(summary_frame)
        kpi_frame.pack(fill='x', padx=5, pady=5)
        
        # KPI grid
        ttk.Label(kpi_frame, text="Total Production:", font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=5, sticky='e')
        ttk.Label(kpi_frame, text=f"{total_production:,.0f} units", font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        ttk.Label(kpi_frame, text="Fault Rate:", font=('Arial', 10)).grid(row=0, column=2, padx=10, pady=5, sticky='e')
        ttk.Label(kpi_frame, text=f"{fault_rate:.1%}", font=('Arial', 10, 'bold')).grid(row=0, column=3, padx=10, pady=5, sticky='w')
        
        ttk.Label(kpi_frame, text="Avg Production Time:", font=('Arial', 10)).grid(row=0, column=4, padx=10, pady=5, sticky='e')
        ttk.Label(kpi_frame, text=f"{avg_production_time:.2f} units", font=('Arial', 10, 'bold')).grid(row=0, column=5, padx=10, pady=5, sticky='w')
        
        # Create production trend chart
        self.create_production_trend(summary_frame)
        
        # Add key insights based on data
        insights_frame = ttk.LabelFrame(summary_frame, text="Key Insights")
        insights_frame.pack(fill='x', padx=5, pady=5)
        
        # Find bottleneck station
        if not self.station_data.empty and 'occupancy_rate' in self.station_data.columns:
            bottleneck = self.station_data.loc[self.station_data['occupancy_rate'].idxmax()]
            bottleneck_name = bottleneck['station_name'] if 'station_name' in bottleneck else f"Station {bottleneck['station_id']}"
            bottleneck_text = f"• Bottleneck identified at {bottleneck_name} (Occupancy: {bottleneck['occupancy_rate']:.1%})"
        else:
            bottleneck_text = "• No clear bottleneck identified with available data"
        
        # Create insights text
        status_text = "✓ Production is running smoothly" if fault_rate < 0.05 else "⚠ High fault rate detected"
        ttk.Label(insights_frame, text=f"• {status_text} ({fault_rate:.1%})", font=('Arial', 10)).pack(anchor='w', padx=20, pady=2)
        ttk.Label(insights_frame, text=bottleneck_text, font=('Arial', 10)).pack(anchor='w', padx=20, pady=2)
        
        if not self.station_data.empty and 'downtime' in self.station_data.columns:
            high_down = self.station_data.loc[self.station_data['downtime'].idxmax()]
            high_down_name = high_down['station_name'] if 'station_name' in high_down else f"Station {high_down['station_id']}"
            ttk.Label(insights_frame, text=f"• Maintenance needed at {high_down_name} (Downtime: {high_down['downtime']:.1f} units)", 
                     font=('Arial', 10)).pack(anchor='w', padx=20, pady=2)
    
    def create_production_trend(self, parent):
        """
        Create production trend chart with fault rate overlay.
        
        Args:
            parent: Parent frame to contain the chart.
        """
        # Get time granularity
        time_map = {'Daily': 'date', 'Weekly': 'week', 'Monthly': 'month', 'Quarterly': 'quarter'}
        time_col = time_map.get(self.time_var.get(), 'date')
        
        # Aggregate data
        grouped = self.production_data.groupby(time_col).agg({
            'production': 'sum',
            'faulty': 'sum'
        }).reset_index()
        
        # Calculate fault rate
        grouped['fault_rate'] = grouped['faulty'] / grouped['production']
        
        # Create figure with dual y-axis
        fig, ax1 = plt.subplots(figsize=(8, 4))
        
        # Production line
        color1 = '#1f77b4'  # Blue
        ax1.set_xlabel('Time Period')
        ax1.set_ylabel('Production', color=color1)
        ax1.plot(grouped[time_col], grouped['production'], color=color1, marker='o')
        ax1.tick_params(axis='y', labelcolor=color1)
        
        # Fault rate line
        color2 = '#d62728'  # Red
        ax2 = ax1.twinx()
        ax2.set_ylabel('Fault Rate', color=color2)
        ax2.plot(grouped[time_col], grouped['fault_rate'], color=color2, marker='x')
        ax2.tick_params(axis='y', labelcolor=color2)
        ax2.set_ylim(0, max(0.2, grouped['fault_rate'].max() * 1.2))
        ax2.axhline(y=0.05, color='red', linestyle='--', alpha=0.5)  # Target line
        
        # Format y-axis as percentage
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
        
        # Set title and layout
        fig.suptitle(f'Production Trend ({self.time_var.get()})', fontsize=12)
        plt.xticks(rotation=45)
        fig.tight_layout()
        
        # Create chart frame
        chart_frame = ttk.Frame(parent)
        chart_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Render chart
        self.render_chart(fig, chart_frame)
    
    def create_station_analysis(self):
        """
        Create workstation-level analysis section.
        
        Displays station metrics, bottleneck analysis, and station-specific 
        recommendations using a heatmap visualization.
        """
        if self.station_data.empty:
            return
            
        # Create station frame
        station_frame = ttk.LabelFrame(self.scrollable_frame, text="Station Analysis")
        station_frame.pack(fill='x', padx=10, pady=5)
        
        # Add station metrics (occupancy and downtime)
        if 'occupancy_rate' in self.station_data.columns and 'downtime' in self.station_data.columns:
            # Calculate bottleneck score
            max_downtime = self.station_data['downtime'].max() if self.station_data['downtime'].max() > 0 else 1
            self.station_data['normalized_downtime'] = self.station_data['downtime'] / max_downtime
            self.station_data['bottleneck_score'] = self.station_data['occupancy_rate'] * 0.6 + self.station_data['normalized_downtime'] * 0.4
            
            # Create visualization container
            chart_container = ttk.Frame(station_frame)
            chart_container.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Create the station heatmap - shows multiple metrics at once
            self.create_station_heatmap(chart_container)
            
            # Add recommendations
            rec_frame = ttk.LabelFrame(station_frame, text="Station Recommendations")
            rec_frame.pack(fill='x', padx=5, pady=5)
            
            # Find problem stations
            high_occ = self.station_data.loc[self.station_data['occupancy_rate'].idxmax()]
            high_occ_name = high_occ['station_name'] if 'station_name' in high_occ else f"Station {high_occ['station_id']}"
            
            high_down = self.station_data.loc[self.station_data['downtime'].idxmax()]
            high_down_name = high_down['station_name'] if 'station_name' in high_down else f"Station {high_down['station_id']}"
            
            # Add recommendations
            ttk.Label(rec_frame, text=f"• Increase capacity at {high_occ_name} (Occupancy: {high_occ['occupancy_rate']:.1%})", 
                    font=('Arial', 9)).pack(anchor='w', padx=20, pady=2)
            ttk.Label(rec_frame, text=f"• Maintenance needed at {high_down_name} (Downtime: {high_down['downtime']:.1f} units)", 
                    font=('Arial', 9)).pack(anchor='w', padx=20, pady=2)
            
            if high_occ_name == high_down_name:
                ttk.Label(rec_frame, text=f"• Critical intervention required at {high_occ_name}", 
                        font=('Arial', 9, 'bold')).pack(anchor='w', padx=20, pady=2)
        else:
            ttk.Label(station_frame, text="Insufficient data for station analysis", 
                    font=('Arial', 10)).pack(pady=20)
    
    def create_station_heatmap(self, parent):
        """
        Create heatmap showing station performance metrics.
        
        Args:
            parent: Parent frame to contain the heatmap.
        """
        # Define metrics to show
        metrics = ['occupancy_rate', 'downtime', 'bottleneck_score'] 
        if not all(metric in self.station_data.columns for metric in metrics):
            ttk.Label(parent, text="Insufficient metrics for heatmap visualization", 
                    font=('Arial', 10)).pack(pady=20)
            return
            
        # Get stations based on filter
        x_col = 'station_name' if 'station_name' in self.station_data.columns else 'station_id'
        
        # Apply station filter if not "All Stations"
        df = self.station_data
        if self.station_var.get() != 'All Stations' and self.station_var.get() in df[x_col].values:
            df = df[df[x_col] == self.station_var.get()]
        
        # Create heatmap data
        heatmap_data = df.set_index(x_col)[metrics].copy()
        
        # Normalize data for better visualization
        for col in heatmap_data.columns:
            if heatmap_data[col].max() > 0:
                heatmap_data[col] = heatmap_data[col] / heatmap_data[col].max()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Create heatmap
        sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt=".2f", ax=ax)
        
        # Set labels
        ax.set_title('Station Performance Heatmap', fontsize=12)
        ax.set_ylabel('Station')
        ax.set_xlabel('Metric (Normalized)')
        
        fig.tight_layout()
        
        # Render chart
        self.render_chart(fig, parent)
    
    def create_material_analysis(self):
        """
        Create material and supply chain analysis section.
        
        Displays material usage, supply chain risk assessment, and provides
        recommendations for material management.
        """
        if self.material_data.empty:
            return
            
        # Create material frame
        material_frame = ttk.LabelFrame(self.scrollable_frame, text="Supply Chain Analysis")
        material_frame.pack(fill='x', padx=10, pady=5)
        
        # Create usage and risk visualizations
        if all(col in self.material_data.columns for col in ['avg_usage', 'avg_resupply']):
            # Calculate risk score
            self.material_data['risk_score'] = self.material_data['avg_usage'] / (self.material_data['avg_resupply'] + 0.1)
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Get material names
            x_col = 'display_name' if 'display_name' in self.material_data.columns else 'material'
            
            # Sort by risk
            df_sorted = self.material_data.sort_values('risk_score', ascending=False)
            
            # Create bar chart with color gradient
            bars = ax.bar(
                df_sorted[x_col], 
                df_sorted['risk_score'],
                color=plt.cm.YlOrRd(df_sorted['risk_score']/df_sorted['risk_score'].max() if df_sorted['risk_score'].max() > 0 else 0)
            )
            
            # Add labels
            ax.set_title('Supply Chain Risk Assessment', fontsize=12)
            ax.set_xlabel('Material')
            ax.set_ylabel('Risk Score (higher = more risk)')
            
            # Add bar labels
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width()/2.,
                    height + 0.01,
                    f'{height:.1f}',
                    ha='center', va='bottom'
                )
            
            # Rotate x labels if needed
            if len(df_sorted) > 4:
                plt.xticks(rotation=45, ha='right')
                
            fig.tight_layout()
            
            # Render chart
            self.render_chart(fig, material_frame)
            
            # Add recommendations for top risk materials
            rec_frame = ttk.Frame(material_frame)
            rec_frame.pack(fill='x', padx=10, pady=5)
            
            ttk.Label(rec_frame, text="Recommendations:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=5)
            
            for _, mat in df_sorted.head(2).iterrows():
                name = mat['display_name'] if 'display_name' in mat else mat['material']
                ttk.Label(rec_frame, text=f"• Increase order quantity for {name} (Risk: {mat['risk_score']:.1f})", 
                        font=('Arial', 9)).pack(anchor='w', padx=20, pady=2)
        else:
            ttk.Label(material_frame, text="Insufficient data for supply chain analysis", 
                    font=('Arial', 10)).pack(pady=20)
    
    def create_correlation_analysis(self):
        """
        Create correlation analysis between key metrics.
        
        Displays scatter plot with trend line showing relationship between
        station occupancy and downtime, with statistical interpretation.
        """
        # Create correlation frame
        corr_frame = ttk.LabelFrame(self.scrollable_frame, text="Advanced Analysis")
        corr_frame.pack(fill='x', padx=10, pady=5)
        
        # Create correlation if we have station data
        if not self.station_data.empty and 'occupancy_rate' in self.station_data.columns and 'downtime' in self.station_data.columns:
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 4))
            
            # Create scatter plot with station metrics
            sns.scatterplot(
                data=self.station_data,
                x='occupancy_rate',
                y='downtime',
                s=100,  # Point size
                ax=ax
            )
            
            # Add station labels to points
            label_col = 'station_name' if 'station_name' in self.station_data.columns else 'station_id'
            for _, point in self.station_data.iterrows():
                ax.text(
                    point['occupancy_rate'] + 0.01, 
                    point['downtime'] + 0.1,
                    point[label_col],
                    fontsize=9
                )
            
            # Add trend line
            sns.regplot(
                x='occupancy_rate',
                y='downtime',
                data=self.station_data,
                scatter=False,
                ax=ax,
                line_kws={"color":"red","alpha":0.7,"lw":2}
            )
            
            # Add labels
            ax.set_title('Correlation: Station Occupancy vs Downtime', fontsize=12)
            ax.set_xlabel('Occupancy Rate')
            ax.set_ylabel('Downtime Units')
            
            # Format x-axis as percentage
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
            
            fig.tight_layout()
            
            # Render chart
            self.render_chart(fig, corr_frame)
            
            # Calculate correlation
            correlation = self.station_data['occupancy_rate'].corr(self.station_data['downtime'])
            
            # Add interpretation
            ttk.Label(corr_frame, text=f"Correlation coefficient: {correlation:.2f}", 
                    font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)
            
            # Interpret correlation
            if abs(correlation) < 0.3:
                interpretation = "Weak or no relationship between occupancy and downtime."
            elif 0.3 <= abs(correlation) < 0.7:
                interpretation = "Moderate relationship between occupancy and downtime."
            else:
                interpretation = "Strong relationship between occupancy and downtime."
                
            if correlation > 0:
                conclusion = "Stations with higher occupancy tend to have more downtime."
            else:
                conclusion = "Stations with higher occupancy tend to have less downtime."
                
            ttk.Label(corr_frame, text=interpretation, font=('Arial', 9)).pack(anchor='w', padx=20, pady=2)
            ttk.Label(corr_frame, text=conclusion, font=('Arial', 9)).pack(anchor='w', padx=20, pady=2)
        else:
            ttk.Label(corr_frame, text="Insufficient data for correlation analysis", 
                    font=('Arial', 10)).pack(pady=20)
    
    def render_chart(self, fig, parent):
        """
        Render matplotlib figure in tkinter container.
        
        Args:
            fig (matplotlib.figure.Figure): The figure to render.
            parent: Parent frame to contain the chart.
        """
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        # Close the figure to prevent memory leaks
        plt.close(fig)


if __name__ == '__main__':
    root = tk.Tk()
    app = FactoryDashboard(root)
    root.mainloop()