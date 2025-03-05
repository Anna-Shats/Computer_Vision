"""
Attention analytics module for processing and visualizing eye-tracking data.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AttentionAnalytics:
    """
    Class for analyzing eye-tracking attention data from retail shelves.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the analytics module.
        
        Args:
            data_dir: Directory containing session data files
        """
        self.data_dir = data_dir
        self.products = []
        self.attention_history = []
        self.metrics = {}
        self.heatmap = None
        
        if data_dir and os.path.exists(data_dir):
            self.load_session_data(data_dir)
            
        logger.info("Attention analytics initialized")
        
    def load_session_data(self, session_dir: str) -> bool:
        """
        Load session data from files.
        
        Args:
            session_dir: Directory containing session data files
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load products data
            products_path = os.path.join(session_dir, "products.json")
            if os.path.exists(products_path):
                with open(products_path, 'r') as f:
                    self.products = json.load(f)
                    
            # Load attention history
            history_path = os.path.join(session_dir, "attention_history.json")
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    self.attention_history = json.load(f)
                    
            # Load metrics
            metrics_path = os.path.join(session_dir, "metrics.json")
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.metrics = json.load(f)
                    
            # Load heatmap
            heatmap_path = os.path.join(session_dir, "heatmap.npy")
            if os.path.exists(heatmap_path):
                self.heatmap = np.load(heatmap_path)
                
            logger.info(f"Loaded session data from {session_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading session data: {e}")
            return False
            
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert attention history to pandas DataFrame for analysis.
        
        Returns:
            DataFrame containing attention data
        """
        if not self.attention_history:
            return pd.DataFrame()
            
        # Convert to pandas DataFrame
        df = pd.DataFrame(self.attention_history)
        
        # Convert timestamps to datetime
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Add derived columns
        df['duration_ms'] = df['duration'] * 1000
        
        return df
        
    def generate_product_attention_chart(self, top_n: int = 10, 
                                        save_path: Optional[str] = None,
                                        show_fig: bool = True) -> plt.Figure:
        """
        Generate a bar chart of product attention times.
        
        Args:
            top_n: Number of top products to include
            save_path: Path to save the chart
            show_fig: Whether to show the figure
            
        Returns:
            Matplotlib figure
        """
        # Sort products by attention time
        if not self.metrics or "products_by_attention_time" not in self.metrics:
            logger.error("No metrics data available")
            return None
            
        products = self.metrics["products_by_attention_time"][:top_n]
        
        # Prepare data
        names = [p["name"] for p in products]
        times = [p["total_attention_time"] for p in products]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot data
        bars = ax.barh(names, times, color='skyblue')
        
        # Add values to bars
        for i, v in enumerate(times):
            ax.text(v + 0.1, i, f"{v:.1f}s", va='center')
            
        # Add labels and title
        ax.set_xlabel('Attention Time (seconds)')
        ax.set_ylabel('Product')
        ax.set_title('Product Attention Analysis')
        
        # Add grid
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Tight layout
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Saved product attention chart to {save_path}")
            
        # Show if requested
        if show_fig:
            plt.show()
        
        return fig
        
    def generate_attention_timeline(self, 
                                  bin_seconds: int = 30, 
                                  save_path: Optional[str] = None,
                                  show_fig: bool = True) -> plt.Figure:
        """
        Generate a timeline visualization of attention over time.
        
        Args:
            bin_seconds: Time bin size in seconds
            save_path: Path to save the chart
            show_fig: Whether to show the figure
            
        Returns:
            Matplotlib figure
        """
        # Get data as DataFrame
        df = self.to_dataframe()
        
        if df.empty:
            logger.error("No attention data available")
            return None
            
        # Group by time bins and product
        df['time_bin'] = pd.to_datetime(
            (df['timestamp'] // bin_seconds) * bin_seconds, 
            unit='s'
        )
        
        # Sum durations by product and time bin
        timeline_data = df.groupby(['time_bin', 'product_name'])['duration'].sum().reset_index()
        
        # Pivot for plotting
        pivot_data = timeline_data.pivot(
            index='time_bin', 
            columns='product_name', 
            values='duration'
        ).fillna(0)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot data
        pivot_data.plot(kind='area', stacked=True, ax=ax, alpha=0.7)
        
        # Add labels and title
        ax.set_xlabel('Time')
        ax.set_ylabel('Attention Duration (seconds)')
        ax.set_title(f'Attention Timeline (Bins: {bin_seconds}s)')
        
        # Add grid
        ax.grid(linestyle='--', alpha=0.7)
        
        # Add legend
        ax.legend(title='Product', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Tight layout
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Saved attention timeline to {save_path}")
            
        # Show if requested
        if show_fig:
            plt.show()
        
        return fig
        
    def generate_category_breakdown(self, 
                                  save_path: Optional[str] = None,
                                  show_fig: bool = True) -> plt.Figure:
        """
        Generate a pie chart of attention by product category.
        
        Args:
            save_path: Path to save the chart
            show_fig: Whether to show the figure
            
        Returns:
            Matplotlib figure
        """
        if not self.products:
            logger.error("No product data available")
            return None
            
        # Group by category
        category_data = {}
        
        for product in self.products:
            category = product.get("category", "Unknown")
            attention_time = product.get("total_attention_time", 0)
            
            if category in category_data:
                category_data[category] += attention_time
            else:
                category_data[category] = attention_time
                
        # Prepare data
        categories = list(category_data.keys())
        attention_times = list(category_data.values())
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot data
        wedges, texts, autotexts = ax.pie(
            attention_times, 
            labels=None, 
            autopct='%1.1f%%',
            startangle=90,
            shadow=False,
            wedgeprops={'edgecolor': 'w', 'linewidth': 1}
        )
        
        # Equal aspect ratio ensures the pie chart is circular
        ax.axis('equal')
        
        # Add legend
        ax.legend(
            wedges, 
            categories, 
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
        
        # Add title
        ax.set_title('Attention by Product Category')
        
        # Tight layout
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Saved category breakdown to {save_path}")
            
        # Show if requested
        if show_fig:
            plt.show()
        
        return fig
        
    def generate_heatmap_visualization(self, 
                                     save_path: Optional[str] = None,
                                     show_fig: bool = True) -> plt.Figure:
        """
        Generate a heatmap visualization of attention.
        
        Args:
            save_path: Path to save the chart
            show_fig: Whether to show the figure
            
        Returns:
            Matplotlib figure
        """
        if self.heatmap is None or np.all(self.heatmap == 0):
            logger.error("No heatmap data available")
            return None
            
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Apply Gaussian smoothing for better visualization
        from scipy.ndimage import gaussian_filter
        smoothed_heatmap = gaussian_filter(self.heatmap, sigma=10)
        
        # Plot heatmap
        im = ax.imshow(
            smoothed_heatmap, 
            cmap='jet', 
            interpolation='bilinear',
            origin='upper'
        )
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Attention Intensity')
        
        # Remove axis ticks
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Add title
        ax.set_title('Attention Heatmap')
        
        # Tight layout
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Saved heatmap visualization to {save_path}")
            
        # Show if requested
        if show_fig:
            plt.show()
        
        return fig
        
    def export_analytics_report(self, output_dir: str) -> str:
        """
        Generate a comprehensive analytics report with all charts.
        
        Args:
            output_dir: Directory to save the report
            
        Returns:
            Path to the report directory
        """
        try:
            # Create report directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = os.path.join(output_dir, f"report_{timestamp}")
            os.makedirs(report_dir, exist_ok=True)
            
            # Generate charts
            self.generate_product_attention_chart(
                save_path=os.path.join(report_dir, "product_attention.png"),
                show_fig=False
            )
            
            self.generate_attention_timeline(
                save_path=os.path.join(report_dir, "attention_timeline.png"),
                show_fig=False
            )
            
            self.generate_category_breakdown(
                save_path=os.path.join(report_dir, "category_breakdown.png"),
                show_fig=False
            )
            
            self.generate_heatmap_visualization(
                save_path=os.path.join(report_dir, "heatmap.png"),
                show_fig=False
            )
            
            # Export metrics as JSON
            metrics_path = os.path.join(report_dir, "metrics.json")
            with open(metrics_path, 'w') as f:
                json.dump(self.metrics, f, indent=4)
            
            # Create HTML report
            html_report = self._generate_html_report(report_dir)
            
            logger.info(f"Analytics report exported to {report_dir}")
            return report_dir
            
        except Exception as e:
            logger.error(f"Error exporting analytics report: {e}")
            return ""
            
    def _generate_html_report(self, report_dir: str) -> str:
        """
        Generate an HTML report summarizing the analytics.
        
        Args:
            report_dir: Directory containing report files
            
        Returns:
            Path to the HTML report file
        """
        try:
            # Define HTML template
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Retail Shelf Attention Analysis Report</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        color: #333;
                    }
                    .header {
                        background-color: #f5f5f5;
                        padding: 20px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }
                    .section {
                        margin-bottom: 30px;
                    }
                    .chart-container {
                        text-align: center;
                        margin: 20px 0;
                    }
                    .chart {
                        max-width: 100%;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    th, td {
                        padding: 10px;
                        border: 1px solid #ddd;
                        text-align: left;
                    }
                    th {
                        background-color: #f5f5f5;
                    }
                    .highlight {
                        background-color: #FFFFE0;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Retail Shelf Attention Analysis Report</h1>
                    <p>Generated on: {date}</p>
                    <p>Session Duration: {session_duration}</p>
                </div>
                
                <div class="section">
                    <h2>Key Findings</h2>
                    <ul>
                        <li>Total products analyzed: {product_count}</li>
                        <li>Total attention time: {total_attention:.2f} seconds</li>
                        <li>Products receiving no attention: {ignored_count} ({ignored_percentage:.1f}%)</li>
                        <li>Most viewed product: {top_product_name} ({top_product_views} views)</li>
                        <li>Product with longest attention: {longest_attention_product} ({longest_attention:.2f} seconds)</li>
                    </ul>
                </div>
                
                <div class="section">
                    <h2>Product Attention Analysis</h2>
                    <div class="chart-container">
                        <img class="chart" src="product_attention.png" alt="Product Attention Chart">
                    </div>
                    
                    <h3>Top 5 Products by Attention Time</h3>
                    <table>
                        <tr>
                            <th>Rank</th>
                            <th>Product</th>
                            <th>Attention Time (s)</th>
                            <th>View Count</th>
                            <th>Average Time per View (s)</th>
                        </tr>
                        {top_products_table}
                    </table>
                </div>
                
                <div class="section">
                    <h2>Attention Timeline</h2>
                    <div class="chart-container">
                        <img class="chart" src="attention_timeline.png" alt="Attention Timeline">
                    </div>
                    <p>This chart shows how attention shifted between products over time during the session.</p>
                </div>
                
                <div class="section">
                    <h2>Category Analysis</h2>
                    <div class="chart-container">
                        <img class="chart" src="category_breakdown.png" alt="Category Breakdown">
                    </div>
                </div>
                
                <div class="section">
                    <h2>Attention Heatmap</h2>
                    <div class="chart-container">
                        <img class="chart" src="heatmap.png" alt="Attention Heatmap">
                    </div>
                    <p>The heatmap visualization shows the areas of the shelf that received the most attention.</p>
                </div>
                
                <div class="section">
                    <h2>Products Receiving No Attention</h2>
                    <table>
                        <tr>
                            <th>Product</th>
                            <th>Category</th>
                            <th>Price</th>
                        </tr>
                        {ignored_products_table}
                    </table>
                </div>
            </body>
            </html>
            """
            
            # Format date
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get key metrics
            session_duration = self.metrics.get("session_duration", 0)
            session_duration_formatted = f"{session_duration:.2f} seconds"
            if session_duration > 60:
                session_duration_formatted = f"{session_duration/60:.2f} minutes"
                
            product_count = self.metrics.get("product_count", 0)
            total_attention = self.metrics.get("total_attention_time", 0)
            
            ignored_products = self.metrics.get("ignored_products", [])
            ignored_count = len(ignored_products)
            ignored_percentage = self.metrics.get("ignored_percentage", 0)
            
            # Get top products
            products_by_time = self.metrics.get("products_by_attention_time", [])
            products_by_count = self.metrics.get("products_by_attention_count", [])
            
            top_product_name = products_by_count[0]["name"] if products_by_count else "None"
            top_product_views = products_by_count[0]["attention_count"] if products_by_count else 0
            
            longest_attention_product = products_by_time[0]["name"] if products_by_time else "None"
            longest_attention = products_by_time[0]["total_attention_time"] if products_by_time else 0
            
            # Generate top products table rows
            top_products_table = ""
            for i, product in enumerate(products_by_time[:5]):
                avg_time = product["total_attention_time"] / product["attention_count"] if product["attention_count"] > 0 else 0
                top_products_table += f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{product["name"]}</td>
                    <td>{product["total_attention_time"]:.2f}</td>
                    <td>{product["attention_count"]}</td>
                    <td>{avg_time:.2f}</td>
                </tr>
                """
                
            # Generate ignored products table rows
            ignored_products_table = ""
            for product in ignored_products:
                ignored_products_table += f"""
                <tr>
                    <td>{product["name"]}</td>
                    <td>{product["category"]}</td>
                    <td>${product["price"]:.2f}</td>
                </tr>
                """
                
            if not ignored_products:
                ignored_products_table = """
                <tr>
                    <td colspan="3" style="text-align: center;">No ignored products</td>
                </tr>
                """
                
            # Format HTML
            html_content = html_template.format(
                date=current_date,
                session_duration=session_duration_formatted,
                product_count=product_count,
                total_attention=total_attention,
                ignored_count=ignored_count,
                ignored_percentage=ignored_percentage,
                top_product_name=top_product_name,
                top_product_views=top_product_views,
                longest_attention_product=longest_attention_product,
                longest_attention=longest_attention,
                top_products_table=top_products_table,
                ignored_products_table=ignored_products_table
            )
            
            # Write to file
            report_path = os.path.join(report_dir, "report.html")
            with open(report_path, 'w') as f:
                f.write(html_content)
                
            logger.info(f"Generated HTML report at {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return "" 