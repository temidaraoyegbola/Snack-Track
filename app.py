import streamlit as st
from supabase import create_client
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh

current_time = datetime.now(ZoneInfo("America/Chicago")).time()
afterschool_time = datetime.strptime("14:30", "%H:%M").time()

is_afterschool = current_time >= afterschool_time

supa_url = st.secrets["supa_url"]
supa_key = st.secrets["supa_key"]

supabase = create_client(supa_url, supa_key)


#Volunteer Only

secret_key=st.secrets["secret_key"]
volunteer_supabase=create_client(supa_url, secret_key)


# Navigation Sidebar

st.sidebar.title("Snack Track")

page = st.sidebar.radio(
    "Go to:",
    ["Store", "Volunteer Dashboard"]
)

# Temporary Shopping Cart

if "cart" not in st.session_state:
    st.session_state.cart = {}
if "in_person_cart" not in st.session_state:
    st.session_state.in_person_cart = {}

if "order_confirmation" not in st.session_state:
    st.session_state.order_confirmation = None

# Storefront

if page == "Store":

    st_autorefresh(
        interval=60_000,
        key="store_refresh"
    )

    # Show order confirmation
    if st.session_state.order_confirmation:

        st.success(
            st.session_state.order_confirmation
        )

        st.session_state.order_confirmation = None

    st.title("໒꒰ྀི∩˃ ᵕ ˂∩꒱ྀི১ 09.21.26! Grand Opening!")
    st.title("AECHS Snack Track")
    st.write("Check out what's in store today! :~)")
    search = st.text_input(
        "🔎 Search snacks",
        placeholder="Search for a snack or drink..."
    )

        # Shows live inventory rows
    show = (
            supabase
            .table("inventory")
            .select("*")
            .execute()
        )

    items = show.data


        # Category tabs
    all_tab, chips_tab, drinks_tab, ramen_tab, other_tab = st.tabs(
            [
                "✮⋆˙🛍˙⋆✮ All",
                "🍪🥨🍿 Chips & Snacks",
                "𐃯 Drinks",
                "˚⋅ 𓐐𓎩 ‧₊˚ Ramen & Noodles",
                "𔓐 Bars & Other"
            ]
        )


    def display_items(category=None, key_prefix=""):

            filtered_items = items

            if category is not None:

                filtered_items = [
                    item
                    for item in items
                    if item["category"] == category
                ]

            if search:

                filtered_items = [
                    item
                    for item in filtered_items
                    if search.lower() in item["name"].lower()
                ]


            for item in filtered_items:

                col1, col2 = st.columns([3, 1])


                with col1:

                    st.markdown(
                        f"### **{item['name']}**"
                    )

                    if item["price"] is None:

                        st.write("Price: Not set")

                    else:

                        st.write(
                            f"Price: ${item['price']:.2f}"
                        )

                    st.caption(
                        f"In Stock: {item['stock_quantity']} units"
                    )


                with col2:

                    # Afterschool item before 2:30 PM
                    if (
                        not item["school_day_only"]
                        and not is_afterschool
                    ):

                        st.button(
                            "Available at 2:30 PM",
                            key=f"{key_prefix}btn_{item['name']}",
                            disabled=True
                        )


                    # Price hasn't been entered
                    elif item["price"] is None:

                        st.button(
                            "Price Not Set",
                            key=f"{key_prefix}btn_{item['name']}",
                            disabled=True
                        )


                    # Item is out of stock
                    elif item["stock_quantity"] <= 0:

                        st.button(
                            "Out of Stock",
                            key=f"{key_prefix}btn_{item['name']}",
                            disabled=True
                        )


                    # Item is available
                    else:

                        if st.button(
                            "＋ Add to Cart",
                            key=f"{key_prefix}btn_{item['name']}"
                        ):

                            st.session_state.cart[item["name"]] = (
                                st.session_state.cart.get(
                                    item["name"],
                                    0
                                ) + 1
                            )

                            st.rerun()


                st.divider()


        # All items
    with all_tab:

            display_items(
                key_prefix="all_"
            )


        # Chips & Snacks
    with chips_tab:

            display_items(
                "Chips & Snacks",
                key_prefix="chips_"
            )


        # Drinks
    with drinks_tab:

            display_items(
                "Drinks",
                key_prefix="drinks_"
            )


        # Ramen & Noodles
    with ramen_tab:

            display_items(
                "Ramen & Noodles",
                key_prefix="ramen_"
            )


        # Bars & Other
    with other_tab:

            display_items(
                "Bars & Other",
                key_prefix="other_"
            )
            # View Cart & Checkout

    st.subheader("🛒 Your Shopping Cart")

    if not st.session_state.cart:

            st.info("Your cart is empty. :~(")

    else:

            total = 0
            cart_has_problem = False

            for snack, qty in list(st.session_state.cart.items()):

                # Find the snack in the live inventory
                item_data = next(
                    (
                        item
                        for item in items
                        if item["name"] == snack
                    ),
                    None
                )

                # Snack no longer exists
                if item_data is None:

                    cart_has_problem = True

                    st.warning(
                        f"{snack} is no longer available."
                    )

                    continue

                price = item_data["price"]
                stock = item_data["stock_quantity"]

                # Price hasn't been entered
                if price is None:

                    cart_has_problem = True

                    st.warning(
                        f"{snack}: price is not set."
                    )

                    continue

                # Make sure quantity isn't higher than stock
                if qty > stock:

                    st.session_state.cart[snack] = stock
                    qty = stock

                item_total = price * qty
                total += item_total

                col1, col2, col3, col4 = st.columns(
                    [3, 1, 1, 1]
                )

                with col1:

                    st.write(f"**{snack}**")

                    st.caption(
                        f"${price:.2f} each"
                    )

                with col2:

                    if st.button(
                        "−",
                        key=f"cart_minus_{snack}"
                    ):

                        if qty > 1:

                            st.session_state.cart[snack] = qty - 1

                        else:

                            del st.session_state.cart[snack]

                        st.rerun()

                with col3:

                    st.write(f"× {qty}")

                with col4:

                    # Don't allow more than available stock
                    if qty < stock:

                        if st.button(
                            "＋",
                            key=f"cart_plus_{snack}"
                        ):

                            st.session_state.cart[snack] = qty + 1
                            st.rerun()

                    else:

                        st.button(
                            "＋",
                            key=f"cart_plus_{snack}",
                            disabled=True
                        )

                st.write(
                    f"Item total: **${item_total:.2f}**"
                )

                st.divider()

            # Cart total

            st.markdown(
                f"### ˗ˋˏ$ˎˊ˗ Total: ${total:.2f}"
            )

            # Clear cart

            if st.button(
                " 🗑 .ᐣ.ᐟ Clear Cart",
                key="clear_student_cart"
            ):

                st.session_state.cart = {}
                st.rerun()

            st.divider()

                # Checkout

            st.subheader("$ˎˊ˗ Checkout")

            customer_name = st.text_input(
                "Enter your name:",
                placeholder="Your name",
                key="checkout_customer_name"
            )

            if st.button(
                "✮⋆˙🛍˙⋆✮ Place Order",
                key="place_order_button"
                ):

                if not customer_name.strip():
                    st.warning(
                        "Please enter your name first! :~3"
                    )

                elif not st.session_state.cart:
                    st.warning(
                        "Your cart is empty! :~("
                    )

                else:
                    items_for_order = [
                        {
                            "name": snack,
                            "quantity": qty
                        }
                        for snack, qty
                        in st.session_state.cart.items()
                    ]

                    result = supabase.rpc(
                        "place_order",
                        {
                            "customer_name_input": customer_name.strip(),
                            "items_input": items_for_order
                        }
                    ).execute()

                    if result.data is True:
                        st.session_state.order_confirmation = (
                            f"Thank you, {customer_name.strip()}! "
                            "Your order has been placed! 🎉"
                        )

                        st.session_state.cart = {}

                        st.rerun()

                    else:
                        st.error(
                            "Sorry! Something changed with your order. "
                            "An item may have sold out or isn't available yet. :~("
                        )


# Volunteer Dashboard
elif page == "Volunteer Dashboard":
    st.title("Volunteer Dashboard")

    # Refresh the volunteer dashboard every 5 seconds
    st_autorefresh(
            interval=5000,
            key="volunteer_refresh"
         )

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

    else:

        st.success("Volunteer access granted! :3")

        st.divider()


        if st.button("Log Out"):

            st.session_state.volunteer_logged_in = False
            st.rerun()

        st.divider()

        orders_tab, in_person_tab, inventory_tab= st.tabs(
            ["🗎 Orders", "🛒 In-Person Order","⛟ Inventory"]
        )

        with orders_tab:
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

                total_earned = sum(
                    order["total_amount"] or 0
                    for order in orders
                )

                st.metric(
                    "💰 Total Earned",
                    f"${total_earned:.2f}"
                )

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


                # PENDING ORDERS

                st.header("ⴵ Pending Orders")

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

                            st.write("**Items:**")
                            order_items = order["items_ordered"].split(", ")

                            for item_entry in order_items:
                                col1, col2 = st.columns([5, 1])
                                with col1:
                                    st.write(item_entry)
                                with col2:
                                    if st.button(
                                        "✕",
                                        key=f"remove_{order['id']}_{item_entry}"
                                    ):
                                        result = volunteer_supabase.rpc(
                                            "remove_order_item",
                                        {
                                            "order_id_input": order["id"],
                                            "item_name_input": item_entry.rsplit(" x", 1)[0]
                                        }
                                    ).execute()
                                        if result.data is True:
                                            st.success("Item removed!")
                                            st.rerun()
                                        else:
                                            st.error("Could not remove that item.")

                            st.caption(
                                f"Placed: "
                                f"{order['created_at']}"
                            )

                            col1, col2 = st.columns(2)
                            with col1:
                                 if st.button(
                                      "✓ Mark Ready",
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

                            with col2:
                                 if st.button(
                                      "✕ Cancel",
                                      key=f"cancel_{order['id']}"
                                 ):
                                      volunteer_supabase.table(
                                           "Orders"
                                      ).update(
                                           {"status": "cancelled"}
                                      ).eq(
                                           "id", order["id"]
                                      ).execute()

                                      st.rerun()



                # READY ORDERS

                st.header(
                    "⋆ ˖ ⏱︎.ᐟ  Ready for Pickup"
                )

                if not ready_orders:

                    st.info(
                        "No orders waiting for pickup!"
                    )

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
                                "٩(^ᗜ^ )و ´- Mark Picked Up",
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

        with in_person_tab:
            # In-person ordering
            st.header("🛒 New In-Person Order")

            search = st.text_input(
                "🔎 Search for a snack:",
                placeholder="Type a snack name..."
            )

            try:
                inventory_feed = (
                    volunteer_supabase
                    .table("inventory")
                    .select("*")
                    .order("name")
                    .execute()
                )

                inventory_items = inventory_feed.data

                # Show matching inventory items
                for item in inventory_items:

                    if search.strip():
                        if search.lower() not in item["name"].lower():
                            continue

                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**{item['name']}**")

                        if item["price"] is None:
                            st.caption("Price not set")

                        else:
                            st.caption(
                                f"${item['price']:.2f} • "
                                f"{item['stock_quantity']} in stock"
                            )

                    with col2:

                        # Price hasn't been entered yet
                        if item["price"] is None:

                            st.button(
                                "Price needed",
                                disabled=True,
                                key=f"cash_price_{item['name']}"
                            )

                        # Afterschool item before 2:30 PM
                        elif (
                            not item["school_day_only"]
                            and not is_afterschool
                        ):

                            st.button(
                                "Available at 2:30 PM",
                                disabled=True,
                                key=f"cash_time_{item['name']}"
                            )

                        # Out of stock
                        elif item["stock_quantity"] <= 0:

                            st.button(
                                "Out of stock",
                                disabled=True,
                                key=f"cash_stock_{item['name']}"
                            )

                        # Available
                        else:

                            if st.button(
                                "＋ Add",
                                key=f"cash_add_{item['name']}"
                            ):

                                st.session_state.in_person_cart[
                                    item["name"]
                                ] = (
                                    st.session_state.in_person_cart.get(
                                        item["name"],
                                        0
                                    ) + 1
                                )

                                st.rerun()

                    st.divider()

            except Exception as e:

                st.error(
                    f"Could not load inventory: {e}"
                )

            # Current In-Person Order

            st.subheader("Current In-Person Order")

            total = 0

            if not st.session_state.in_person_cart:

                st.info("No items added yet.")

            else:
               for snack, qty in list(
                   st.session_state.in_person_cart.items()
              ):
                   item_data = next(
                       (
                           item
                           for item in inventory_items
                           if item["name"] == snack
                       ),
                       None
                   )

                   if item_data and item_data["price"] is not None:
                       item_total = item_data["price"] * qty
                       total += item_total

                       col1, col2 = st.columns([6, 1])

                       with col1:
                           st.write(
                               f"**{snack}** × {qty} — "
                               f"${item_total:.2f}"
                           )

                       with col2:
                           if st.button(
                               "✕",
                                key=f"remove_in_person_{snack}"
                           ):
                               del st.session_state.in_person_cart[snack]
                               st.rerun()

                # Total goes AFTER the cart loop
                
            st.markdown(f"### Total: ${total:.2f}")

            if st.button(
                    "🗑️ Clear Order",
                    key="clear_in_person_order"
                ):
                    st.session_state.in_person_cart = {}
                    st.rerun()

            customer_name = st.text_input(
                    "Customer name (optional):",
                    key="in_person_customer_name"
                )

            if st.button(
                    "Submit In-Person Order",
                    type="primary"
                ):

                    items_for_order = [
                        {
                            "name": snack,
                            "quantity": qty
                        }
                        for snack, qty
                        in st.session_state.in_person_cart.items()
                    ]

                    order_name = (
                        customer_name.strip()
                        if customer_name.strip()
                        else "In-Person"
                    )

                    result = volunteer_supabase.rpc(
                        "place_order",
                        {
                            "customer_name_input": order_name,
                            "items_input": items_for_order
                        }
                    ).execute()

                    if result.data is True:

                        st.success(
                            "In-person order recorded! ✓"
                        )

                        st.session_state.in_person_cart = {}
                        st.session_state.in_person_customer = ""

                        st.rerun()

                    else:

                        st.error(
                            "The order could not be placed. "
                            "Check the stock, prices, and availability."
                        )
        with inventory_tab:
            with inventory_tab:

                st.header("📦 Inventory Management")

                try:
                    inventory_feed = (
                        volunteer_supabase
                        .table("inventory")
                        .select("*")
                        .order("name")
                        .execute()
                    )

                    inventory_items = inventory_feed.data

                    if not inventory_items:
                        st.info("No inventory items found.")

                    else:
                        for item in inventory_items:
                            with st.container(border=True):
                                st.subheader(item["name"])

                                col1, col2 = st.columns(2)

                                with col1:
                                    # Price
                                    current_price = item["price"]

                                    new_price = st.number_input(
                                        "Price ($)",
                                        min_value=0.0,
                                        step=0.25,
                                        value=(
                                            float(current_price)
                                            if current_price is not None
                                            else 0.0
                                    ),
                            key=f"price_{item['name']}"
                            )

                        # Stock
                            new_stock = st.number_input(
                                "Stock quantity",
                                min_value=0,
                                step=1,
                                value=int(item["stock_quantity"]),
                                key=f"stock_{item['name']}"
                            )

                            with col2:
                                # Availability
                                availability = st.selectbox(
                                    "Availability",
                                    [
                                        "All day",
                                        "After 2:30 PM"
                                    ],
                                    index=(
                                        0
                                        if item["school_day_only"]
                                        else 1
                                    ),
                                    key=f"availability_{item['name']}"
                                )

                                if availability == "All day":
                                    new_school_day_only = True
                                else:
                                    new_school_day_only = False

                    # Save button
                            if st.button(
                                "💾 Save Changes",
                                key=f"save_{item['name']}"
                            ):
                                try:
                                    volunteer_supabase \
                                        .table("inventory") \
                                        .update(
                                            {
                                                "price": new_price,
                                                "stock_quantity": new_stock,
                                                "school_day_only":
                                                    new_school_day_only
                                            }
                                    ) \
                                    .eq(
                                        "name",
                                        item["name"]
                                    ) \
                                    .execute()

                                    st.success(
                                        f"{item['name']} updated! ✓"
                                    )

                                    st.rerun()

                                except Exception as e:
                                    st.error(
                                        f"Could not update "
                                        f"{item['name']}: {e}"
                                    )

                except Exception as e:
                    st.error(
                        f"Could not load inventory: {e}"
                    )

                    