"""
Advanced Visualizer Module
Enhanced visualizations with interactive charts and advanced analytics
"""

import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class AdvancedVisualizer:
    """Advanced visualization capabilities for electricity market analysis"""
    
    def __init__(self):
        self.color_schemes = {
            'default': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'market': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#5C2E7E'],
            'revenue': ['#2ecc71', '#f39c12', '#e74c3c', '#3498db', '#9b59b6']
        }
        
        self.chart_templates = {
            'professional': 'plotly_white',
            'dark': 'plotly_dark',
            'minimal': 'simple_white'
        }
    
    def create_market_heatmap(self, price_data: Dict[str, pd.Series], 
                           title: str = "Multi-Market Price Heatmap") -> go.Figure:
        """
        Create interactive heatmap for multi-market price comparison
        
        Args:
            price_data: Dictionary of market price series
            title: Chart title
            
        Returns:
            Interactive heatmap figure
        """
        # Create DataFrame with all markets
        df = pd.DataFrame(price_data)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=df.values.T,
            x=df.index,
            y=df.columns,
            colorscale='Viridis',
            colorbar=dict(title="Price ($/MWh)"),
            hovertemplate='Market: %{y}<br>Time: %{x}<br>Price: $%{z:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Market",
            template=self.chart_templates['professional'],
            height=500
        )
        
        return fig
    
    def create_revenue_waterfall(self, events_df: pd.DataFrame, 
                                title: str = "Revenue Waterfall Analysis") -> go.Figure:
        """
        Create waterfall chart for revenue analysis
        
        Args:
            events_df: DataFrame with extreme events
            title: Chart title
            
        Returns:
            Interactive waterfall figure
        """
        # Sort events by revenue
        sorted_events = events_df.sort_values('revenue', ascending=False).head(10)
        
        # Calculate cumulative revenue
        cumulative_revenue = sorted_events['revenue'].cumsum()
        
        # Create waterfall data
        x = [f"Event {i+1}" for i in range(len(sorted_events))]
        y = sorted_events['revenue'].values
        text = [f"${rev:,.0f}" for rev in y]
        
        # Color based on positive/negative revenue
        colors = ['#2ecc71' if rev > 0 else '#e74c3c' for rev in y]
        
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=x,
            y=y,
            text=text,
            textposition='auto',
            marker_color=colors,
            name='Revenue'
        ))
        
        # Add cumulative line
        fig.add_trace(go.Scatter(
            x=x,
            y=cumulative_revenue,
            mode='lines+markers',
            name='Cumulative Revenue',
            line=dict(color='#3498db', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Events",
            yaxis=dict(title="Revenue ($)", side="left"),
            yaxis2=dict(title="Cumulative Revenue ($)", side="right", overlaying="y"),
            template=self.chart_templates['professional'],
            height=600,
            legend=dict(x=0.01, y=0.99)
        )
        
        return fig
    
    def create_volatility_surface(self, price_data: pd.Series, 
                                window_sizes: List[int] = [24, 48, 168],
                                title: str = "Volatility Surface Analysis") -> go.Figure:
        """
        Create 3D surface plot for volatility analysis
        
        Args:
            price_data: Price series data
            window_sizes: List of rolling window sizes
            title: Chart title
            
        Returns:
            Interactive 3D surface figure
        """
        # Calculate rolling volatilities
        volatility_data = []
        
        for window in window_sizes:
            rolling_vol = price_data.rolling(window=window).std()
            volatility_data.append(rolling_vol.dropna())
        
        # Create meshgrid
        max_points = min(len(vol) for vol in volatility_data)
        x = np.arange(max_points)
        y = window_sizes
        z = np.array([vol.iloc[:max_points].values for vol in volatility_data])
        
        # Create surface plot
        fig = go.Figure(data=[go.Surface(
            z=z,
            x=x,
            y=y,
            colorscale='Viridis',
            colorbar=dict(title="Volatility ($)")
        )])
        
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title="Time Points",
                yaxis_title="Window Size (Hours)",
                zaxis_title="Volatility ($)"
            ),
            template=self.chart_templates['professional'],
            height=600
        )
        
        return fig
    
    def create_event_sankey(self, events_df: pd.DataFrame,
                           title: str = "Event Flow Analysis") -> go.Figure:
        """
        Create Sankey diagram for event type transitions
        
        Args:
            events_df: DataFrame with extreme events
            title: Chart title
            
        Returns:
            Interactive Sankey figure
        """
        # Prepare data for Sankey
        event_types = events_df['event_type'].unique()
        
        # Create nodes
        nodes = []
        node_dict = {}
        
        # Add event type nodes
        for i, event_type in enumerate(event_types):
            nodes.append(dict(label=event_type))
            node_dict[event_type] = i
        
        # Add outcome nodes
        outcomes = ['High Profit', 'Moderate Profit', 'Break Even', 'Loss']
        for outcome in outcomes:
            nodes.append(dict(label=outcome))
            node_dict[outcome] = len(nodes) - 1
        
        # Create links
        links = []
        for _, event in events_df.iterrows():
            source = node_dict[event['event_type']]
            revenue = event['revenue']
            
            # Determine outcome
            if revenue > 50000:
                target = node_dict['High Profit']
            elif revenue > 0:
                target = node_dict['Moderate Profit']
            elif revenue > -10000:
                target = node_dict['Break Even']
            else:
                target = node_dict['Loss']
            
            links.append(dict(source=source, target=target, value=1))
        
        # Aggregate links
        aggregated_links = {}
        for link in links:
            key = (link['source'], link['target'])
            aggregated_links[key] = aggregated_links.get(key, 0) + link['value']
        
        final_links = [
            dict(source=k[0], target=k[1], value=v)
            for k, v in aggregated_links.items()
        ]
        
        # Create Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=[node['label'] for node in nodes]
            ),
            link=dict(
                source=[link['source'] for link in final_links],
                target=[link['target'] for link in final_links],
                value=[link['value'] for link in final_links]
            )
        )])
        
        fig.update_layout(
            title=title,
            template=self.chart_templates['professional'],
            height=600
        )
        
        return fig
    
    def create_correlation_matrix(self, market_data: Dict[str, pd.Series],
                                title: str = "Market Correlation Matrix") -> go.Figure:
        """
        Create correlation matrix heatmap for multiple markets
        
        Args:
            market_data: Dictionary of market price series
            title: Chart title
            
        Returns:
            Interactive correlation matrix figure
        """
        # Create DataFrame and calculate correlations
        df = pd.DataFrame(market_data)
        correlation_matrix = df.corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            colorbar=dict(title="Correlation"),
            text=correlation_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate='Market 1: %{x}<br>Market 2: %{y}<br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            template=self.chart_templates['professional'],
            height=500
        )
        
        return fig
    
    def create_price_distribution(self, price_data: pd.Series,
                                event_data: pd.DataFrame = None,
                                title: str = "Price Distribution Analysis") -> go.Figure:
        """
        Create price distribution histogram with event overlay
        
        Args:
            price_data: Price series data
            event_data: DataFrame with extreme events
            title: Chart title
            
        Returns:
            Interactive distribution figure
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Price Distribution', 'Event Price Distribution'),
            vertical_spacing=0.1
        )
        
        # Overall price distribution
        fig.add_trace(
            go.Histogram(
                x=price_data,
                nbinsx=50,
                name='All Prices',
                marker_color='#3498db',
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # Event price distribution
        if event_data is not None and len(event_data) > 0:
            # Extract event prices
            event_prices = []
            for _, event in event_data.iterrows():
                event_prices.extend(event['peak_hours'].values())
                event_prices.extend(event['off_peak_hours'].values())
            
            if event_prices:
                fig.add_trace(
                    go.Histogram(
                        x=event_prices,
                        nbinsx=30,
                        name='Event Prices',
                        marker_color='#e74c3c',
                        opacity=0.7
                    ),
                    row=2, col=1
                )
        
        fig.update_layout(
            title=title,
            template=self.chart_templates['professional'],
            height=600,
            showlegend=True
        )
        
        fig.update_xaxes(title_text="Price ($/MWh)", row=1, col=1)
        fig.update_xaxes(title_text="Price ($/MWh)", row=2, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=2, col=1)
        
        return fig
    
    def create_revenue_treemap(self, events_df: pd.DataFrame,
                              title: str = "Revenue by Event Type") -> go.Figure:
        """
        Create treemap for revenue visualization by event type
        
        Args:
            events_df: DataFrame with extreme events
            title: Chart title
            
        Returns:
            Interactive treemap figure
        """
        # Group by event type
        grouped = events_df.groupby('event_type').agg({
            'revenue': ['sum', 'mean', 'count']
        }).round(2)
        
        # Prepare data for treemap
        labels = grouped.index
        values = grouped[('revenue', 'sum')]
        parents = [''] * len(labels)
        
        # Add sub-items for each event type
        for i, (event_type, group) in enumerate(events_df.groupby('event_type')):
            for _, event in group.iterrows():
                labels.append(f"{event_type} - {event['date'].strftime('%m/%d')}")
                values.append(abs(event['revenue']))
                parents.append(event_type)
        
        # Create treemap
        fig = go.Figure(go.Treemap(
            labels=labels,
            values=values,
            parents=parents,
            branchvalues="total",
            hovertemplate='<b>%{label}</b><br>Revenue: $%{value:,.0f}<extra></extra>',
            texttemplate="%{label}<br>$%{value:,.0f}",
            textinfo="label+value"
        ))
        
        fig.update_layout(
            title=title,
            template=self.chart_templates['professional'],
            height=600
        )
        
        return fig
    
    def create_advanced_dashboard(self, market_data: Dict[str, pd.Series],
                                events_df: pd.DataFrame,
                                title: str = "Advanced Market Dashboard") -> go.Figure:
        """
        Create comprehensive dashboard with multiple visualizations
        
        Args:
            market_data: Dictionary of market price series
            events_df: DataFrame with extreme events
            title: Dashboard title
            
        Returns:
            Multi-panel dashboard figure
        """
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Price Trends', 'Volume Analysis',
                'Revenue Distribution', 'Event Types',
                'Market Correlation', 'Volatility Analysis'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "histogram"}, {"type": "pie"}],
                [{"type": "heatmap"}, {"type": "scatter"}]
            ]
        )
        
        # Price trends
        for market, data in market_data.items():
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data.values,
                    name=market,
                    mode='lines'
                ),
                row=1, col=1
            )
        
        # Revenue distribution
        fig.add_trace(
            go.Histogram(
                x=events_df['revenue'],
                name='Revenue',
                nbinsx=20
            ),
            row=2, col=1
        )
        
        # Event types pie chart
        event_counts = events_df['event_type'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=event_counts.index,
                values=event_counts.values,
                name='Event Types'
            ),
            row=2, col=2
        )
        
        # Market correlation
        df = pd.DataFrame(market_data)
        corr_matrix = df.corr()
        fig.add_trace(
            go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0
            ),
            row=3, col=1
        )
        
        # Volatility analysis
        for market, data in market_data.items():
            rolling_vol = data.rolling(24).std()
            fig.add_trace(
                go.Scatter(
                    x=rolling_vol.index,
                    y=rolling_vol.values,
                    name=f'{market} Volatility',
                    mode='lines',
                    yaxis='y6'
                ),
                row=3, col=2
            )
        
        fig.update_layout(
            title=title,
            template=self.chart_templates['professional'],
            height=1200,
            showlegend=True
        )
        
        return fig


if __name__ == "__main__":
    # Example usage
    visualizer = AdvancedVisualizer()
    
    # Create sample data
    dates = pd.date_range('2026-01-01', periods=168, freq='H')
    np.random.seed(42)
    
    market_data = {
        'ERCOT': pd.Series(50 + 10 * np.sin(np.arange(168) * 2 * np.pi / 24) + np.random.normal(0, 5, 168), index=dates),
        'NYISO': pd.Series(55 + 8 * np.sin(np.arange(168) * 2 * np.pi / 24) + np.random.normal(0, 4, 168), index=dates),
        'PJM': pd.Series(48 + 12 * np.sin(np.arange(168) * 2 * np.pi / 24) + np.random.normal(0, 6, 168), index=dates)
    }
    
    # Create sample events
    events_df = pd.DataFrame({
        'date': pd.date_range('2026-01-01', periods=10, freq='D'),
        'revenue': np.random.normal(20000, 15000, 10),
        'event_type': np.random.choice(['Price Spike', 'High Volatility', 'Market Stress'], 10)
    })
    
    # Create visualizations
    heatmap = visualizer.create_market_heatmap(market_data)
    correlation = visualizer.create_correlation_matrix(market_data)
    revenue_chart = visualizer.create_revenue_treemap(events_df)
    
    print("Advanced Visualizations Created:")
    print(f"• Market Heatmap: {len(heatmap.data)} traces")
    print(f"• Correlation Matrix: {correlation.data[0].z.shape} matrix")
    print(f"• Revenue Treemap: {len(revenue_chart.labels)} segments")
