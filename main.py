import streamlit as st
import random
from datetime import datetime
from typing import Dict, List, Tuple

# Initialize session state
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'used_cards' not in st.session_state:
    st.session_state.used_cards = set()

# Poker card configuration
SUITS = ['♠️', '♥️', '♦️', '♣️']
NUMBERS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
COFFEE_TYPES = ['Latte', 'Americano', 'Cappuccino', 'Mocha', 'Long Black', 'Fresh Milk']

def generate_order_number():
    """Generate a unique poker card order number"""
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

def add_order(coffee_type: str, temperature: str):
    """Add a new order to the session state"""
    order_number = generate_order_number()
    order = {
        'order_number': order_number,
        'coffee_type': coffee_type,
        'temperature': temperature,
        'timestamp': datetime.now(),
        'status': 'pending'
    }
    st.session_state.orders.append(order)

def get_pending_orders():
    """Get all pending orders sorted by timestamp"""
    return [order for order in st.session_state.orders if order['status'] == 'pending']

def get_drink_summary():
    """Get aggregated drink counts for barista"""
    pending_orders = get_pending_orders()
    drink_counts = {}
    
    for order in pending_orders:
        drink_key = f"{order['temperature']} {order['coffee_type']}"
        drink_counts[drink_key] = drink_counts.get(drink_key, 0) + 1
    
    return drink_counts

def mark_order_completed(order_number: str):
    """Mark an order as completed"""
    for order in st.session_state.orders:
        if order['order_number'] == order_number:
            order['status'] = 'completed'
            break

# Page configuration
st.set_page_config(
    page_title="Coffee Shop Interface",
    page_icon="☕",
    layout="wide"
)

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
                    add_order(st.session_state.selected_coffee, "Hot")
                    st.success(f"Order added: Hot {st.session_state.selected_coffee}")
                    st.session_state.selected_coffee = None  # Reset selection
                    st.rerun()
            
            with temp_col2:
                if st.button("🧊 ICED", key="iced_btn", use_container_width=True):
                    add_order(st.session_state.selected_coffee, "Iced")
                    st.success(f"Order added: Iced {st.session_state.selected_coffee}")
                    st.session_state.selected_coffee = None  # Reset selection
                    st.rerun()
            
            with temp_col3:
                if st.button("❌ Cancel", key="cancel_btn", use_container_width=True):
                    st.session_state.selected_coffee = None
                    st.rerun()
    
    with col2:
        st.subheader("Recent Orders")
        recent_orders = st.session_state.orders[-5:] if st.session_state.orders else []
        
        if recent_orders:
            for order in reversed(recent_orders):
                status_icon = "✅" if order['status'] == 'completed' else "🕐"
                st.info(f"{status_icon} {order['order_number']}: {order['temperature']} {order['coffee_type']}")
        else:
            st.info("No orders yet")

# BARISTA PAGE
elif page == "👨‍🍳 Barista":
    st.title("👨‍🍳 Barista Dashboard")
    st.markdown("---")
    
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
            st.session_state.orders = [order for order in st.session_state.orders if order['status'] != 'completed']
            st.rerun()
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

# WAITER SERVICE PAGE
elif page == "🍽️ Waiter Service":
    st.title("🍽️ Waiter Service")
    st.markdown("---")
    
    pending_orders = get_pending_orders()
    pending_orders.sort(key=lambda x: x['timestamp'])  # Sort by timestamp (first ordered first)
    
    if pending_orders:
        st.markdown("### 📝 Orders to Serve (First Ordered First)")
        
        for i, order in enumerate(pending_orders):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Large, easy-to-read order display
                st.markdown(f"""
                <div style="
                    background-color: #fff3cd; 
                    padding: 20px; 
                    margin: 10px 0; 
                    border-radius: 10px; 
                    border-left: 5px solid #ffc107;
                ">
                    <h1 style="margin: 0; color: #856404; font-size: 2.5em;">{order['order_number']}</h1>
                    <h2 style="margin: 10px 0; color: #495057;">{order['temperature']} {order['coffee_type']}</h2>
                    <p style="margin: 0; color: #6c757d; font-size: 0.9em;">
                        Ordered: {order['timestamp'].strftime('%H:%M:%S')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"✅ Served", key=f"serve_{order['order_number']}", use_container_width=True):
                    mark_order_completed(order['order_number'])
                    st.success(f"Order {order['order_number']} marked as served!")
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

# Footer
st.markdown("---")
st.markdown("Made with ❤️ and ☕")
