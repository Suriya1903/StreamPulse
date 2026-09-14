import time

import pandas as pd
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StreamPulse | Fraud Analytics",
    page_icon="🛡️",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.7;
        margin-bottom: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🛡️ StreamPulse</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Real-Time Fraud Detection & Analytics Platform'
    '</div>',
    unsafe_allow_html=True,
)


st.caption(
    "Kafka → Spark Structured Streaming → ML → PostgreSQL → FastAPI"
)


# ============================================================
# API HELPER
# ============================================================

def get_api_data(endpoint):

    try:

        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=5,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException:

        return None


# ============================================================
# API HEALTH
# ============================================================

health = get_api_data("/health")


if health:

    st.success(
        "🟢 StreamPulse API is online"
    )

else:

    st.error(
        "🔴 StreamPulse API is unavailable. "
        "Please start FastAPI."
    )

    st.stop()


# ============================================================
# SUMMARY
# ============================================================

summary = get_api_data(
    "/fraud-summary"
)


if summary is None:

    st.error(
        "Unable to retrieve fraud analytics."
    )

    st.stop()


# ============================================================
# KPI SECTION
# ============================================================

st.header("📈 System Overview")


col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Total Transactions",
        f"{summary['total_transactions']:,}",
    )


with col2:

    st.metric(
        "Fraud Detected",
        f"{summary['fraudulent_transactions']:,}",
    )


with col3:

    st.metric(
        "Normal Transactions",
        f"{summary['normal_transactions']:,}",
    )


with col4:

    st.metric(
        "Fraud Rate",
        f"{summary['fraud_rate_percentage']:.2f}%",
    )


with col5:

    st.metric(
        "Avg Fraud Probability",
        f"{summary['average_fraud_probability']:.2%}",
    )


st.divider()


# ============================================================
# FETCH TRANSACTIONS
# ============================================================

transaction_data = get_api_data(
    "/transactions?limit=100"
)


if transaction_data is None:

    st.error(
        "Unable to retrieve transaction data."
    )

    st.stop()


transactions = transaction_data.get(
    "transactions",
    []
)


if transactions:

    df = pd.DataFrame(
        transactions
    )

else:

    df = pd.DataFrame()


# ============================================================
# RISK DISTRIBUTION
# ============================================================

st.header("🚦 Risk Distribution")


risk_summary = get_api_data(
    "/risk-summary"
)


if risk_summary:

    risk_df = pd.DataFrame(
        {
            "Risk Level": list(
                risk_summary.keys()
            ),
            "Transactions": list(
                risk_summary.values()
            ),
        }
    )

    col1, col2 = st.columns(2)

    with col1:

        st.bar_chart(
            risk_df.set_index(
                "Risk Level"
            )
        )

    with col2:

        st.dataframe(
            risk_df,
            use_container_width=True,
            hide_index=True,
        )

else:

    st.info(
        "No risk information available yet."
    )


st.divider()


# ============================================================
# TRANSACTION ANALYTICS
# ============================================================

if not df.empty:

    st.header("📊 Transaction Analytics")


    # --------------------------------------------------------
    # Convert timestamp
    # --------------------------------------------------------

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )


    # --------------------------------------------------------
    # Transaction volume over time
    # --------------------------------------------------------

    volume_df = (
        df.set_index("timestamp")
        .resample("1min")
        .size()
        .reset_index(name="Transactions")
    )


    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "Transaction Volume"
        )

        if not volume_df.empty:

            st.line_chart(
                volume_df.set_index(
                    "timestamp"
                )["Transactions"]
            )

        else:

            st.info(
                "Not enough data for a volume chart."
            )


    # --------------------------------------------------------
    # Fraud trend
    # --------------------------------------------------------

    fraud_trend_df = (
        df.assign(
            Fraud=df["fraud_prediction"]
        )
        .set_index("timestamp")
        .resample("1min")["Fraud"]
        .sum()
        .reset_index()
    )


    with col2:

        st.subheader(
            "Fraud Detection Trend"
        )

        if not fraud_trend_df.empty:

            st.line_chart(
                fraud_trend_df.set_index(
                    "timestamp"
                )["Fraud"]
            )

        else:

            st.info(
                "Not enough data for a fraud trend."
            )


    st.divider()


    # ========================================================
    # FRAUD BY MERCHANT
    # ========================================================

    st.subheader(
        "🏪 Fraud by Merchant"
    )


    merchant_df = (
        df.groupby("merchant")
        .agg(
            Total_Transactions=(
                "transaction_id",
                "count"
            ),
            Fraudulent_Transactions=(
                "fraud_prediction",
                "sum"
            ),
        )
        .reset_index()
    )


    merchant_df["Fraud_Rate"] = (
        merchant_df[
            "Fraudulent_Transactions"
        ]
        /
        merchant_df[
            "Total_Transactions"
        ]
        * 100
    )


    col1, col2 = st.columns(2)


    with col1:

        st.bar_chart(
            merchant_df.set_index(
                "merchant"
            )[
                "Fraudulent_Transactions"
            ]
        )


    with col2:

        display_merchant = merchant_df.copy()

        display_merchant[
            "Fraud_Rate"
        ] = display_merchant[
            "Fraud_Rate"
        ].round(2)

        st.dataframe(
            display_merchant,
            use_container_width=True,
            hide_index=True,
        )


    st.divider()


    # ========================================================
    # FRAUD BY LOCATION
    # ========================================================

    st.subheader(
        "📍 Fraud by Location"
    )


    location_df = (
        df.groupby("location")
        .agg(
            Total_Transactions=(
                "transaction_id",
                "count"
            ),
            Fraudulent_Transactions=(
                "fraud_prediction",
                "sum"
            ),
        )
        .reset_index()
    )


    location_df["Fraud_Rate"] = (
        location_df[
            "Fraudulent_Transactions"
        ]
        /
        location_df[
            "Total_Transactions"
        ]
        * 100
    )


    col1, col2 = st.columns(2)


    with col1:

        st.bar_chart(
            location_df.set_index(
                "location"
            )[
                "Fraudulent_Transactions"
            ]
        )


    with col2:

        display_location = location_df.copy()

        display_location[
            "Fraud_Rate"
        ] = display_location[
            "Fraud_Rate"
        ].round(2)

        st.dataframe(
            display_location,
            use_container_width=True,
            hide_index=True,
        )


    st.divider()


    # ========================================================
    # PAYMENT METHOD ANALYSIS
    # ========================================================

    st.subheader(
        "💳 Fraud by Payment Method"
    )


    payment_df = (
        df.groupby("payment_method")
        .agg(
            Total_Transactions=(
                "transaction_id",
                "count"
            ),
            Fraudulent_Transactions=(
                "fraud_prediction",
                "sum"
            ),
        )
        .reset_index()
    )


    payment_df["Fraud_Rate"] = (
        payment_df[
            "Fraudulent_Transactions"
        ]
        /
        payment_df[
            "Total_Transactions"
        ]
        * 100
    )


    st.bar_chart(
        payment_df.set_index(
            "payment_method"
        )[
            "Fraudulent_Transactions"
        ]
    )


    st.dataframe(
        payment_df,
        use_container_width=True,
        hide_index=True,
    )


    st.divider()


    # ========================================================
    # TRANSACTION AMOUNT ANALYSIS
    # ========================================================

    st.subheader(
        "💰 Transaction Amount Analysis"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Average Amount",
            f"₹{df['amount'].mean():,.2f}",
        )


    with col2:

        st.metric(
            "Maximum Amount",
            f"₹{df['amount'].max():,.2f}",
        )


    with col3:

        fraud_amount = df.loc[
            df["fraud_prediction"] == 1,
            "amount",
        ]

        if not fraud_amount.empty:

            st.metric(
                "Avg Fraud Amount",
                f"₹{fraud_amount.mean():,.2f}",
            )

        else:

            st.metric(
                "Avg Fraud Amount",
                "₹0",
            )


st.divider()


# ============================================================
# RECENT FRAUD
# ============================================================

st.header(
    "🚨 Recent Fraudulent Transactions"
)


fraud_data = get_api_data(
    "/recent-fraud?limit=10"
)


if fraud_data and fraud_data.get(
    "transactions"
):

    fraud_df = pd.DataFrame(
        fraud_data["transactions"]
    )


    fraud_df = fraud_df.rename(
        columns={
            "transaction_id":
                "Transaction ID",

            "customer_id":
                "Customer",

            "amount":
                "Amount",

            "location":
                "Location",

            "merchant":
                "Merchant",

            "fraud_probability":
                "Fraud Probability",

            "risk_level":
                "Risk",

            "timestamp":
                "Timestamp",
        }
    )


    fraud_df["Amount"] = (
        fraud_df["Amount"]
        .round(2)
    )


    fraud_df["Fraud Probability"] = (
        fraud_df["Fraud Probability"]
        .round(4)
    )


    st.dataframe(
        fraud_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.success(
        "No fraudulent transactions detected."
    )


st.divider()


# ============================================================
# RECENT TRANSACTIONS
# ============================================================

st.header(
    "📋 Recent Transactions"
)


if not df.empty:

    display_df = df.copy()


    display_df = display_df.rename(
        columns={
            "transaction_id":
                "Transaction ID",

            "customer_id":
                "Customer",

            "amount":
                "Amount",

            "location":
                "Location",

            "merchant":
                "Merchant",

            "payment_method":
                "Payment Method",

            "device":
                "Device",

            "timestamp":
                "Timestamp",

            "fraud_prediction":
                "Fraud Prediction",

            "fraud_probability":
                "Fraud Probability",

            "risk_score":
                "Risk Score",

            "risk_level":
                "Risk Level",
        }
    )


    display_df["Amount"] = (
        display_df["Amount"]
        .round(2)
    )


    display_df["Fraud Probability"] = (
        display_df["Fraud Probability"]
        .round(4)
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No transactions available."
    )


# ============================================================
# AUTO REFRESH
# ============================================================

st.divider()


st.caption(
    "🔄 Dashboard automatically refreshes every 5 seconds."
)


time.sleep(5)

st.rerun()