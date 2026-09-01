import streamlit as st
from supabase import create_client


supa_url = st.secrets["supa_url"]
supa_key = st.secrets["supa_key"]

supabase = create_client(supa_url, supa_key)

#Volunteer Only

secret_key=st.secrets["secret_key"]
volunteer_supabase=create_client(supa_url, secret_key)


# Navigation Sidebar

st.sidebar.title("Snack Track Navi")

page = st.sidebar.radio(
    "Go to:",
    ["Store", "Volunteer Dashboard"]
)

# Temporary Shopping Cart

if "cart" not in st.session_state:
    st.session_state.cart = {}

# Storefront

if page == "Store":

    st.title("AECHS Snack Track")
    st.write("Check out what's in store today! :~)")


    try:
        # Shows live inventory rows
        show = supabase.table("inventory").select("*").execute()
        items = show.data


        # Displays snacks neatly
        for item in items:

            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### **{item['name']}**")
                st.write(f"Price: ${item['price']:.2f}")
                st.caption(
                    f"In Stock: {item['stock_quantity']} units"
                )


            with col2:

                if item["stock_quantity"] > 0:

                    if st.button(
                        "Add to Cart",
                        key=f"btn_{item['name']}"
                    ):
                        st.session_state.cart[item["name"]] = (
                            st.session_state.cart.get(
                                item["name"], 0
                            ) + 1
                        )

                        st.success(
                            f"Added {item['name']}!"
                        )

                        st.rerun()

                else:
                    st.error("Out of stock")


            st.divider()

        # View Cart & Checkout

        st.subheader("Your Shopping Cart")

        if not st.session_state.cart:

            st.write("Your cart is empty.")

        else:

            for snack, qty in st.session_state.cart.items():
                st.write(f"- {snack} x {qty}")


            customer_name = st.text_input("Enter your name to place order:")

            if st.button("Submit order? :~3"):
                if customer_name:

                    items_for_order = [
                        {
                            "name": snack,
                            "quantity": qty
                        }
                        for snack, qty in st.session_state.cart.items()
                    ]

                    result = supabase.rpc(
                        "place_order",
                        {
                            "customer_name_input": customer_name,
                            "items_input": items_for_order
                        }
                    ).execute()

                    if result.data is True:

                        st.success(
                            f"Thank you for supporting us {customer_name}! "
                            "Your order has been sent. <3"
                        )

                        st.session_state.cart = {}
                        st.rerun()

                    else:
                        st.error(
                            "Sorry! One or more items in your cart "
                            "are no longer in stock. :~("
                        )

                else:
                    st.warning("Please enter your name first! :~3")


    except Exception as e:

        st.error(
            f"Could not connect to your database: {e}"
        )

# Volunteer Dashboard
elif page == "Volunteer Dashboard":

    st.title("Volunteer Dashboard")

    if "volunteer_logged_in" not in st.session_state:
        st.session_state.volunteer_logged_in = False

    # Volunteer Login
    if not st.session_state.volunteer_logged_in:

        st.subheader("Volunteer Login")

        pin = st.text_input(
            "Enter volunteer PIN:",
            type="password"
        )

        if st.button("Log In"):
            if pin == st.secrets["volunteer_pin"]:

                st.session_state.volunteer_logged_in = True
                st.rerun()

            else:
                st.error("Incorrect PIN.")

    # Volunteer Dashboard
    else:

        st.success("Volunteer access granted! :3")

        if st.button("Log Out"):
            st.session_state.volunteer_logged_in = False
            st.rerun()

        st.divider()

        try:
            # Get orders
            order_feed = (
                volunteer_supabase
                .table("Orders")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            orders = order_feed.data

            if not orders:

                st.info(
                    "No orders have been placed yet. :~<"
                )

            else:

                # Separate orders by status
                pending_orders = [
                    order for order in orders
                    if order["status"] == "pending"
                ]

                ready_orders = [
                    order for order in orders
                    if order["status"] == "ready"
                ]


                # Order Pending

                st.header("🟡 Pending Orders")

                if not pending_orders:

                    st.info("No pending orders!")

                else:

                    for order in pending_orders:

                        with st.container(border=True):

                            st.subheader(
                                f"Order #{order['id']}"
                            )

                            st.write(
                                f"**Customer:** "
                                f"{order['customer_name']}"
                            )

                            st.write(
                                f"**Items:** "
                                f"{order['items_ordered']}"
                            )

                            st.caption(
                                f"Placed: "
                                f"{order['created_at']}"
                            )

                            if st.button(
                                "✅ Mark Ready",
                                key=f"ready_{order['id']}"
                            ):

                                volunteer_supabase.table(
                                    "Orders"
                                ).update(
                                    {"status": "ready"}
                                ).eq(
                                    "id", order["id"]
                                ).execute()

                                st.rerun()

                # READY ORDERS

                st.header("🟢 Ready for Pickup")

                if not ready_orders:

                    st.info("No orders waiting for pickup!")

                else:

                    for order in ready_orders:

                        with st.container(border=True):

                            st.subheader(
                                f"Order #{order['id']}"
                            )

                            st.write(
                                f"**Customer:** "
                                f"{order['customer_name']}"
                            )

                            st.write(
                                f"**Items:** "
                                f"{order['items_ordered']}"
                            )

                            st.caption(
                                f"Placed: "
                                f"{order['created_at']}"
                            )

                            if st.button(
                                "📦 Mark Picked Up",
                                key=f"picked_{order['id']}"
                            ):

                                volunteer_supabase.table(
                                    "Orders"
                                ).update(
                                    {"status": "picked_up"}
                                ).eq(
                                    "id", order["id"]
                                ).execute()

                                st.rerun()

        except Exception as e:

            st.error(
                f"Could not load orders: {e}"
            )


