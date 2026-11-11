import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    df = pd.read_csv("Unicorn_Companies.csv")
    
    # Data cleaning 
    # Replacing NaN in City and Investors columns
    df.fillna({"Select Investors":"None"},inplace=True)
    capitals = {"Bahamas":"Nassau", "Singapore":"Singapore City", "Hong Kong": "Hong Kong"}
    df.loc[:,"City"] = df['City'].fillna(df['Country/Region'].map(capitals))

    # changing datatype of Date Joined column
    df["Date Joined"] = pd.to_datetime(df["Date Joined"])
    df["Year Joined"] = df["Date Joined"].dt.year

    # changing the Valuation & Funding columns
    df["Valuation"] = df["Valuation"].str.replace("$", "").str.replace("B", "000000000")
    df["Valuation"] = df["Valuation"].astype("float64")

    df["Funding"] = df["Funding"].str.replace("$", "").str.replace("B", "000000000").str.replace("M", "000000").str.replace('Unknown', "-1")
    df["Funding"] = df["Funding"].astype("float64")

    # Replacing duplicated Artificial Intelligence in Industry column
    df['Industry']=df['Industry'].replace({"Artificial Intelligence":"Artificial intelligence"})

    return df
try:
    df = load_data()
    # app title
    st.title("Unicorn Companies Analysis App")
    # interactive table
    # st.dataframe(df.head(10))
    # st.write(df.head(10))

    # filters for country, industry etc
    countries = df["Country/Region"].unique()
    industries = df['Industry'].unique()
    continent = df['Continent'].unique()
    
    # date filter in slider form
    year_min = int(df['Year Joined'].min())
    year_max = int(df["Year Joined"].max())
    if year_min < year_max:
        year_range = st.sidebar.slider("Year Joined", min_value=year_min, max_value=year_max, value=(year_min, year_max))
    else:
        year_range = (year_min, year_max)
        
    #create the multiselect box in the app sidbar
    selected_industries = st.sidebar.multiselect("Select Industries", industries, default=industries)
    selected_countries = st.sidebar.multiselect("Choose Countries", countries, default=countries)
    selected_continent = st.sidebar.multiselect("Select Continent", continent, default=continent)

    # Apply the filters selected
    filtered_df = df[(df["Industry"].isin(selected_industries)) & 
                     (df["Continent"].isin(selected_continent)) & 
                     (df["Country/Region"].isin(selected_countries))].copy()
    
    # Display the filtered data
    st.dataframe(filtered_df)

    # format long numbers
    def billions_format(value):
        return f"${value/1000000000:,.2f}B"

    def trillions_format(value):
        return f"${value / 1000000000000:,.2f}T"

    # empty filters handler
    def show_empty_msg():
        st.info("No matching filter. Adjust your selected filters")

    # Global Overview
    st.header("1. Global Overview")
    if not filtered_df.empty:
        total_companies = filtered_df["Company"].nunique()
        total_valuation = filtered_df["Valuation"].sum()
        total_funding = filtered_df["Funding"].sum()
        avg_valuation = filtered_df["Valuation"].mean()

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        col1.metric("Total Unicorns", f"{total_companies:,}")
        col2.metric("Combined Valuation", trillions_format(total_valuation))
        col3.metric("Total Funding", billions_format(total_funding))
        col4.metric("Average Valuation", billions_format(avg_valuation))

        col6, col7 = st.columns(2)

        with col6:
            industry_counts = (filtered_df["Industry"].value_counts().reset_index())
            industry_counts.columns = ["Industry", "Companies"]

            st.write(industry_counts)
            
            fig = px.pie(
            industry_counts,
            names="Industry",
            values="Companies",
            hole=0.45, 
            title="Unicorns by Industry")
            st.plotly_chart(fig, use_container_width=True)

        with col7:
            continent_counts = (filtered_df["Continent"].value_counts().reset_index())
            continent_counts.columns = ["Continent","Companies"]

            st.write(continent_counts)
            
            fig = px.bar(
            continent_counts,
            x="Continent",
            y="Companies",
            color="Continent",
            title="Unicorns by Continent"
            )
            st.plotly_chart(fig, use_container_width=True)


#    col8, col9 = st.columns(2)
            
    ### Q1 - top 5 industries by funding
    # with col8:
    #     industry_funding = (filtered_df.groupby("Industry")["Funding"].sum().reset_index())
    #     industry_funding.columns = ["Industry", "Total Funding"]
    
    #     industry_funding = industry_funding.sort_values(by="Total Funding", ascending=False).head(5)
    #     # st.write(industry_funding)
    
    #     fig = px.bar(
    #         industry_funding,
    #         x="Industry",
    #         y="Total Funding",
    #         color="Industry",
    #         title="Top 5 Industries by Funding"
    #     )
    #     fig.update_layout(
    #     autosize=True,
    #     showlegend=False,
    #     height=500,
    #     margin=dict(l=50, r=30, t=70, b=120)
    #     )
    #     fig.update_xaxes(tickangle=45)
    #     st.plotly_chart(fig, use_container_width=True)
        


    ### This is another section
    st.subheader("Geographical Distribution Map")
    if not filtered_df.empty:
        map_data = (
            filtered_df.groupby("Country/Region").agg(
                Companies=("Company", "nunique"),
                Total_Valuation=("Valuation", "sum")
            ).reset_index()
        )
        
        fig=px.choropleth(
            map_data,
            locations="Country/Region",
            locationmode="country names",
            color="Companies",
            hover_name="Country/Region",
            hover_data=["Total_Valuation"],
            title="Global Unicorn Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        show_empty_msg()

    
    ### Q1 - top 5 industries by funding
    st.subheader("Q1 - Top 5 Industries by Funding")
    
    chart_1_data = df.groupby("Industry")["Funding"].sum().reset_index().sort_values(by="Funding", ascending=False)
    top5 = chart_1_data.head(5)
    colors = plt.cm.coolwarm(top5["Funding"] / top5["Funding"].max())
    x = top5["Industry"]
    y = top5["Funding"]
    plt.bar(x, y, color=colors)
#    plt.title("Top 5 Industries by Funding")
    plt.ylabel("Funding")
    plt.xlabel("Industry")
    plt.xticks(rotation=45)
#    plt.show()
    st.pyplot(plt.gcf())
    plt.close()

    ### Q2 - Top 5 industries by valuation
    st.subheader("Q2 - Top 5 industries by valuation")
    
    chart_2_data = df.groupby("Industry")["Valuation"].sum().reset_index().sort_values(by="Valuation", ascending=False)
    top5_val = chart_2_data.head(5)
    colors = plt.cm.viridis(top5_val["Valuation"] / top5_val["Valuation"].max())
    plt.bar(top5_val["Industry"], top5_val["Valuation"], color=colors)
#    plt.title("Top 5 Industries by Valuation")
    plt.ylabel("Valuation")
    plt.xlabel("Industry")
    plt.xticks(rotation=45)
#    plt.show()
    st.pyplot(plt.gcf())
    plt.close()
    
    ### Q3 - Top 5 investors globally
    st.subheader("Q3 - Top 5 investors globally")

    Investors = df["Select Investors"].dropna().str.split(",").explode().str.strip().value_counts().reset_index()
    Investors.rename(columns={"Select Investors":"Investors", "count":"No. of Companies"}, inplace=True)
    top5_investors = Investors.head(5)
    colors = plt.cm.turbo(top5_investors["No. of Companies"] / top5_investors["No. of Companies"].max())

    plt.bar(top5_investors["Investors"], top5_investors["No. of Companies"], color=colors)
    plt.title("Top 5 Investors Globally")
    plt.ylabel("Number of Companies Invested In")
    plt.xlabel("Investors")
    plt.xticks(rotation=45)
#    plt.show()
    st.pyplot(plt.gcf())
    plt.close()


    ### Q4 - Fastest companies to reach unicorn status(date founded-date joined)
    st.subheader("Q4 - Fastest companies to reach unicorn status(date founded-date joined)")
    
    df["Year Joined"] = df["Date Joined"].dt.year
    df_q4 = df[["Company", "Date Joined", "Year Founded", "Year Joined"]]
    df_q4.loc[:,"Years_to_Unicorn"] = (df_q4["Year Joined"] - df_q4["Year Founded"])
    df_q4 = df_q4.reset_index().query("Years_to_Unicorn >= 1").sort_values("Years_to_Unicorn", ascending=True).head(50)
    df_q4

    ### Q5 - Most valuable company
    st.subheader("Q5 - Most Valuable Company")
    
    df[["Company", "Valuation"]].sort_values(by="Valuation", ascending=False)
    company_valuation = df.groupby("Company")["Valuation"].sum().sort_values(ascending=False).head(20)

    company_valuation

    ### # Q6 - Location where most unicorn companies are concentrated
    st.subheader("Q6 - Location where most unicorn companies are concentrated")

    most_loc = df["Country/Region"].value_counts().head(10)
    most_loc
#    df[['City', 'Country/Region', 'Continent']]
    # aggregrate country/region data
    country_counts = df["Country/Region"].value_counts().reset_index()
    country_counts.columns = ['Country', 'No. of Companies']
    country_counts.head(3)
    fig = px.choropleth(country_counts, locations="Country", locationmode="country names", color="No. of Companies",
    title="Unicorn Companies by Country")

#    fig.show()
    st.plotly_chart(fig, use_container_width=True)


    
except URLError as e:
    st.error(f"This demo requires internet access. Connection error: {e.reason}")