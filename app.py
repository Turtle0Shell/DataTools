import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient 


@st.cache_data  # Cache the data to improve performance
def load_data():
    

   
     client = MongoClient('mongodb+srv://turtle0sheild:Aa123456@datatools.qpgaxdw.mongodb.net/')
     db = client['DST_project']
     collection = db['test']
     data = list(collection.find())
     df_from_mongo = pd.DataFrame(data)
     client.close()
     return df_from_mongo


df = load_data()


st.title("Interactive Airline Review Analysis")
st.markdown("This web app presents an analysis of airline reviews...")


st.sidebar.header("Filters")
selected_airline = st.sidebar.selectbox("Select an Airline", ["All"] + sorted(df['Airline Name'].unique()))

# Filter data based on selection
if selected_airline != "All":
    filtered_df = df[df['Airline Name'] == selected_airline]
else:
    filtered_df = df


# Section 1: Basic Statistics
st.header("Basic Rating Statistics (Ignoring Zeros)")
def calculate_stats_ignoring_zeros(df, columns):
    
    stats = {}
    for column in columns:
        non_zero_values = df[df[column] > 0][column]
        stats[column] = {
            'mean': non_zero_values.mean(),
            'median': non_zero_values.median(),
            'count': non_zero_values.count()
        }
    return pd.DataFrame(stats).T

rating_columns = ['Overall_Rating', 'Seat Comfort', 'Cabin Staff Service', 'Food & Beverages',
                  'Ground Service', 'Inflight Entertainment', 'Wifi & Connectivity', 'Value For Money']
rating_stats = calculate_stats_ignoring_zeros(filtered_df, rating_columns)
st.dataframe(rating_stats)

# Section 2: Top Airlines by Mean Overall Rating
st.header("Top Airlines by Mean Overall Rating (Ignoring Zeros)")
if not filtered_df.empty:
    top_n = st.slider("Number of Top Airlines to Show", 5, 20, 10)
    top_airlines = filtered_df[filtered_df['Overall_Rating'] > 0].groupby('Airline Name')['Overall_Rating'].mean().sort_values(ascending=False).head(top_n)
    fig_top_airlines, ax_top_airlines = plt.subplots()
    top_airlines.plot(kind='bar', ax=ax_top_airlines)
    ax_top_airlines.set_xlabel("Airline Name")
    ax_top_airlines.set_ylabel("Mean Overall Rating")
    ax_top_airlines.set_title(f"Top {top_n} Airlines by Mean Overall Rating")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig_top_airlines)
else:
    st.warning("No data available for the selected airline.")


# Section 3: Correlation Heatmap
st.header("Correlation Heatmap of Ratings (Ignoring Zeros)")
columns_to_analyze = ['Overall_Rating', 'Seat Comfort', 'Cabin Staff Service', 'Food & Beverages',
                      'Ground Service', 'Inflight Entertainment', 'Wifi & Connectivity', 'Value For Money']
filtered_corr_df = filtered_df[(filtered_df[columns_to_analyze] > 0).all(axis=1)][columns_to_analyze]
if not filtered_corr_df.empty:
    correlation_matrix = filtered_corr_df.corr()
    fig_corr, ax_corr = plt.subplots()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', ax=ax_corr)
    ax_corr.set_title("Correlation Heatmap")
    st.pyplot(fig_corr)
else:
    st.warning("Insufficient data for correlation analysis for the selected airline.")

    

