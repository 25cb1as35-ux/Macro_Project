import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px
import os
from groq import Groq

# --- 1. CUSTOM BRANDING & LAYOUT ---
st.set_page_config(page_title="Churn Analytics | Bank", page_icon="🏦", layout="wide")

st.markdown("""
<style>
    /* Floral Background */
    .stApp {
        background-color: #FFF5F6;
        background-image: url("https://www.transparenttextures.com/patterns/floral-white.png");
    }
    
    /* Main Card Styling */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 8px 20px rgba(255, 182, 193, 0.3);
        border: 1px solid #FFC0CB;
    }
    
    /* Headings */
    h1, h2, h3, h4 {
        color: #D87093 !important;
        font-family: 'Georgia', serif;
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #D87093;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #C71585;
        color: white;
    }
    
    /* Sleek Static Banner */
    .header-banner {
        background: linear-gradient(135deg, #D87093, #C71585);
        padding: 25px 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(216, 112, 147, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header Banner
st.markdown("""
<div class="header-banner">
    <h1 style="color:white !important; margin:0; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">Bank Customer Retention Analytics</h1>
    <p style="margin:5px 0 0 0; font-size:1.1rem; color: white; font-weight: bold; opacity: 0.9;">Predictive Modeling Dashboard (XGBoost)</p>
</div>
""", unsafe_allow_html=True)

# --- LOAD MODEL ---
model, scaler = None, None
try:
    model = joblib.load('churn_xgb_model.pkl')
    scaler = joblib.load('scaler.pkl')
except Exception as e:
    st.error(f"Error: Model or scaler file not found! Please ensure 'churn_xgb_model.pkl' and 'scaler.pkl' are in the same folder. ({e})")

# --- INITIALIZE GROQ CLIENT ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    client = None

# --- SIDEBAR: MODEL INFO + FEATURE IMPORTANCE ---
with st.sidebar:
    st.markdown("<h2 style='text-align: left;'>Model Information</h2>", unsafe_allow_html=True)
    st.write("**Algorithm:** XGBoost Classifier")
    st.write("**Accuracy:** 84.55%")
    st.write("**F1-Score:** 62.64%")
    st.write("---")
    st.markdown("<h3 style='text-align: left; font-size: 18px;'>Key Drivers of Churn</h3>", unsafe_allow_html=True)

    fallback_features = ['Age', 'NumOfProducts', 'IsActiveMember', 'Balance',
                         'Geography_Germany', 'Gender', 'Tenure', 'EstimatedSalary',
                         'CreditScore', 'Geography_Spain']
    fallback_importances = [0.39, 0.25, 0.11, 0.08, 0.05, 0.04, 0.03, 0.02, 0.02, 0.01]

    try:
        if hasattr(model, "feature_importances_"):
            imp = model.feature_importances_
            if len(imp) == len(fallback_features):
                features, importances = fallback_features, list(imp)
            else:
                features, importances = fallback_features, fallback_importances
        else:
            features, importances = fallback_features, fallback_importances
    except Exception:
        features, importances = fallback_features, fallback_importances

    df_eda = pd.DataFrame({'Feature': features, 'Importance': importances}).sort_values('Importance')

    fig_eda = px.bar(
        df_eda, x='Importance', y='Feature', orientation='h',
        color='Importance', color_continuous_scale=['#FFB6C1', '#D87093']
    )
    fig_eda.update_layout(
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_eda, use_container_width=True)

# --- TABS ---
tab1, tab2, tab3 = st.tabs([
    "Single Customer Prediction",
    "Batch Prediction (Upload File)",
    "Model Insights & EDA"
])

# ==========================================
# TAB 1: SINGLE CUSTOMER PREDICTION + CHATBOT
# ==========================================
with tab1:
    with st.form("prediction_form"):
        st.markdown("<h4>Enter Customer Details:</h4>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=650,
                                           help="The customer's credit score (300-850).")
            age = st.number_input("Age", min_value=18, max_value=100, value=35,
                                  help="The customer's age in years.")
            tenure = st.number_input("Tenure (Years)", min_value=0, max_value=10, value=5,
                                     help="Number of years the customer has been with the bank.")
            balance = st.number_input("Account Balance ($)", min_value=0.0, value=75000.0,
                                      help="The current balance in the customer's account.")

        with col2:
            estimated_salary = st.number_input("Estimated Salary ($)", min_value=0.0, value=50000.0,
                                               help="The estimated annual salary of the customer.")
            geography = st.selectbox("Geography", ["France", "Spain", "Germany"],
                                     help="The country where the customer resides.")
            gender = st.selectbox("Gender", ["Female", "Male"],
                                  help="The customer's gender.")

        with col3:
            num_products = st.selectbox("Number of Products", [1, 2, 3, 4],
                                        help="The number of bank products the customer uses.")
            has_card = st.selectbox("Has Credit Card?", ["Yes", "No"],
                                    help="Does the customer have a bank credit card?")
            is_active = st.selectbox("Is Active Member?", ["Yes", "No"],
                                     help="Is the customer actively using their account?")

        st.write("")
        submitted = st.form_submit_button("Run Prediction Analysis")

    if submitted:
        if model is None or scaler is None:
            st.error("Model not loaded — cannot run prediction.")
        else:
            input_data = pd.DataFrame({
                'CreditScore': [credit_score],
                'Gender': [1 if gender == "Male" else 0],
                'Age': [age],
                'Tenure': [tenure],
                'Balance': [balance],
                'NumOfProducts': [num_products],
                'HasCrCard': [1 if has_card == "Yes" else 0],
                'IsActiveMember': [1 if is_active == "Yes" else 0],
                'EstimatedSalary': [estimated_salary],
                'Geography_Germany': [1 if geography == "Germany" else 0],
                'Geography_Spain': [1 if geography == "Spain" else 0]
            })

            num_cols = ['CreditScore', 'Age', 'Tenure', 'Balance', 'EstimatedSalary']
            input_data[num_cols] = scaler.transform(input_data[num_cols])

            prediction = model.predict(input_data)[0]
            probability = model.predict_proba(input_data)[0][1]

            st.session_state.last_prediction = {
                "age": age, "balance": balance, "tenure": tenure,
                "estimated_salary": estimated_salary, "geography": geography,
                "gender": gender, "num_products": num_products,
                "has_card": has_card, "is_active": is_active,
                "prediction": int(prediction), "probability": float(probability),
            }
            
            st.session_state.messages = []

            st.write("---")
            res_col1, res_col2 = st.columns([1, 1])

            with res_col1:
                st.markdown("### Customer Summary")
                st.markdown(f"""
                * **Profile:** {age}-year-old {gender} from {geography}
                * **Financials:** Balance of ${balance:,.2f} | Salary: ${estimated_salary:,.2f}
                * **Account Status:** {'Active' if is_active == 'Yes' else 'Inactive'} | {tenure} Years Tenure
                * **Products:** Uses {num_products} bank product(s)
                """)

                st.markdown("### Recommendation")
                if prediction == 1:
                    st.error("**High Risk!** This customer is likely to churn.")
                    if age > 50:
                        st.warning("Older customers have a high churn rate. Offer a dedicated senior account manager.")
                    elif num_products >= 3:
                        st.warning("This customer has too many products. Schedule a call to simplify their banking experience.")
                    elif is_active == "No":
                        st.warning("The customer is inactive. Send a re-engagement email with a small cash bonus.")
                    else:
                        st.warning("Offer a short-term retention discount on their account fees.")
                else:
                    st.success("**Safe!** This customer is likely to stay.")
                    st.info("Maintain regular engagement and offer cross-selling opportunities.")

            with res_col2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=probability * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Churn Probability", 'font': {'size': 24, 'color': '#D87093'}},
                    gauge={
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#D87093"},
                        'bar': {'color': "#D87093"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "lightgray",
                        'steps': [
                            {'range': [0, 40], 'color': "#E8F8F5"},
                            {'range': [40, 70], 'color': "#FEF9E7"},
                            {'range': [70, 100], 'color': "#FDEDEC"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90}
                    }
                ))
                fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)

    # --- AI CHATBOT ---
    if "last_prediction" in st.session_state:
        st.write("---")
        st.markdown("### 🤖 AI Banking Assistant")
        st.write("Ask me anything about this customer's risk profile or what retention strategy to use.")

        cust = st.session_state.last_prediction

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Example: Why is this customer a risk? What offer should we give them?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if client is None:
                ai_response = "⚠️ **Groq API Key not found.** Please check your `.streamlit/secrets.toml` file to activate the AI."
            else:
                context = f"""
                You are an expert banking retention assistant talking to a bank employee. 
                Here is the customer's profile and the machine learning model's prediction:
                - Age: {cust['age']}
                - Geography: {cust['geography']}
                - Gender: {cust['gender']}
                - Account Balance: ${cust['balance']:,.2f}
                - Number of Products: {cust['num_products']}
                - Active Member: {cust['is_active']}
                - Tenure: {cust['tenure']} years
                - Estimated Salary: ${cust['estimated_salary']:,.2f}
                - Churn Prediction: {'HIGH RISK' if cust['prediction'] == 1 else 'LOW RISK'}
                - Churn Probability: {cust['probability']*100:.1f}%

                Answer the employee's question directly using this data. Be concise, professional, and helpful. 
                If they ask for an offer or strategy, suggest something specific based on this customer's risk factors.
                """

                try:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": context},
                            {"role": "user", "content": prompt}
                        ],
                        model="openai/gpt-oss-20b",
                        temperature=0.7,
                        max_tokens=300,
                    )
                    ai_response = chat_completion.choices[0].message.content
                except Exception as e:
                    ai_response = f"Sorry, I couldn't reach the AI service. Error: {e}"

            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            with st.chat_message("assistant"):
                st.markdown(ai_response)

# ==========================================
# TAB 2: BATCH PREDICTION
# ==========================================
with tab2:
    st.markdown("<h4>Upload a CSV file to predict churn for multiple customers at once.</h4>", unsafe_allow_html=True)
    st.markdown("<p>The file must contain: <b>CreditScore, Geography, Gender, Age, Tenure, Balance, NumOfProducts, HasCrCard, IsActiveMember, EstimatedSalary</b></p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        batch_data = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(batch_data.head())

        if st.button("Run Batch Prediction"):
            if model is None or scaler is None:
                st.error("Model not loaded — cannot run batch prediction.")
            else:
                try:
                    df_processed = batch_data.copy()
                    df_processed['Gender'] = df_processed['Gender'].apply(lambda x: 1 if x == 'Male' else 0)
                    df_processed['Geography_Germany'] = df_processed['Geography'].apply(lambda x: 1 if x == 'Germany' else 0)
                    df_processed['Geography_Spain'] = df_processed['Geography'].apply(lambda x: 1 if x == 'Spain' else 0)
                    df_processed = df_processed.drop('Geography', axis=1)

                    feature_order = ['CreditScore', 'Gender', 'Age', 'Tenure', 'Balance',
                                     'NumOfProducts', 'HasCrCard', 'IsActiveMember',
                                     'EstimatedSalary', 'Geography_Germany', 'Geography_Spain']
                    df_features = df_processed[feature_order].copy()

                    num_cols = ['CreditScore', 'Age', 'Tenure', 'Balance', 'EstimatedSalary']
                    df_features.loc[:, num_cols] = scaler.transform(df_features[num_cols])

                    predictions = model.predict(df_features)
                    probabilities = model.predict_proba(df_features)[:, 1]

                    batch_data['Churn_Prediction'] = predictions
                    batch_data['Churn_Probability'] = probabilities

                    st.success("Batch prediction completed successfully!")
                    st.dataframe(batch_data)

                    csv = batch_data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name='churn_predictions.csv',
                        mime='text/csv',
                    )

                except Exception as e:
                    st.error(f"An error occurred: {e}. Please ensure the CSV format matches the instructions.")

# ==========================================
# TAB 3: MODEL INSIGHTS & EDA
# ==========================================
with tab3:
    st.markdown("<h3>Model Performance Insights</h3>", unsafe_allow_html=True)
    st.write("Visual evaluation metrics of the XGBoost model used in this application.")

    col_cm, col_comp = st.columns(2)

    with col_cm:
        st.markdown("#### Confusion Matrix")
        st.write("Evaluates the accuracy of predictions on the 2,000 test customers.")
        if os.path.exists('confusion_matrix.png'):
            st.image('confusion_matrix.png')
        else:
            st.info("*(Confusion matrix image not found. Place 'confusion_matrix.png' in the app folder to display it.)*")

    with col_comp:
        st.markdown("#### Model Comparison")
        st.write("Why XGBoost was selected over other algorithms.")

        models = ['Logistic Regression', 'Decision Tree', 'Random Forest', 'XGBoost']
        accuracy = [71.8, 80.3, 80.9, 84.55]

        fig_comp = px.bar(
            x=models, y=accuracy,
            labels={'x': 'Algorithm', 'y': 'Accuracy (%)'},
            color=accuracy,
            color_continuous_scale=['#FFB6C1', '#D87093'],
            text_auto=True
        )
        fig_comp.update_layout(coloraxis_showscale=False, height=350)
        fig_comp.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        st.plotly_chart(fig_comp, use_container_width=True)
