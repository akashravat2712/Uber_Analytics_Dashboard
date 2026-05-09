import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

st.set_page_config("Uber Analytics",layout="wide")
df=pd.read_csv("uber_data.csv")

#SIDEBAR
with st.sidebar:
    selected=option_menu("Main Menu",["Dataset","Overview","Ride Analytics"],icons=["table","bar-chart","graph-up"],menu_icon="car-front",default_index=1)

#DATASET
if selected=="Dataset":
    st.title("Data Exploration")
    col1,col2,col3=st.columns(3)
    col1.metric("Total Rows",df.shape[0])
    col2.metric("Total Columns",df.shape[1])
    col3.metric("Missing Values",df.isnull().sum().sum())

    st.divider()

    #COLUMNS SELECTION
    st.subheader("select Columns")
    selected_columns=st.multiselect("Choose Columns",df.columns,default=df.columns)
    filtered_df=df[selected_columns]
    # st.dataframe()
    st.divider()

    #SEARCH Dataset
    st.subheader("Search In Dataset")
    search=st.text_input("Search data From Here")
    if search:
        filtered_df=filtered_df[filtered_df.astype(str).apply(
            lambda row:row.str.contains(search,case=False).any(),axis=1
        )]
        st.dataframe()
    st.divider()

    #Column filter -column name| Value
    st.subheader("Column Filter")
    col1,col2=st.columns(2)
    with col1:
        filter_column=st.selectbox("Select Column",filtered_df.columns)
    with col2:
        filter_value=st.selectbox("Select Value",filtered_df[filter_column].dropna().unique())
    st.divider()
    st.dataframe(filtered_df)
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data", csv, "filtered_uber_data.csv", "csv")
    st.divider()
#
# #SLIDER
#TABLE
#DOWNLOADst.divider()
    #slider
    st.subheader("Row slider")
    row_num=st.slider("Select Row Number",0,max_value=df.shape[0])

    st.subheader("Row Preview")
    st.dataframe(filtered_df.iloc[row_num-1])
    #
    # csv = filtered_df.to_csv(index=False).encode('utf-8')
    # st.download_button("Download Filtered Data", csv, "filtered_uber_data.csv", "csv")

if selected=="Overview":
    st.title("Dashboard Overview")
    col1,col2=st.columns(2)
    col1.metric("Total Rides",len(df))
    col2.metric("Revenue",df["Booking Value"].sum())
    st.divider()
    total_revenue=df["Booking Value"].sum()
    total_rides = len(df)

    #Business Unit Performance
    st.subheader("Business Unit Performance")
    bu_metrix=df.groupby("Vehicle Type").agg(
        Total_Booking=("Booking ID","count"),
        Revenue_Generated=("Booking Value","sum"),
        Avg_Distance=("Ride Distance","mean"),
        Av_Rating=("Customer Rating","mean")
    )
    bu_metrix["Revenue Share%"]=(bu_metrix["Revenue_Generated"]/total_revenue*100
                                 if total_revenue>0 else 0)
    st.dataframe(bu_metrix.style.format({
        "Total_Booking":"${:,.2f}",
        "Avg_Distance":"{:,.2f}Km",
        "Av_Rating":"{:,.1f}",
        "Revenue Share%":"{:,.2f}%"
    }).background_gradient(subset="Revenue_Generated",cmap="YlOrRd"))

    # Operation efficiency
    col_eff , col_can = st.columns(2)
    with col_eff:
         st.subheader("Operation Efficiency")
         eef_df = df.groupby("Vehicle Type") [["Avg VTAT", "Avg CTAT"]].mean()
         st.write("Average TurnAround Time(in Minutes)")
         st.dataframe(eef_df.style.highlight_max(axis=0,color="#d81416").highlight_min(axis=0,color="#e6ed6f"),
                 use_container_width=True)

    with col_can:
        st.subheader("Cancellation Audit")
        status_count = df["Booking Status"].value_counts().to_frame(name="Count")
        status_count["Share %"] = (status_count["Count"]/total_rides*100)
        st.dataframe(status_count,use_container_width=True)



    # FINANCIAL DEEP DIVE
    st.header("Financial Deep Dive")
    pay_col , reason_col = st.columns([4,4])

    # payment analysis
    completed_ride =df[df["Booking Status"]=="Completed"]
    with pay_col:
        st.markdown("** Payment Method Overview**")
        pay_summary = (completed_ride["Payment Method"].value_counts(normalize=True)*100)
        st.dataframe(pay_summary.rename("% Usage"),use_container_width=True)

    with reason_col:
        st.markdown("Primary Cancellation Trigger")
        cust_reason = (df["Reason for cancelling by Customer"].dropna().value_counts().head(3))
        drv_reason = (df["Driver Cancellation Reason"].dropna().value_counts().head(3))

        cust_reason.index = "Customer:" + cust_reason.index
        drv_reason.index = "Driver:" + drv_reason.index

        reason_df = pd.concat([cust_reason, drv_reason]).to_frame()

        reason_df.columns=["Incident Found"]
        st.dataframe(reason_df)

    # data quality
    with st.expander("Data Quality & Audit Logo"):
        audit1,audit2 = st.columns(2)
        audit1.write(f"Duplicate Records: {df.duplicated().sum()}")
        audit2.write(f"Missing Values: {df["Booking Value"].isnull().sum()}")
        st.info("Missing Booking Values are Expected for Cancelled ride or no-driver found")
        st.success("Executive Overview Generated from Operational Dataset")

    st.title("Uber Operation")
    st.markdown("---")

    # Strategic kpi layer
    completed_ride = df[df["Booking Status"]=="Completed"]
    total_revenue = completed_ride["Booking Value"].sum()
    avg_distance = completed_ride["Ride Distance"].mean()
    success_rate = (len(completed_ride)/total_rides*100 if total_rides>0 else 0)
    avg_rating = completed_ride["Customer Rating"].dropna().mean()

    kpi1,kpi2,kpi3,kpi4 = st.columns(4)
    kpi1.metric("Gross Total Revenue",f"{total_revenue:,.0f}",
                "Target:%1.2M")
    kpi2.metric("Fulfilment Rate",f"{success_rate:,.1f}",
                "-2.4% vs Last Month",)
    kpi3.metric("Avg Distance",f"{avg_distance:,.2f}km",)
    kpi4.metric("Avg Rating",f"{avg_rating:,.1f}%")

    # column statistics
    if st.checkbox("Show Full Dataset"):
        st.dataframe(completed_ride,use_container_width=True)

    # column statistics
    st.subheader("column statistics")
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns

    if len(numeric_cols) > 0:
        selected_col = st.selectbox("Select Numeric Value", numeric_cols)
        st.write(df[selected_col].describe())
    st.divider()


# #TABLE
# # DOWNLOAD BUTTON
# csv = filtered_df.to_csv(index=False).encode('utf-8')
#
# st.download_button(
#     label="Download Filtered Data",
#     data=csv,
#     file_name="filtered_data.csv",
#     mime="text/csv"
# )