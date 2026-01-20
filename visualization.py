from typing import Dict, List, Optional, Tuple
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta

def plot_uploads_per_day(records_df: pd.DataFrame, days: int = 30) -> None:
    """
    Display a bar chart of uploads per day for the specified number of days.
    
    Args:
        records_df (pd.DataFrame): DataFrame containing records from DynamoDB
        days (int, optional): Number of days to display. Defaults to 30.
    """
    if records_df.empty:
        st.warning("No records available to display.")
        return
    
    # Make a copy to avoid modifying the original DataFrame
    df = records_df.copy()
    
    # Convert creation_date to datetime if it's a string
    if 'creation_date' in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df['creation_date']):
            df['creation_date'] = pd.to_datetime(df['creation_date'])
        
        # Extract just the date part (without time) for consistent daily grouping
        df['date'] = df['creation_date'].dt.normalize()
        
        # Group by date and count records
        daily_counts = df.groupby('date').size()
        
        # Get the last 'days' days
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)  # -1 to include today
        
        # Create a complete date range to include all days
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Reindex with the complete date range, filling missing values with 0
        daily_counts = daily_counts.reindex(date_range, fill_value=0)
        
        # Create a DataFrame for plotting
        plot_df = pd.DataFrame({
            'Date': daily_counts.index,
            'Uploads': daily_counts.values
        })
        
        # Ensure the date column is in the correct format
        plot_df['Date'] = pd.to_datetime(plot_df['Date']).dt.date
        
        # Create the bar chart using Plotly
        fig = px.bar(
            plot_df,
            x='Date',
            y='Uploads',
            title=f'Uploads Per Day (Last {days} Days)',
            labels={'Date': 'Date', 'Uploads': 'Number of Uploads'},
            color_discrete_sequence=['#1f77b4']
        )
        
        # Update layout for better readability
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Number of Uploads',
            xaxis_tickformat='%b %d, %Y',
            hovermode='x',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        # Add a line connecting the bars
        fig.add_scatter(
            x=plot_df['Date'],
            y=plot_df['Uploads'],
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=2),
            marker=dict(size=8, color='#ff7f0e'),
            name='Trend',
            hovertemplate='%{y} uploads on %{x|%b %d, %Y}<extra></extra>'
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Show some statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Uploads", int(daily_counts.sum()))
        with col2:
            st.metric("Average Daily Uploads", f"{daily_counts.mean():.1f}")
        with col3:
            st.metric("Busiest Day", f"{daily_counts.idxmax().strftime('%b %d, %Y')}")
    else:
        st.error("No 'creation_date' column found in the data.")

def plot_uploads_by_user(records_df: pd.DataFrame) -> None:
    """
    Display a bar chart of uploads by user.
    
    Args:
        records_df (pd.DataFrame): DataFrame containing records from DynamoDB
    """
    if records_df.empty:
        st.warning("No records available to display.")
        return
    
    if 'user_name' in records_df.columns:
        user_counts = records_df['user_name'].value_counts().reset_index()
        user_counts.columns = ['User', 'Uploads']
        
        fig = px.bar(
            user_counts,
            x='User',
            y='Uploads',
            title='Uploads by User',
            labels={'User': 'User', 'Uploads': 'Number of Uploads'},
            color='User',
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        
        fig.update_layout(
            xaxis_title='User',
            yaxis_title='Number of Uploads',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No 'user_name' column found in the data.")

def display_upload_analytics(records_df: pd.DataFrame, days: int = 30) -> None:
    """
    Display a dashboard of upload analytics.
    
    Args:
        records_df (pd.DataFrame): DataFrame containing records from DynamoDB
        days (int, optional): Number of days to display. Defaults to 30.
    """
    st.header("📊 Upload Analytics")
    
    # Uploads per day chart
    st.subheader("Daily Uploads")
    plot_uploads_per_day(records_df, days)
    
    # Uploads by user chart
    st.subheader("Uploads by User")
    plot_uploads_by_user(records_df)
    
    # Show recent uploads in a table
    st.subheader("Recent Uploads")
    if not records_df.empty:
        # Select and order columns
        display_cols = ['creation_date', 'user_name', 'data_id']
        if 'image_url' in records_df.columns:
            display_cols.append('image_url')
        if 'excel_url' in records_df.columns:
            display_cols.append('excel_url')
            
        # Format the DataFrame for display
        display_df = records_df[display_cols].copy()
        display_df['creation_date'] = pd.to_datetime(display_df['creation_date']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Display the table
        st.dataframe(
            display_df.sort_values('creation_date', ascending=False),
            column_config={
                'creation_date': 'Upload Time',
                'user_name': 'User',
                'data_id': 'Record ID',
                'image_url': st.column_config.LinkColumn('Image'),
                'excel_url': st.column_config.LinkColumn('Excel File')
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No recent uploads to display.")
