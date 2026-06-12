import streamlit as st
import pandas as pd #processing data
import base64 #converts bytes to base64
import database as db #our database!
from streamlit_card import card #library w/ card capabilities
import scoring as sc #imports scoring file

#CSS for the piggy loader
loader = st.markdown("""
<style>
.full-center {
    display: absolute;
    top: 0px;
    bottom: 0px;
    left: 0px;
    right: 0px;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
                
.pig-loader-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

.pig {
    position: relative;
    width: 150px;
    height: 150px;
}

.pig-body {
    width: 100%;
    height: 100%;
    background: pink;
    border-radius: 50%;
    position: relative;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
}

.pig-nose {
    position: absolute;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 55px;
    height: 40px;
    background: #ffb3c6;
    border-radius: 50%;
    border: 3px solid #d3819f;
    animation: spin 1s linear infinite;
    display: flex;
    justify-content: center;
    align-items: center;
}

.pig-nostril {
    width: 12px;
    height: 18px;
    background: #d3819f;
    border-radius: 50%;
    top: 45%;
    margin: 0 5px;
}

.pig-ear-left, .pig-ear-right {
    width: 45px;
    height: 45px;
    background: pink;
    position: absolute;
    top: -10px;
    border-radius: 50%;
    transform: rotate(20deg);
}

.pig-ear-left {
    left: 5px;
}

.pig-ear-right {
    right: 5px;
    transform: rotate(-20deg);
}

.pig-eye {
    width: 18px;
    height: 18px;
    background: black;
    border-radius: 50%;
    position: absolute;
    top: 25%;
}

.pig-eye-left { left: 35%; }
.pig-eye-right { right: 35%; }

@keyframes spin {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}
</style>

 <div class="full-center">
    <div class="pig-loader-container">
        <div class="pig">
            <div class="pig-ear-left"></div>
            <div class="pig-ear-right"></div>
            <div class="pig-body"></div>
            <div class="pig-eye pig-eye-left"></div>
            <div class="pig-eye pig-eye-right"></div>
            <div class="pig-nose">
                <div class="pig-nostril"></div>
                <div class="pig-nostril"></div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

loader.empty()

# Initialize session state (what page ur on)
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'reset_feedback' not in st.session_state:
    st.session_state.reset_feedback = None

# --- Initialize session state for settings toggle ---
if 'show_settings' not in st.session_state:
    st.session_state.show_settings = False

# --- Function to render the settings button and sidebar ---
def render_settings_button():
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("⚙️", key="settings_button"):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()

    if st.session_state.show_settings:
        with st.sidebar:
            st.header("⚙️")
            st.selectbox("Theme", ["Light", "Dark"], key="theme_choice")
            st.slider("Font Size", 10, 30, 16, key="font_size")
            st.checkbox("Show Debug Info", key="debug_info")

#tab styling that applies to the whole website
st.markdown("""
    <style>
    /* Target all tab buttons */
    .stTabs [data-baseweb="tab-list"] button {
        color: #999999 !important;
    }
    
    /* Active tab - pink text */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #fc7eff !important;
    }
    
    /* Target the paragraph inside active tab */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
        color: #fc7eff !important;
    }
    
    /* Target any div/span text inside active tab */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] div,
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] span {
        color: #fc7eff !important;
    }
    
    /* Pink underline for active tab */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        border-bottom: 3px solid #fc7eff !important;
    }
    
    /* Remove default highlight */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #fc7eff !important;
    }
    
    /* Hover effect */
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: #fc7eff !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover p {
        color: #fc7eff !important;
    }
                /* CENTER THE TABS */
            .stTabs [data-baseweb="tab-list"] {
                display: flex !important;
                justify-content: center !important;
                width: 100% !important;
            }

            div[data-testid="stTabs"] {
                text-align: center;
            }
        </style>
    </style>
""", unsafe_allow_html=True)

# ========== WELCOME PAGE (Public Landing) ==========
st.set_page_config(layout="wide")
if st.session_state.page == 'welcome':
    
    # Function to convert images
    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    
    # Convert your existing background image
    bg1 = get_base64_image("background.jpg")
    bg2 = get_base64_image("background2.jpg")
    
    # CSS for landing page (FIX not done w this)
    st.markdown(f"""
        <style>
            /*Fonts*/
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');
            
            /* Remove Streamlit's padding */
            .main, .block-container {{
                padding: 0 !important;
                margin: 0 !important;
            }}
            html, body, .stApp, .main, .block-container {{
                background-color: transparent !important;
                padding: 0 !important;
                margin: 0 !important;
            }}
            
            /* Remove ALL gaps and spacing */
            .element-container {{
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            div[data-testid="stVerticalBlock"] {{
                gap: 0 !important;
            }}
            
            /* Style the text content on landing page*/
            .welcome-content {{
                height: 100vh;
                width: 100vw;

                background-image: url('data:image/jpeg;base64,{bg1}');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;

                display: flex;
                flex-direction: column;
                justify-content: center;

                padding-left: 3rem;
                margin: 0;
            }}
            
            .welcome-content h1 {{
                font-size: 50px;
                font-weight: 700;
                color: #ffffff !important;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                margin-bottom: 0px;
                font-family: 'Poppins', sans-serif;

            }}
            .welcome-content h1 a {{
                display: none;
            }}
            
            .welcome-content p {{
                font-size: 15px;
                color: #ffffff;
                margin-top: 0px;
                margin-bottom: 0px;
                max-width: 600px;
                font-family: 'Poppins', sans-serif;
                font-weight: 400;
            }}
            
            /* Pull button up AND collapse its space */
            .stButton {{
                margin-top: -38vh !important;
                margin-bottom: -100px !important;
                margin-left: 3rem !important;
                display: block !important;
                padding: 0 !important;
            }}
            
            .stButton > button {{
                background-color: #ffffff !important;
                color: #333333 !important;
                padding: 10px 30px !important;
                font-size: 20px !important;
                border: none !important;
                border-radius: 5px !important;
                cursor: pointer !important;
                font-family: 'Poppins', sans-serif !important;
                display: block !important;
            }}
            
            .stButton > button:hover {{
                background-color: #f0f0f0 !important;
                transform: scale(1.05) !important;
                box-shadow: 0 0 20px rgba(255, 182, 193, 0.9), 0 0 40px rgba(255, 192, 203, 0.6) !important;
            }}

            /* Card section styling */
            .card-section {{
                background-image: url('data:image/png;base64,{bg2}');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                height: 100vh;
                width: 100vw;
                padding: 4rem 3rem !important;
                margin: 0 !important;
                display: block;
            }}
            
            .card-section-title {{
                font-family: 'Poppins', sans-serif;
                font-size: 36px;
                font-weight: 600;
                color: #2d2d2d;
                margin-bottom: 0.5rem;
            }}
            
            .card-section-subtitle {{
                font-family: 'Poppins', sans-serif;
                font-size: 14px;
                font-weight: 400;
                color: #8a8a8a;
                max-width: 500px;
                margin-bottom: 3rem;
                line-height: 1.6;
            }}
            
            /* Cards container */
            .cards-container {{
                display: flex;
                gap: 1.5rem;
                justify-content: flex-start;
                flex-wrap: wrap;
            }}
            
            /* Individual card */
            .info-card {{
                background-color: white;
                border-radius: 12px;
                padding: 2rem;
                width: 280px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                position: relative;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            
            .info-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
            }}
            
            /* Card icon */
            .card-icon {{
                position: absolute;
                top: 1.5rem;
                right: 1.5rem;
                font-size: 32px;
                color: #ff9b9b;
            }}
            
            /* Card title */
            .card-title {{
                font-family: 'Poppins', sans-serif;
                font-size: 18px;
                font-weight: 600;
                color: #000000 !important;
                margin-bottom: 0.8rem;
                padding-right: 40px;
            }}
            
            /* Card description */
            .card-description {{
                font-family: 'Poppins', sans-serif;
                font-size: 13px;
                font-weight: 400;
                color: #7a7a7a;
                line-height: 1.6;
            }}
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"""
        <div class="welcome-content">
            <h1>Poor spending habits?</h1>
            <p>Piggy Point helps you understand and improve your spending habits by analyzing your financial data.</p>
        </div>
        """, unsafe_allow_html=True)

        # Button inside first page
        if st.button("Get Started", key="final-signup"):
            st.session_state.page = "signup"
            st.rerun()

#about page
    st.markdown("""
    <div class="card-section">
    <h2 class="card-section-title">Piggy point aims to better your financial situation with these three simple solutions</h2>

    <div class="cards-container">
    <div class="info-card">
    #<div class="card-icon"></div>
    <h3 class="card-title">Personalized spending score</h3>
    <p class="card-description">put description</p>
    </div>

    <div class="info-card">
    #<div class="card-icon"> </div>
    <h3 class="card-title">Target spending</h3>
    <p class="card-description">Add description</p>
    </div>

    <div class="info-card">
    #<div class="card-icon"></div>
    <h3 class="card-title">Graphs</h3>
    <p class="card-description">add description</p>
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ========== Signup/Login PAGE ==========
elif st.session_state.page in ['signup', 'initialization']:
    #styling for the signup/login page
    st.markdown("""
        <style>
                
        /* Background */
        .stApp {
            background-color: #fdeaff;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='152' height='152' viewBox='0 0 152 152'%3E%3Cg fill-rule='evenodd'%3E%3Cg id='temple' fill='%23f6b8f4' fill-opacity='0.36'%3E%3Cpath d='M152 150v2H0v-2h28v-8H8v-20H0v-2h8V80h42v20h20v42H30v8h90v-8H80v-42h20V80h42v40h8V30h-8v40h-42V50H80V8h40V0h2v8h20v20h8V0h2v150zm-2 0v-28h-8v20h-20v8h28zM82 30v18h18V30H82zm20 18h20v20h18V30h-20V10H82v18h20v20zm0 2v18h18V50h-18zm20-22h18V10h-18v18zm-54 92v-18H50v18h18zm-20-18H28V82H10v38h20v20h38v-18H48v-20zm0-2V82H30v18h18zm-20 22H10v18h18v-18zm54 0v18h38v-20h20V82h-18v20h-20v20H82zm18-20H82v18h18v-18zm2-2h18V82h-18v18zm20 40v-18h18v18h-18zM30 0h-2v8H8v20H0v2h8v40h42V50h20V8H30V0zm20 48h18V30H50v18zm18-20H48v20H28v20H10V30h20V10h38v18zM30 50h18v18H30V50zm-2-40H10v18h18V10z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            background-size: 300px 300px;  /* Add this to make it bigger */
        }
        
        /* Card styling - controls the card dimensions */
        .stTabs, [data-testid="stVerticalBlock"][overflow="visible"]:has(.card-marker) {
            background-color: #1a1a2e;
            border-radius: 40px;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.5);
            padding: 90px 80px;
            height: 750px !important; /* Controls card height */
            overflow-y: auto !important; /* Adds scrollbar if content overflows */
        }
                
        h1 {
            font-size: 28px !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            margin-bottom: 40px !important;
            text-align: center;
        }
                
        .stTextInput > div > div > input:focus-visible {
            border: 2px solid #fc7eff !important;
            box-shadow: 0 0 0 3px rgba(252, 126, 255, 0.2) !important;
            outline: none !importnant;
        }
                
        .stButton > button {
            font-size: 16px !important;
            height: 52px !important;
            background: linear-gradient(135deg, #fc7eff 0%, #e645f0 100%) !important;
            border: none !important;
            color: white !important;
            border-radius: 25px !important;
            margin-top: 30px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(252, 126, 255, 0.3);
            transition: all 0.3s ease !important;
            cursor: pointer !important;
            width: 100% !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(252, 126, 255, 0.5);
            background: linear-gradient(135deg, #e645f0 0%, #d030e0 100%) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    #actual content for the login page

    # Back button
    if st.button("← Back to Home", key="back_home"):
        st.session_state.page = 'welcome'
        st.rerun()

    if st.session_state.page == 'signup':
        # Tabs
        tab1, tab2 = st.tabs(["Sign up", "Login"])

        with tab1: 
            st.title("Create an account with Piggy Point!")
            new_username = st.text_input("Choose a Username", placeholder="Username", key="new_user")
            new_password = st.text_input("Choose a Password", type="password", placeholder="Password", key="new_pass")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm Password", key="confirm_pass")
            
            if st.button("Sign Up", use_container_width=True, key="signup_btn"):
                if not new_username or not new_password:
                    st.error("Please fill in all fields")
                elif db.user_exists(new_username):
                    st.error("Username already exists")
                elif new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    if db.create_user(new_username, new_password):
                        st.success("Account created successfully!")
                        st.session_state.logged_in = True
                        st.session_state.username = new_username
                        st.session_state.page = 'initialization'
                        st.rerun()
                    else:
                        st.error("Error creating account")

        with tab2:           
            st.title("Login to your Piggy Point account!")
            username = st.text_input("Username", placeholder="Type your username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Type your password", key="login_pass")
            
            if st.button("Login", use_container_width=True, key="login_btn"):
                if db.verify_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    #spending targets page
    else:
        card = st.container()

        with card:
            st.subheader("Enter your spending targets")
            targets = {
                category: st.number_input(
                    category,
                    min_value=0.0,
                    step=1.0,
                    value=0.0
                ) for category in sc.categories
            }

            if st.button(label="Continue"):
                if db.save_user_targets(st.session_state.username, targets):
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Error creating account")


            st.write("""<div class='card-marker'/>""", unsafe_allow_html=True)
                
# ========== DASHBOARD PAGE ==========
elif st.session_state.page == 'dashboard':
    # --- Top-right area: Settings + Logout buttons ---
    # Three columns: content spacer + two action buttons
    spacer, col_settings, col_logout = st.columns([10, 1, 1])
    with col_settings:
        if st.button("⚙️", key="settings_button", use_container_width=True):
            st.session_state.page = 'settings'
            st.rerun()
    with col_logout:
        if st.button("Logout", key="logout_button", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.page = 'welcome'
            st.rerun()

    # Settings sidebar removed in favor of a dedicated page

    # --- Logo placement section ---
    # Display centered logo image

    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    logo_base64 = get_base64_image("logo.png")

    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <img src="data:image/png;base64,{logo_base64}" width="300">
        </div>
    """, unsafe_allow_html=True)




    #Tabs
    tab1, tab2, tab3 = st.tabs(["Dashboard", "User Input", "Summary"])

    with tab1:
        col1, col2 = st.columns([2,3])
        with col1:
            st.header("Dashboard")
            st.write("Welcome to your Dashboard!")

    with col2:
        with st.container(border=True):
            st.markdown("### Monthly Savings")
            
            data = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                'Savings': [500, 750, 600, 900, 850]
            })
            
            st.line_chart(data.set_index('Month'), color='#fc7eff')

    with tab2:

        col1, col2 = st.columns([1,1])
        with col1:
            with st.container(border=True):
                st.subheader("User Input")
                # First choose: Income or Expense
                transaction_type = st.selectbox(
                    "What are you recording?",
                    ["Income", "Expense"]
                )
                
                # Categories change based on type
                if transaction_type == "Income":
                    category = st.selectbox(
                        "Income Category",
                        ["Salary", "Investment/Savings", "Gift", "Other"]
                    )
                    amount = st.number_input("Amount ($)", min_value=0.0, step=10.0)
                    
                else:  # Expense
                    category = st.selectbox(
                        "Expense Category",
                        sc.categories
                    )
                    amount = st.number_input("Expense Amount ($)", min_value=0.0, step=10.0)
                
                if st.button("Record Transaction", use_container_width=True):
                    if amount <= 0:
                        st.error("Amount must be greater than 0")
                    else:
                        transaction_data = {
                            'transaction_type': transaction_type,
                            'category': category,
                            'amount': amount
                        }
                        if db.save_user_transactions(st.session_state.username, transaction_data):
                            st.success(f"Recorded {transaction_type}: ${amount} for {category}")

                            # Auto-update targets whenever income is added or changed
                            if transaction_type == "Income":
                                # Calculate total income
                                user_data = db.get_user_transactions(st.session_state.username)
                                transactions = user_data.get('transactions', [])
                                total_income = sum(t['amount'] for t in transactions if t['transaction_type'] == 'Income')

                                # Set targets based on income and weights
                                new_targets = {
                                    cat: total_income * sc.weights[cat] for cat in sc.categories
                                }
                                db.save_user_targets(st.session_state.username, new_targets)
                                st.info(f"Auto-updated spending targets based on total income of ${total_income:.2f}")
                        else:
                            st.error("Failed to save transaction")
            with col2:
                def handle_reset(label, reset_fn):
                            """Run a reset action, stash feedback, and refresh the dashboard."""
                            if reset_fn(st.session_state.username):
                                # Recalculate targets if income was reset
                                if "Income" in label or "All" in label:
                                    user_data = db.get_user_transactions(st.session_state.username)
                                    transactions_updated = user_data.get('transactions', [])
                                    total_income = sum(t['amount'] for t in transactions_updated if t['transaction_type'] == 'Income')

                                    # Update targets based on new total income
                                    new_targets = {
                                        cat: total_income * sc.weights[cat] for cat in sc.categories
                                    }
                                    db.save_user_targets(st.session_state.username, new_targets)

                                st.session_state.reset_feedback = f"{label} reset complete."
                                st.rerun()
                            else:
                                st.error(f"Failed to reset {label.lower()}.")
                # Transaction History section
                #Reset all button
                header_col, action_col = st.columns([0.80, 0.20])
                with header_col:
                        st.subheader("Transaction History")
                with action_col:
                        manage_trigger = getattr(st, "popover", None)
                        if manage_trigger:
                            menu = manage_trigger("Manage Data", use_container_width=True)
                        else:
                            menu = st.expander("Manage Data", expanded=False)

                        with menu:
                            st.caption("Reset stored totals for this account.")
                            if st.button("Total Income Reset", use_container_width=True, key="btn_reset_income"):
                                handle_reset("Total Income", db.reset_total_income)
                            if st.button("Total Expenses Reset", use_container_width=True, key="btn_reset_expense"):
                                handle_reset("Total Expenses", db.reset_total_expenses)
                            if st.button("All Reset", use_container_width=True, key="btn_reset_all"):
                                handle_reset("All data", db.reset_all_transactions)

                # Fetch user transactions
                user_data = db.get_user_transactions(st.session_state.username)
                transactions = user_data.get('transactions', [])
                if transactions:
                    #Display transactions with delete buttons
                    for transaction in transactions:
                        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                        
                        with col1:
                            date_str = transaction.get('date', 'N/A')
                            if isinstance(date_str, str):
                                st.write(date_str[:10])
                            else:
                                st.write(str(date_str)[:10])
                        with col2:
                            st.write(transaction.get('transaction_type', 'N/A'))
                        with col3:
                            st.write(transaction.get('category', 'N/A'))
                        with col4:
                            st.write(f"${transaction.get('amount', 0):.2f}")
                        with col5:
                            # Use the transaction ID to delete
                            transaction_id = transaction.get('id')
                            transaction_type_to_delete = transaction.get('transaction_type')
                            if st.button("🗑️", key=f"delete_{transaction_id}"):
                                if db.delete_transaction_by_id(transaction_id):
                                    st.success("Transaction deleted!")

                                    # Recalculate targets if an income transaction was deleted
                                    if transaction_type_to_delete == "Income":
                                        user_data = db.get_user_transactions(st.session_state.username)
                                        transactions_updated = user_data.get('transactions', [])
                                        total_income = sum(t['amount'] for t in transactions_updated if t['transaction_type'] == 'Income')

                                        # Update targets based on new total income
                                        new_targets = {
                                            cat: total_income * sc.weights[cat] for cat in sc.categories
                                        }
                                        db.save_user_targets(st.session_state.username, new_targets)

                                    st.rerun()
                                else:
                                    st.error("Failed to delete transaction")
                else:
                    st.info("No transactions recorded yet.")


    with tab3:
        st.title("Financial Dashboard")

        # Fetch user transactions
        user_data = db.get_user_transactions(st.session_state.username)
        transactions = user_data.get('transactions', [])

        if st.session_state.reset_feedback:
            st.success(st.session_state.reset_feedback)
            st.session_state.reset_feedback = None

        def handle_reset(label, reset_fn):
            """Run a reset action, stash feedback, and refresh the dashboard."""
            if reset_fn(st.session_state.username):
                st.session_state.reset_feedback = f"{label} reset complete."
                st.rerun()
            else:
                st.error(f"Failed to reset {label.lower()}.")

        if not transactions:
            st.info("No transactions recorded yet. Go to the User Input tab to add your first transaction!")
        else:
            # Convert to DataFrame for easier processing
            df_transactions = pd.DataFrame(transactions)
            df_transactions['date'] = pd.to_datetime(df_transactions['date'])
            df_transactions['month'] = df_transactions['date'].dt.strftime('%b')

            # Calculate totals
            total_income = df_transactions[df_transactions['transaction_type'] == 'Income']['amount'].sum()
            total_expenses = df_transactions[df_transactions['transaction_type'] == 'Expense']['amount'].sum()
            savings = total_income - total_expenses

            # Row 1 - Big card with main chart
            with st.container(border=True):
                st.markdown("### Income vs Expenses")

                # Aggregate by month and type
                monthly_data = df_transactions.groupby(['month', 'transaction_type'])['amount'].sum().unstack(fill_value=0)

                if not monthly_data.empty:
                    # Dynamically set colors based on number of columns
                    num_columns = len(monthly_data.columns)
                    if num_columns == 1:
                        # Only one type of transaction
                        st.line_chart(monthly_data, color='#fc7eff')
                    else:
                        # Both income and expense
                        st.line_chart(monthly_data, color=['#fc7eff', '#7effc7'])
                else:
                    st.write("Not enough data to display chart")

            # Row 2 - Two smaller cards
            col1, col2 = st.columns(2)

            with col1:
                with st.container(border=True):
                    st.markdown("### Expense Categories")

                    # Aggregate expenses by category
                    expense_categories = df_transactions[df_transactions['transaction_type'] == 'Expense'].groupby('category')['amount'].sum()

                    if not expense_categories.empty:
                        st.bar_chart(expense_categories, color="#fc7eff")
                    else:
                        st.write("No expenses recorded yet")

            with col2:
                actuals = {}

                for transaction in transactions:
                    if transaction["transaction_type"] == "Expense":
                        category = transaction["category"]
                        actuals[category] = (actuals[category] if category in actuals else 0) + transaction["amount"]

                targets = db.get_user_targets(st.session_state.username)

                score = sc.calculate_spending_score({
                    category: {
                        "actual": actuals[category] if category in actuals else 0,
                        "target": targets[category] if category in targets else 0,
                    } for category in sc.categories
                })

                with st.container(border=True):
                    st.markdown("### This Month")
                    st.metric("Total Income", f"${total_income:,.2f}")
                    st.metric("Total Expenses", f"${total_expenses:,.2f}")
                    st.metric("Score", f"{score:,.2f}") # later track over time

# ========== SETTINGS PAGE ==========
elif st.session_state.page == 'settings':
    # Top controls for navigation
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        if st.button("← Back", key="back_dashboard"):
            st.session_state.page = 'dashboard'
            st.rerun()
    with col2:
        st.header("⚙️")

    # Tabs for Settings page
    tab_settings, tab_user, tab_history = st.tabs(["Settings page", "User info", "History"])

    with tab_settings:
        with st.container(border=True):
            st.subheader("Settings")
            st.selectbox("Theme", ["Light", "Dark"], key="theme_choice")
            st.slider("Font Size", 10, 30, 16, key="font_size")
            st.checkbox("Show Debug Info", key="debug_info")

    with tab_user:
        with st.container(border=True):
            st.subheader("User Info")
            st.write(f"Username: {st.session_state.get('username', '')}")
            st.write("Email: —")
            st.write("Member since: —")

    with tab_history:
        with st.container(border=True):
            st.title("History")
            st.subheader("Your current spending targets")

            # Load existing targets if you have them, or default to 0
            existing_targets = db.get_user_targets(st.session_state.username) or {}

            targets = {
                category: st.number_input(
                    category,
                    min_value=0.0,
                    step=1.0,
                    value=existing_targets.get(category, 0.0)  # prefill with saved targets or default to 0
                )
                for category in sc.categories
            }

            if st.button("Save targets"):
                if db.save_user_targets(st.session_state.username, targets):
                    st.success("Targets updated!")
                else:
                    st.error("Error saving targets")
