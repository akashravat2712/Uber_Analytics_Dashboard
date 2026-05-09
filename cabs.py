import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px


st.set_page_config("Uber Analytics",layout="wide")
df=pd.read_csv("uber_data.csv")

#SIDEBAR
with st.sidebar:
    selected=option_menu("Main Menu",["Dataset","Overview","Ride Analytics","Data Assistant"],
                         icons=["table","bar-chart","graph-up",],menu_icon="car-front",default_index=0)

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
    total_rides=len(df)
    total_revenue=df["Booking Value"].sum()

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

    #Operatonal Efficiency
    col_eff,col_can=st.columns(2)
    with col_eff:
        st.subheader("Operational efficiency")
        eef_df=df.groupby("Vehicle Type")[["Avg VTAT","Avg CTAT"]].mean()
        st.write("Average Turn Arround Time(In Minutes)")
        st.dataframe(eef_df.style.highlight_max(axis=0,color="#d81416").highlight_min(axis=0,color="#e6ed6f"),use_container_width=True)

        with col_can:
            st.subheader("Cancellation Audit")
            status_count=df["Booking Status"].value_counts().to_frame(name="Count")
            status_count["Share %"]=(status_count["Count"]/total_rides*100)
            st.dataframe(status_count,use_container_width=True)

    #Financial Deep Dive
    st.header("Financial Deep Dive")
    pay_col,reason_col=st.columns([4,6])

    #Payment Analysis
    completed_ride=(df["Booking Status"]=="Completed").sum()
    with pay_col:
        st.markdown("**Payment Method Overview")
        pay_summary=(df["Payment Method"].value_counts(normalize=True)*100)
        st.dataframe(pay_summary.rename("% Usage"),use_container_width=True)
    with reason_col:
        st.markdown("**Primary Cancellation Trigger")
        cust_reason=(df["Reason for cancelling by Customer"].dropna().value_counts().head(3))
        drv_reason=(df["Driver Cancellation Reason"].dropna().value_counts().head(3))
        cust_reason.index="Customer:"+cust_reason.index
        drv_reason.index="Driver:"+drv_reason.index

        reason_df=pd.concat([cust_reason,drv_reason]).to_frame()
        reason_df.columns=["Incident Found"]
        st.dataframe(reason_df)

    #Data Quality
    with st.expander("Data Quality & Audit Logs"):
        audit1,audit2=st.columns(2)
        audit1.write(f"Duplicate Records:{df.duplicated().sum()}")
        audit2.write(f"Missing Values:{df["Booking Value"].isna().sum()}")
        st.info("Missing Booking Values are Expacted for Cancelled ride or no-driver found")
        st.success("Executive Overview Generated From Operational Dataset")

    st.title("Uber Operation")
    st.markdown("---")

    #Strategic KPI Layer
    completed_ride=df[df["Booking Status"]=="Completed"]
    total_revenue=completed_ride["Booking Value"].sum()
    avg_distance=completed_ride["Ride Distance"].mean()
    success_rate=(len(completed_ride)/total_rides*100 if total_rides>0 else 0)
    avg_rating=completed_ride["Customer Rating"].dropna().mean()

    kpi1,kpi2,kpi3,kpi4=st.columns(4)
    kpi1.metric("Gross Total Revenue",f"{total_revenue:,.0f}","Target:%1.2M")
    kpi2.metric("Fulfilment Rate",f"{success_rate:,.1f}","-2.4% VS Last Month")
    kpi3.metric("Avg Distance",f"{avg_distance:,.2f}Km")
    kpi4.metric("Avg Rating",f"{avg_rating:.1f}")

    #Show Full dataset
    if st.checkbox("Show Full dataset"):
        st.dataframe(completed_ride,use_container_width=True)

    #Column Statistics
    st.header("Column Statistics")
    numeric_cols=df.select_dtypes(include=["int64","float64"]).columns

    if len(numeric_cols)>0:
        selected_col=st.selectbox("Select Numeric Value",numeric_cols)
        st.write(df[selected_col].describe())
    st.divider()
if selected=="Ride Analytics":
    st.title("Advance Ride Intelligence Dashboard")
    st.divider()

    completed=df[df["Booking Status"]=="Completed"]

    #Sunburst Chart
    st.subheader("Revenue Hierarchy")
    fig1=px.sunburst(completed,path=["Vehicle Type","Payment Method"],values="Booking Value",color="Booking Value",color_continuous_scale="Turbo")
    fig1.update_layout(height=500)
    st.plotly_chart(fig1)
    st.divider()

    #Treemap
    st.subheader("Revenue Distribution")
    fig2=px.treemap(completed,path=["Vehicle Type","Payment Method"],
                    values="Booking Value",
                    color="Booking Value",
                    color_continuous_scale="Blues")
    fig2.update_layout(margin=dict(t=20,l=0,r=0,b=0),height=420)
    st.plotly_chart(fig2,use_container_width=True)

    st.subheader("Customer rating Spread")
    fig3=px.box(completed,x="Vehicle Type",y="Customer Rating",color="Vehicle Type")
    fig3.update_layout(showlegend=True,height=420)
    st.plotly_chart(fig3)
    st.divider()

    #Sankey Chart
    st.subheader("Ride Flow Analysis")
    flow=df.groupby(["Vehicle Type","Booking Status"]).size().reset_index(name="count")
    source_label=flow["Vehicle Type"].unique().tolist()
    target_label=flow["Booking Status"].unique().tolist()

    labels=source_label+target_label

    source=flow["Vehicle Type"].apply(
        lambda x:labels.index(x)
    ).tolist()
    target=flow["Booking Status"].apply(
        lambda x:labels.index(x)
    ).tolist()
    value=flow["count"].tolist()

    import plotly.graph_objects as go
    fig4=go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="blue",width=0.5),label=labels
                  ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])
    fig4.update_layout(height=500)
    st.plotly_chart(fig4)
    st.divider()

    #Ride Demand by vehicle Type
    st.subheader(" Ride Demand by Vehicle Type")
    demand=df["Vehicle Type"].value_counts().reset_index()
    demand.columns=["Vehicle Type","Total Bookings"]
    fig5 = px.bar(demand, x="Vehicle Type", y="Total Bookings",
                  title="Ride Demand by vehicle Type",color="Vehicle Type")
    st.plotly_chart(fig5,use_container_width=True)
    st.divider()

    # Revenue by Vehicle Type
    st.subheader("Revenue by Vehicle Type")
    revenue = df.groupby(["Vehicle Type","Booking Status"]).sum().reset_index()
    fig6 = px.bar(revenue, x="Booking Value", y="Vehicle Type",
                   title="Revenue by Vehicle Type",orientation="h",color="Vehicle Type")
    st.plotly_chart(fig6,use_container_width=True)
    st.divider()

    # Donut Chart
    st.subheader("Booking Status Distribution")
    status = df["Booking Status"].value_counts().reset_index()
    status.columns=["Status","Count"]
    fig7 = px.pie(status, names="Status", values="Count", hole=0.4)
    st.plotly_chart(fig7,use_container_width=True)
    st.divider()

    # Pie Chart
    st.subheader("Payment Method Usage")
    Payment=df["Payment Method"].value_counts().reset_index()
    Payment.columns=["Method","Count"]
    fig8 = px.pie(Payment, names="Method", values="Count")
    st.plotly_chart(fig8,use_container_width=True)
    st.divider()

    # Ride Distance vs Booking Value
    st.subheader("Ride Distance vs Booking Value")
    fig9 = px.scatter(df, x="Ride Distance", y="Booking Value", color="Vehicle Type")
    st.plotly_chart(fig9,use_container_width=True)
    st.divider()

    # Customer Rating Distribution
    st.subheader("Customer Rating Distribution")
    fig10 = px.histogram(df, x="Customer Rating",nbins=10)
    st.plotly_chart(fig10,use_container_width=True)
    st.divider()

    # Cancellation Reasons Analysis
    st.subheader("Cancellation Reasons Analysis")
    cancel_reason = pd.concat([
        df["Reason for cancelling by Customer"],
        df["Driver Cancellation Reason"]
    ]).dropna().value_counts().reset_index()
    cancel_reason.columns = ["Cancellation Reason", "Count"]
    fig11 = px.bar(cancel_reason.head(10), x="Count", y="Cancellation Reason", orientation="h")
    st.plotly_chart(fig11, use_container_width=True)
    st.divider()

    # Average Distance by Vehicle Type
    st.subheader("Average Distance by Vehicle Type")
    avg_dist = df.groupby("Vehicle Type")["Ride Distance"].mean().reset_index()
    fig12 = px.bar(avg_dist, x="Vehicle Type", y="Ride Distance",
                  title="Average Distance by Vehicle Type", color="Vehicle Type")
    st.plotly_chart(fig12, use_container_width=True)
    st.divider()

    # Booking Value Distribution
    st.subheader("Booking Value Distribution")
    fig13 = px.histogram(df, x="Booking Value",nbins=10, color="Vehicle Type")
    st.plotly_chart(fig13, use_container_width=True)
    st.divider()

    # Operational Efficiency (CTAT vs VTAT)
    st.subheader("Operational Efficiency (CTAT vs VTAT)")
    fig14 = px.scatter(df, x="Avg CTAT",y="Avg VTAT",color="Avg VTAT")
    st.plotly_chart(fig14, use_container_width=True)
    st.divider()

if selected == "Data Assistant":
    st.title("Data Assistant")
    st.divider()

    st.write("Ask Question about the dataset and get visual analysis")
    user_question = st.text_input("Ask me question")

    if user_question:
        q = user_question.lower()

        completed = df[df["Booking Status"] == "Completed"]

        # Total Rides
        if "total rides" in q:
            total = len(df)
            st.success(f"Total Rides in Dataset: {total}")

            status = df["Booking Status"].value_counts()
            fig1 = px.bar(x=status.index,
                          y=status.values,
                          labels={"x": "Booking Status", "y": "Ride Count"},
                          title="Ride Distribution by Status")
            st.plotly_chart(fig1, use_container_width=True)

        # revenue analysis

        elif "revenue" in q:
            revenue = completed.groupby("Vehicle Type")["Booking Value"].sum()
            st.success(f"Total Revenue: {revenue.sum():,.2f}")

            fig2 = px.bar(x=revenue.index,
                          y=revenue.values,
                          title="Revenue by Vehicle Type",
                          labels={"x": "Vehicle Type", "y": "Booking Value"})
            st.plotly_chart(fig2, use_container_width=True)

         # vehicle
        elif "vehicle" in q:
            vehicle = df["Vehicle Type"].value_counts()
            st.success(f"Most Used Vehicle: {vehicle.idxmax()}")
            fig3 = px.pie(names=vehicle.index, values=vehicle.values,
                          title="Vehicle Usage Distribution")
            st.plotly_chart(fig3)

        # Payment analysis
        elif "payment" in q:
            payment = df["Payment Method"].value_counts()
            fig4 = px.pie(names=payment.index,
                          values=payment.values,
                          title="Payment Method")
            st.plotly_chart(fig4, use_container_width=True)

        # Cancellation
        elif "cancel" in q:
            cancel = df["Booking Status"].value_counts()
            fig5 = px.bar(x=cancel.index,
                          y=cancel.values,
                          title = "Ride Status",
                          labels={"x": "Booking Status", "y": "Ride Count"})
            st.plotly_chart(fig5, use_container_width=True)

        # rating analysis
        elif "rating" in q:
            fig6 = px.histogram(completed, x="Customer Rating",nbins=10,title="Customer Rating")
            st.plotly_chart(fig6, use_container_width=True)
            st.success(f"Average Rating {completed["Customer Rating"].mean():,.1f}")

        # distance analysis
        elif "distance" in q:
            fig7 = px.scatter(completed, x="Ride Distance",y="Booking Value",
                              title="Ride Distance vs Booking Value",color="Vehicle Type")
            st.plotly_chart(fig7, use_container_width=True)
            st.success(f"Average Distance {completed['Ride Distance'].mean():,.2f}km")

        else:
            st.warning("Question not recognized please ask question from cancellation, vehicle, revenue etc")





