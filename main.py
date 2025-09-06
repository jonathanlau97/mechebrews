import streamlit as st
import time
from typing import Dict, List

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Coffee Shop Interface",
    page_icon="☕",
    layout="wide"
)

# Initialize session state
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'card_counter' not in st.session_state:
    st.session_state.card_counter = 0
if 'selected_drinks' not in st.session_state:
    st.session_state.selected_drinks = {}
if 'daily_served' not in st.session_state:
    st.session_state.daily_served = {}

# Poker card configuration
SUITS = ['♠️', '♥️', '♦️', '♣️']
NUMBERS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
COFFEE_TYPES = ['Latte', 'Americano', 'Cappuccino', 'Mocha', 'Long Black', 'Fresh Milk']

def generate_order_number():
    """Generate sequential poker card order number A->K"""
    try:
        current_counter = st.session_state.card_counter
        
        # Calculate position in sequence (A=0, 2=1, 3=2, ..., K=12)
        card_position = current_counter % 13
        suit_position = (current_counter // 13) % 4
        
        card_number = NUMBERS[card_position]
        card_suit = SUITS[suit_position]
        order_number = f"{card_suit}{card_number}"
        
        # Increment counter
        st.session_state.card_counter += 1
        
        return order_number
    except Exception as e:
        st.error(f"Card generation error: {e}")
        return f"#{st.session_state.card_counter + 1}"

def add_order(drinks_dict: dict):
    """Add a new order with multiple drinks"""
    try:
        if not drinks_dict:
            return False
            
        order_number = generate_order_number()
        order = {
            'order_number': order_number,
            'drinks': drinks_dict.copy(),  # Dictionary of {drink_key: quantity}
            'timestamp': time.time(),
            'status': 'pending'
        }
        st.session_state.orders.append(order)
        return True
    except Exception as e:
        st.error(f"Error adding order: {str(e)}")
        return False

def get_pending_orders():
    """Get all pending orders sorted by timestamp"""
    try:
        pending = [order for order in st.session_state.orders if order.get('status', 'pending') == 'pending']
        pending.sort(key=lambda x: x.get('timestamp', 0))
        return pending
    except Exception as e:
        st.error(f"Error getting orders: {str(e)}")
        return []

def get_drink_summary():
    """Get aggregated drink counts for barista"""
    try:
        pending_orders = get_pending_orders()
        drink_counts = {}
        
        for order in pending_orders:
            drinks = order.get('drinks', {})
            for drink_key, quantity in drinks.items():
                drink_counts[drink_key] = drink_counts.get(drink_key, 0) + quantity
        
        return drink_counts
    except Exception as e:
        st.error(f"Error getting drink summary: {str(e)}")
        return {}

def mark_order_completed(order_number: str):
    """Mark an order as completed and update daily served count"""
    try:
        import datetime
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        for order in st.session_state.orders:
            if order.get('order_number') == order_number:
                order['status'] = 'completed'
                
                # Count total cups in this order
                drinks = order.get('drinks', {})
                total_cups = sum(drinks.values())
                
                # Update daily served count
                if today not in st.session_state.daily_served:
                    st.session_state.daily_served[today] = 0
                st.session_state.daily_served[today] += total_cups
                
                return True
        return False
    except Exception as e:
        st.error(f"Error marking order complete: {str(e)}")
        return False

def get_today_served():
    """Get total cups served today"""
    try:
        import datetime
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        return st.session_state.daily_served.get(today, 0)
    except:
        return 0

def format_time(timestamp):
    """Format timestamp to readable time"""
    try:
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%H:%M:%S')
    except:
        return "Unknown time"

# Sidebar for page selection
st.sidebar.title("Coffee Shop Interface")

# Show today's served count in sidebar
today_served = get_today_served()
st.sidebar.markdown("---")
st.sidebar.metric("☕ Cups Served Today", today_served)
st.sidebar.markdown("---")

page = st.sidebar.selectbox(
    "Select Page",
    ["🛒 Order Input", "👨‍🍳 Barista", "🍽️ Waiter Service"]
)

# ORDER INPUT PAGE
if page == "🛒 Order Input":
    st.title("☕ Coffee Order")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Build Your Order")
        
        # Display current order being built
        if st.session_state.selected_drinks:
            st.markdown("### 📝 Current Order:")
            total_items = 0
            for drink_key, qty in st.session_state.selected_drinks.items():
                if qty > 0:
                    st.write(f"• {drink_key}: **{qty}**")
                    total_items += qty
            st.info(f"Total items: {total_items}")
            st.markdown("---")
        
        # Coffee selection with quantity controls - simplified view
        st.markdown("### Select Drinks")
        
        # Create a clean grid layout
        drink_cols = st.columns(2)
        
        for i, coffee in enumerate(COFFEE_TYPES):
            with drink_cols[i % 2]:
                with st.container():
                    st.markdown(f"**{coffee}**")
                    
                    # Hot option
                    hot_key = f"Hot {coffee}"
                    current_hot = st.session_state.selected_drinks.get(hot_key, 0)
                    
                    hot_cols = st.columns([3, 1, 1])
                    with hot_cols[0]:
                        st.write("🔥 Hot")
                    with hot_cols[1]:
                        if current_hot > 0:
                            if st.button("−", key=f"minus_hot_{coffee}", help="Remove one"):
                                st.session_state.selected_drinks[hot_key] = current_hot - 1
                                if st.session_state.selected_drinks[hot_key] == 0:
                                    del st.session_state.selected_drinks[hot_key]
                                st.rerun()
                        else:
                            st.write("")
                    with hot_cols[2]:
                        display_text = f"+{current_hot}" if current_hot > 0 else "+"
                        if st.button(display_text, key=f"plus_hot_{coffee}", help="Add one"):
                            st.session_state.selected_drinks[hot_key] = current_hot + 1
                            st.rerun()
                    
                    # Iced option
                    iced_key = f"Iced {coffee}"
                    current_iced = st.session_state.selected_drinks.get(iced_key, 0)
                    
                    iced_cols = st.columns([3, 1, 1])
                    with iced_cols[0]:
                        st.write("🧊 Iced")
                    with iced_cols[1]:
                        if current_iced > 0:
                            if st.button("−", key=f"minus_iced_{coffee}", help="Remove one"):
                                st.session_state.selected_drinks[iced_key] = current_iced - 1
                                if st.session_state.selected_drinks[iced_key] == 0:
                                    del st.session_state.selected_drinks[iced_key]
                                st.rerun()
                        else:
                            st.write("")
                    with iced_cols[2]:
                        display_text = f"+{current_iced}" if current_iced > 0 else "+"
                        if st.button(display_text, key=f"plus_iced_{coffee}", help="Add one"):
                            st.session_state.selected_drinks[iced_key] = current_iced + 1
                            st.rerun()
                    
                    st.markdown("---")
        
        # Order action buttons
        order_cols = st.columns(2)
        with order_cols[0]:
            if st.button("✅ PLACE ORDER", use_container_width=True, type="primary"):
                if st.session_state.selected_drinks:
                    if add_order(st.session_state.selected_drinks):
                        st.success("Order placed successfully!")
                        st.session_state.selected_drinks = {}
                        st.rerun()
                else:
                    st.warning("Please select at least one drink!")
        
        with order_cols[1]:
            if st.button("🗑️ CLEAR ALL", use_container_width=True):
                st.session_state.selected_drinks = {}
                st.rerun()
    
    with col2:
        st.subheader("Recent Orders")
        try:
            recent_orders = st.session_state.orders[-5:] if st.session_state.orders else []
            
            if recent_orders:
                for order in reversed(recent_orders):
                    status_icon = "✅" if order.get('status') == 'completed' else "🕐"
                    order_num = order.get('order_number', 'Unknown')
                    drinks = order.get('drinks', {})
                    total_cups = sum(drinks.values())
                    
                    with st.expander(f"{status_icon} {order_num} ({total_cups} cups)"):
                        for drink, qty in drinks.items():
                            st.write(f"• {drink}: {qty}")
            else:
                st.info("No orders yet")
        except Exception as e:
            st.error("Error displaying recent orders")

# BARISTA PAGE
elif page == "👨‍🍳 Barista":
    st.title("👨‍🍳 Barista Dashboard")
    st.markdown("---")
    
    try:
        drink_summary = get_drink_summary()
        
        if drink_summary:
            st.markdown("### 📋 Drinks to Make")
            
            for drink, count in drink_summary.items():
                st.markdown(f"""
                <div style="
                    background-color: #f0f2f6; 
                    padding: 20px; 
                    margin: 10px 0; 
                    border-radius: 10px; 
                    border-left: 5px solid #ff6b6b;
                ">
                    <h2 style="margin: 0; color: #2c3e50;">{drink}</h2>
                    <h1 style="margin: 5px 0; color: #e74c3c; font-size: 3em;">{count}</h1>
                </div>
                """, unsafe_allow_html=True)
            
            # Summary
            total_drinks = sum(drink_summary.values())
            st.markdown(f"""
            <div style="
                background-color: #e8f5e8; 
                padding: 15px; 
                margin: 20px 0; 
                border-radius: 10px; 
                text-align: center;
            ">
                <h2 style="margin: 0; color: #27ae60;">Total Drinks: {total_drinks}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Clear completed orders button
            if st.button("🗑️ Clear Completed Orders", use_container_width=True):
                try:
                    st.session_state.orders = [order for order in st.session_state.orders if order.get('status') != 'completed']
                    st.rerun()
                except Exception as e:
                    st.error("Error clearing orders")
        else:
            st.markdown("""
            <div style="
                text-align: center; 
                padding: 50px; 
                background-color: #f8f9fa; 
                border-radius: 10px; 
                margin: 20px 0;
            ">
                <h1 style="color: #6c757d;">☕ No drinks to make!</h1>
                <p style="font-size: 1.2em; color: #6c757d;">All caught up! 🎉</p>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error("Error loading barista dashboard")

# WAITER SERVICE PAGE
elif page == "🍽️ Waiter Service":
    st.title("🍽️ Waiter Service")
    st.markdown("---")
    
    try:
        pending_orders = get_pending_orders()
        
        if pending_orders:
            st.markdown("### 📝 Orders to Serve (First Ordered First)")
            
            for i, order in enumerate(pending_orders):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    order_num = order.get('order_number', f'Order #{i+1}')
                    drinks = order.get('drinks', {})
                    order_time = format_time(order.get('timestamp', time.time()))
                    total_cups = sum(drinks.values())
                    
                    # Create drinks list
                    drinks_list = []
                    for drink, qty in drinks.items():
                        if qty > 1:
                            drinks_list.append(f"{qty}x {drink}")
                        else:
                            drinks_list.append(drink)
                    drinks_text = "<br>".join([f"• {drink}" for drink in drinks_list])
                    
                    st.markdown(f"""
                    <div style="
                        background-color: #fff3cd; 
                        padding: 20px; 
                        margin: 10px 0; 
                        border-radius: 10px; 
                        border-left: 5px solid #ffc107;
                    ">
                        <h1 style="margin: 0; color: #856404; font-size: 2.5em;">{order_num}</h1>
                        <h3 style="margin: 10px 0; color: #495057;">({total_cups} cups total)</h3>
                        <div style="margin: 10px 0; color: #495057; font-size: 1.1em;">
                            {drinks_text}
                        </div>
                        <p style="margin: 0; color: #6c757d; font-size: 0.9em;">
                            Ordered: {order_time}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"✅ Served", key=f"serve_{order_num}_{i}", use_container_width=True):
                        if mark_order_completed(order_num):
                            st.success(f"Order {order_num} served!")
                            st.balloons()
                            st.rerun()
            
            # Summary
            total_pending_cups = sum(sum(order.get('drinks', {}).values()) for order in pending_orders)
            st.markdown(f"""
            <div style="
                background-color: #d1ecf1; 
                padding: 15px; 
                margin: 20px 0; 
                border-radius: 10px; 
                text-align: center;
            ">
                <h2 style="margin: 0; color: #0c5460;">
                    {len(pending_orders)} Orders Pending | {total_pending_cups} Total Cups
                </h2>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div style="
                text-align: center; 
                padding: 50px; 
                background-color: #d4edda; 
                border-radius: 10px; 
                margin: 20px 0;
            ">
                <h1 style="color: #155724;">🎉 All orders served!</h1>
                <p style="font-size: 1.2em; color: #155724;">Great job! No pending orders.</p>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error("Error loading waiter service page")

# ANALYTICS PAGE
elif page == "📊 Analytics":
    st.title("📊 Coffee Shop Analytics")
    st.markdown("---")
    
    try:
        # Load historical data
        orders_history, daily_summary = load_historical_data()
        
        if not orders_history and not daily_summary:
            st.info("📈 No historical data yet. Complete some orders and save your session to see analytics!")
        else:
            # Daily Summary Section
            if daily_summary:
                st.subheader("📅 Daily Summary")
                
                summary_df = pd.DataFrame(daily_summary)
                summary_df['date'] = pd.to_datetime(summary_df['date'])
                summary_df = summary_df.sort_values('date', ascending=False)
                
                # Display recent days
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Days Recorded", len(summary_df))
                    if len(summary_df) > 0:
                        latest_day = summary_df.iloc[0]
                        st.metric("Latest Day Orders", latest_day['total_orders'])
                
                with col2:
                    total_all_time_cups = summary_df['total_cups'].sum()
                    st.metric("All-Time Cups Sold", total_all_time_cups)
                    if len(summary_df) > 0:
                        st.metric("Latest Day Cups", latest_day['total_cups'])
                
                # Recent days table
                st.subheader("Recent Days")
                display_df = summary_df.copy()
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                st.dataframe(
                    display_df.rename(columns={
                        'date': 'Date',
                        'total_orders': 'Orders',
                        'total_cups': 'Cups Sold'
                    }),
                    use_container_width=True
                )
            
            # Drink Popularity Section
            if orders_history:
                st.subheader("☕ Drink Popularity")
                
                drink_stats = get_drink_analytics(orders_history)
                
                if drink_stats:
                    # Create a simple bar chart display
                    st.markdown("**Most Popular Drinks (All Time):**")
                    
                    for i, (drink, count) in enumerate(list(drink_stats.items())[:10], 1):
                        percentage = (count / sum(drink_stats.values())) * 100
                        st.markdown(f"""
                        <div style="
                            background-color: #f0f2f6;
                            padding: 10px;
                            margin: 5px 0;
                            border-radius: 5px;
                            border-left: 5px solid #ff6b6b;
                        ">
                            <strong>{i}. {drink}</strong><br>
                            <span style="color: #666;">
                                {count} cups sold ({percentage:.1f}%)
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Raw data section (expandable)
                with st.expander("📋 View Raw Order Data"):
                    if orders_history:
                        orders_df = pd.DataFrame(orders_history)
                        orders_df = orders_df.sort_values(['date', 'order_time'], ascending=False)
                        st.dataframe(orders_df, use_container_width=True)
        
        # Data management
        st.markdown("---")
        st.subheader("🔧 Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download Historical Data"):
                try:
                    if orders_history:
                        df = pd.DataFrame(orders_history)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📄 Download Orders CSV",
                            data=csv,
                            file_name=f"coffee_orders_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("No data to download")
                except Exception as e:
                    st.error(f"Download error: {e}")
        
        with col2:
            if st.button("🗑️ Clear All History", type="secondary"):
                if st.button("⚠️ Confirm Delete All History"):
                    try:
                        if os.path.exists('coffee_orders_history.csv'):
                            os.remove('coffee_orders_history.csv')
                        if os.path.exists('daily_summary.csv'):
                            os.remove('daily_summary.csv')
                        st.success("All historical data cleared!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing data: {e}")
        
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ and ☕")
