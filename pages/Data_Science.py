import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
sys.path.append('..')
from database import DatabaseManager
import os

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Data Science Dashboard", page_icon="📊", layout="wide")

# Check login
if not st.session_state.get('logged_in', False):
    st.warning("⚠️ Please login first")
    st.stop()

st.title("📊 Data Science Dashboard")
st.markdown("### Dataset Catalog & Resource Management")

# Initialize database
db = DatabaseManager()

# Fetch all datasets
df_datasets = db.get_all_datasets()

if df_datasets.empty:
    st.warning("No dataset metadata available")
    st.stop()

# Convert date columns if they exist
if 'upload_date' in df_datasets.columns:
    df_datasets['upload_date'] = pd.to_datetime(df_datasets['upload_date'])


col1, col2, col3, col4 = st.columns(4)

with col1:
    total_datasets = len(df_datasets)
    st.metric("Total Datasets", total_datasets)

with col2:
    if 'size_mb' in df_datasets.columns:
        total_storage = df_datasets['size_mb'].sum()
        st.metric("Total Storage", f"{total_storage:.1f} MB")
    else:
        st.metric("Total Storage", "N/A")

with col3:
    if 'row_count' in df_datasets.columns:
        total_rows = df_datasets['row_count'].sum()
        st.metric("Total Records", f"{total_rows:,.0f}")
    else:
        st.metric("Total Records", "N/A")

with col4:
    if 'size_mb' in df_datasets.columns:
        avg_size = df_datasets['size_mb'].mean()
        st.metric("Avg Dataset Size", f"{avg_size:.1f} MB")
    else:
        st.metric("Avg Dataset Size", "N/A")

st.divider()

st.subheader("🎯 Critical Insight: Resource Consumption & Governance Analysis")

# Analysis tabs
tab1, tab2, tab3 = st.tabs(["💾 Storage Analysis", "📈 Source Dependencies", "🗂️ Dataset Catalog"])

with tab1:
    st.markdown("### Dataset Resource Consumption Analysis")
    
    if 'size_mb' in df_datasets.columns and 'dataset_name' in df_datasets.columns:
        # Top datasets by size
        top_datasets = df_datasets.nlargest(10, 'size_mb')
        
        # Create bar chart
        fig = px.bar(
            top_datasets,
            x='dataset_name',
            y='size_mb',
            color='size_mb',
            color_continuous_scale='Blues',
            title='Top 10 Datasets by Storage Consumption',
            labels={'size_mb': 'Size (MB)', 'dataset_name': 'Dataset Name'},
            text='size_mb'
        )
        fig.update_traces(texttemplate='%{text:.1f} MB', textposition='outside')
        fig.update_xaxes(tickangle=-45)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate storage distribution
        if 'source' in df_datasets.columns:
            storage_by_source = df_datasets.groupby('source')['size_mb'].sum().reset_index()
            storage_by_source.columns = ['Source', 'Total Size (MB)']
            storage_by_source = storage_by_source.sort_values('Total Size (MB)', ascending=False)
            
            # Key Finding
            largest_source = storage_by_source.iloc[0]
            total_storage_val = storage_by_source['Total Size (MB)'].sum()
            percentage = (largest_source['Total Size (MB)'] / total_storage_val) * 100
            
            st.warning(f"""
            **🔍 KEY FINDING:** The '{largest_source['Source']}' department consumes 
            {largest_source['Total Size (MB)']:.1f} MB ({percentage:.1f}% of total storage).
            Consider implementing data archiving policies for this department.
            """)
            
            # Storage by source table
            st.dataframe(storage_by_source, use_container_width=True, hide_index=True)
    else:
        st.info("Storage data not available")

with tab2:
    st.markdown("### Data Source Dependencies")
    
    if 'source' in df_datasets.columns:
        # Dataset count by source
        source_counts = df_datasets['source'].value_counts().reset_index()
        source_counts.columns = ['Source', 'Dataset Count']
        
        # Pie chart
        fig = px.pie(
            source_counts,
            values='Dataset Count',
            names='Source',
            title='Dataset Distribution by Source Department',
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Combined analysis
        if 'size_mb' in df_datasets.columns and 'row_count' in df_datasets.columns:
            st.markdown("### Source Department Statistics")
            
            source_stats = df_datasets.groupby('source').agg({
                'size_mb': 'sum',
                'row_count': 'sum',
                'dataset_name': 'count'
            }).reset_index()
            source_stats.columns = ['Source', 'Total Size (MB)', 'Total Rows', 'Dataset Count']
            source_stats = source_stats.sort_values('Total Size (MB)', ascending=False)
            
            # Create grouped bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Storage (MB)',
                x=source_stats['Source'],
                y=source_stats['Total Size (MB)'],
                marker_color='indianred'
            ))
            fig.add_trace(go.Bar(
                name='Dataset Count',
                x=source_stats['Source'],
                y=source_stats['Dataset Count'],
                marker_color='lightsalmon'
            ))
            fig.update_layout(
                title='Resource Consumption by Source',
                barmode='group',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(source_stats, use_container_width=True, hide_index=True)

with tab3:
    st.markdown("### Complete Dataset Catalog")
    
    # Add search and filter
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("🔍 Search datasets", placeholder="Enter dataset name...")
    with col2:
        if 'source' in df_datasets.columns:
            source_filter = st.multiselect("Filter by Source", options=df_datasets['source'].unique())
    
    # Apply filters
    filtered_df = df_datasets.copy()
    if search_term:
        filtered_df = filtered_df[filtered_df['dataset_name'].str.contains(search_term, case=False, na=False)]
    if source_filter:
        filtered_df = filtered_df[filtered_df['source'].isin(source_filter)]
    
    # Display filtered data
    st.dataframe(
        filtered_df.sort_values('size_mb', ascending=False) if 'size_mb' in filtered_df.columns else filtered_df,
        use_container_width=True,
        hide_index=True
    )
    
    st.info(f"Showing {len(filtered_df)} of {len(df_datasets)} datasets")

st.divider()

st.subheader("💡 Data Governance Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Immediate Actions:
    1. **Archive Old Datasets**: Move datasets older than 6 months to cold storage
    2. **Implement Size Limits**: Set maximum dataset size policies per department
    3. **Data Quality Checks**: Run validation on top 10 largest datasets
    4. **Duplicate Detection**: Scan for duplicate or redundant datasets
    """)

with col2:
    st.markdown("""
    #### Long-term Strategies:
    1. **Governance Framework**: Establish data retention and archiving policies
    2. **Automated Cleanup**: Schedule quarterly data cleanup processes
    3. **Cost Allocation**: Implement chargeback model for storage costs
    4. **Metadata Standards**: Enforce comprehensive metadata documentation
    """)

st.divider()


st.subheader("🤖 AI Data Governance Advisor")

with st.expander("Get AI-Powered Data Management Insights"):
    user_question = st.text_area(
        "Ask the AI about data governance, storage optimization, or best practices:",
        placeholder="E.g., 'What are best practices for data retention policies?'"
    )
    
    if st.button("Get AI Advice"):
        if user_question:
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                st.warning("""
                ⚠️ OpenAI API key not configured. To enable AI features:
                1. Set environment variable: `export OPENAI_API_KEY='your-key'`
                2. Or create a `.env` file with: `OPENAI_API_KEY=your-key`
                """)
            else:
                try:
                    import openai
                    openai.api_key = api_key
                    
                    context = f"""
                    Current Data Science Metrics:
                    - Total Datasets: {total_datasets}
                    - Total Storage: {total_storage:.1f} MB
                    - Total Records: {total_rows:,.0f}
                    """
                    
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a data governance expert providing strategic insights."},
                            {"role": "user", "content": f"{context}\n\nQuestion: {user_question}"}
                        ]
                    )
                    
                    st.success("AI Response:")
                    st.write(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"AI service error: {str(e)}")
        else:
            st.warning("Please enter a question")


with st.expander("➕ Add New Dataset"):
    with st.form("add_dataset_form"):
        new_name = st.text_input("Dataset Name")
        new_source = st.selectbox("Source Department", ["IT", "Cybersecurity", "Marketing", "Finance", "Operations"])
        new_size = st.number_input("Size (MB)", min_value=0.0, step=0.1)
        new_rows = st.number_input("Row Count", min_value=0, step=1000)
        new_date = st.date_input("Upload Date")
        
        if st.form_submit_button("Add Dataset"):
            if new_name:
                db.add_dataset(new_name, new_source, new_size, new_rows, new_date)
                st.success("Dataset added successfully!")
                st.rerun()
            else:
                st.warning("Please provide a dataset name")

with st.expander("🗑️ Delete Dataset"):
    if 'dataset_id' in df_datasets.columns:
        dataset_to_delete = st.selectbox(
            "Select dataset to delete",
            options=df_datasets['dataset_id'].tolist(),
            format_func=lambda x: df_datasets[df_datasets['dataset_id']==x]['dataset_name'].values[0]
        )
        
        if st.button("Delete Selected Dataset", type="primary"):
            db.delete_dataset(dataset_to_delete)
            st.success("Dataset deleted successfully!")
            st.rerun()