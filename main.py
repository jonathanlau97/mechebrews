import streamlit as st
import random
import time
from typing import Dict, List, Tuple

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Coffee Shop Interface",
    page_icon="☕",
    layout="wide"
)

# Initialize session state
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'used_cards' not in st.session_state:
    st.session_state.used_cards = set()
if 'selected_coffee' not in st.session_state:
    st.session_state.selected_coffee = None

# Poker card configuration
SUITS = ['♠️', '♥️', '♦️', '♣️']
NUMBERS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
COFFEE_TYPES = ['Latte', 'Americano', 'Cappuccino', 'Mocha', 'Long Black', 'Fresh Milk']

def generate_order_number():
    """Generate a unique poker card order number"""
    try:
        available_cards = []
        for suit in SUITS:
            for number in NUMBERS:
                card = f"{suit}{number}"
                if card not in st.session_state.used_cards:
                    available_cards.append(card)
        
        if not available_cards:
            # Reset if all cards are used
            st.session_state.used_cards = set()
            available_cards = [f"{suit}{number}" for suit in SUITS for number in NUMBERS]
        
        selected_card = random.choice(available_cards)
        st.session_state.used_cards.add(selected_card)
        return selected_card
    except Exception as e:
        # Fallback to simple numbering if card system fails
        return f"#{len(st.session_state.orders) + 1}"

def add_order(coffee_type: str, temperature: str):
    """Add a new order to the session state"""
    try:
        order_number = generate_order_number()
        order = {
            'order_number': order_number,
            'coffee_type': coffee_type,
            'temperature': temperature,
            'timestamp': time.time(),  # Using time.time() instead of datetime
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
        # Sort by timestamp
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
            drink_key = f"{order.get('temperature', 'Hot')} {order.get('coffee_type', 'Unknown')}"
            drink_counts[drink_key] = drink_counts.get(drink_key, 0) + 1
        
        return drink_counts
    except Exception as e:
        st.error(f"Error getting drink summary: {str(e)}")
        return {}

def mark_order_completed(order_number: str):
    """Mark an order as completed"""
    try:
        for order in st.session_state.orders:
            if order.get('order_number') == order_number:
                order['status'] = 'completed'
                return True
        return False
    except Exception as e:
        st.error(f"Error marking order complete: {str(e)}")
        return False

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
        st.subheader("Select Your Coffee")
        
        # Coffee type selection
        coffee_cols = st.columns(3)
        
        for i, coffee in enumerate(COFFEE_TYPES):
            with coffee_cols[i % 3]:
                if st.button(coffee, key=f"coffee_{coffee}", use_container_width=True):
                    st.session_state.selected_coffee = coffee
                    st.rerun()
        
        # Show selected coffee and temperature options
        if st.session_state.selected_coffee:
            st.success(f"Selected: {st.session_state.selected_coffee}")
            
            st.subheader("Temperature")
            temp_col1, temp_col2, temp_col3 = st.columns([1, 1, 1])
            
            with temp_col1:
                if st.button("🔥 HOT", key="hot_btn", use_container_width=True):
                    if add_order(st.session_state.selected_coffee, "Hot"):
                        st.success(f"Order added: Hot {st.session_state.selected_coffee}")
                        st.session_state.selected_coffee = None
                        time.sleep(1)  # Brief pause to show success message
                        st.rerun()
            
            with temp_col2:
                if st.button("🧊 ICED", key="iced_btn", use_container_width=True):
                    if add_order(st.session_state.selected_coffee, "Iced"):
                        st.success(f"Order added: Iced {st.session_state.selected_coffee}")
                        st.session_state.selected_coffee = None
                        time.sleep(1)  # Brief pause to show success message
                        st.rerun()
            
            with temp_col3:
                if st.button("❌ Cancel", key="cancel_btn", use_container_width=True):
                    st.session_state.selected_coffee = None
                    st.rerun()
    
    with col2:
        st.subheader("Recent Orders")
        try:
            recent_orders = st.session_state.orders[-5:] if st.session_state.orders else []
            
            if recent_orders:
                for order in reversed(recent_orders):
                    status_icon = "✅" if order.get('status') == 'completed' else "🕐"
                    order_num = order.get('order_number', 'Unknown')
                    coffee = order.get('coffee_type', 'Unknown')
                    temp = order.get('temperature', 'Hot')
                    st.info(f"{status_icon} {order_num}: {temp} {coffee}")
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
                # Large, easy-to-read format
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
                    # Large, easy-to-read order display
                    order_num = order.get('order_number', f'Order #{i+1}')
                    coffee = order.get('coffee_type', 'Unknown')
                    temp = order.get('temperature', 'Hot')
                    order_time = format_time(order.get('timestamp', time.time()))
                    
                    st.markdown(f"""
                    <div style="
                        background-color: #fff3cd; 
                        padding: 20px; 
                        margin: 10px 0; 
                        border-radius: 10px; 
                        border-left: 5px solid #ffc107;
                    ">
                        <h1 style="margin: 0; color: #856404; font-size: 2.5em;">{order_num}</h1>
                        <h2 style="margin: 10px 0; color: #495057;">{temp} {coffee}</h2>
                        <p style="margin: 0; color: #6c757d; font-size: 0.9em;">
                            Ordered: {order_time}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"✅ Served", key=f"serve_{order_num}_{i}", use_container_width=True):
                        if mark_order_completed(order_num):
                            st.success(f"Order {order_num} marked as served!")
                            st.rerun()
            
            # Summary
            st.markdown(f"""
            <div style="
                background-color: #d1ecf1; 
                padding: 15px; 
                margin: 20px 0; 
                border-radius: 10px; 
                text-align: center;
            ">
                <h2 style="margin: 0; color: #0c5460;">Total Orders Pending: {len(pending_orders)}</h2>
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

# Footer
st.markdown("---")
st.markdown("Made with ❤️ and ☕")
