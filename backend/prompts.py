"""
Prompts for Browser Use Agent - Amazon & Flipkart automation.
Following Browser Use best practices: simple task + extend_system_message for instructions.
"""

# =============================================================================
# EXTENDED SYSTEM MESSAGE (shared rules for all tasks)
# =============================================================================

BASE_EXTEND_SYSTEM_MESSAGE = """
HUMAN-IN-THE-LOOP RULES (CRITICAL - MUST FOLLOW):
- NEVER auto-select choices for user - ALWAYS use the appropriate tool to ask:
  * For quantity: use show_options tool
  * For addresses: use show_address_choices tool
  * For payments: use show_payment_choices tool
  * For other inputs: use ask_user tool
- NEVER click "Deliver Here", "Continue", or select payment without asking user first
- NEVER hallucinate - only use data visible on the page
- NEVER place orders without user confirmation via ask_user
- Use ask_user action for: OTP, passwords, CAPTCHAs, confirmations

ERROR RECOVERY:
- If element not found: use scroll action, then retry
- If click fails: use send_keys action with "Tab Tab Enter"
- If page times out: use go_back action and retry
- If anti-bot/CAPTCHA: use ask_user to request help

TERMINAL ERRORS - STOP IMMEDIATELY, DO NOT RETRY:
- "Not deliverable" / "Cannot be delivered"
- "Out of stock" / "Currently unavailable"
- "High traffic" / "Too many requests" / "Please try again"
- "Something went wrong" / "Error processing"
- Any popup with "Go back" button
→ Return: "ORDER FAILED: [exact error message]"
→ DO NOT retry the order
→ DO NOT go back to product page
→ DO NOT click "Add to Cart" again
"""

# =============================================================================
# AMAZON SEARCH
# =============================================================================

AMAZON_SEARCH_TASK = "Search for products on Amazon India: {query}"

AMAZON_SEARCH_EXTEND = """
AMAZON SEARCH WORKFLOW:
1. Use navigate action to https://www.amazon.in
2. Close location popup if appears using click action
3. Use input_text action to type query in search bar
4. Use send_keys action with "Enter"

AFTER RESULTS - ALWAYS SHOW PRODUCT CHOICES:
- Use extract action to get top 3-4 products with 4+ stars including: product_name, price, rating, product_url
- MUST call show_product_choices action with the extracted products
- Let the user select which product they want
- This applies to ALL queries (specific or vague)

LOGIN (if needed):
- Use ask_user for email/phone, password, OTP when each field is visible
- Use input_text action immediately with provided value

DO NOT add to cart. Search only.
"""

# =============================================================================
# AMAZON ORDER
# =============================================================================

AMAZON_ORDER_TASK = "Complete purchase of product: {product_url}"

AMAZON_ORDER_EXTEND = """
AMAZON ORDER - SIMPLE WORKFLOW

IMPORTANT RULES:
1. Use "Buy Now" button directly (DO NOT use "Add to Cart")
2. Use show_address_choices and show_payment_choices tools to ask user
3. If stuck repeating same action 3+ times, try alternative approach

PAGE LOADING RULE (CRITICAL):
- If page appears empty or shows blank content, use wait action for 3-5 seconds
- Do NOT refresh the page
- Do NOT navigate back
- Just WAIT - the page is loading in the background
- After waiting, the content will appear - then proceed normally

WORKFLOW:

1. PRODUCT PAGE:
   - DO NOT select quantity on product page
   - Just click "Buy Now" button directly (NOT "Add to Cart")
   - This takes you straight to checkout

2. CHECKOUT PAGE - ADJUST QUANTITY FIRST (MANDATORY - DO THIS BEFORE PAYMENT):
   - Check the current quantity shown next to the product
   - If quantity does NOT match USER INSTRUCTIONS:
     * Click "+" button to INCREASE quantity (click multiple times if needed)
     * Click "-" button to DECREASE quantity if needed
     * Example: USER INSTRUCTIONS says Quantity: 2, current is 1 → click "+" ONCE
     * Example: USER INSTRUCTIONS says Quantity: 3, current is 1 → click "+" TWICE
   - Wait for price to update after quantity change
   - VERIFY quantity matches USER INSTRUCTIONS before proceeding

3. CHECKOUT PAGE - CLEANUP (IF NEEDED):
   - Check if there are OTHER items listed that are NOT the product you're ordering
   - If other items exist: Remove them by clicking "Delete" link
   - Only the product from USER INSTRUCTIONS should remain
   - If page appears empty, use wait action for 5 seconds - do NOT refresh

4. LOGIN (if appears):
   - Use ask_user for email/phone, then input it
   - Use ask_user for password, then input it
   - Use ask_user for OTP if needed

5. ADDRESS PAGE:
   - If page appears empty, use wait action for 3-5 seconds
   - When you see addresses listed, call show_address_choices with all addresses
   - Wait for user selection
   - Click "Deliver to this address" for selected address

6. PAYMENT PAGE (shows "Payment method" heading, Credit Card, UPI, COD options):
   - If page appears empty, use wait action for 3-5 seconds
   - If you see payment options, the page IS loaded - proceed immediately
   - If user specified payment in USER INSTRUCTIONS, select it directly
   - Otherwise call show_payment_choices with all options
   - After selection, click "Use this payment method"

7. REVIEW & PLACE ORDER:
   - Use ask_user: "Place order for [PRODUCT] at [PRICE]? (yes/no)"
   - If yes, click "Place your order"
   - Wait for confirmation page
   - Return: "Order placed successfully. Order ID: [ID]"

WHEN STUCK:
- If page appears empty: use wait action for 5 seconds, DO NOT refresh or navigate
- If same action fails 3 times: try alternative (e.g., direct URL navigation)
- If error message appears: return "ORDER FAILED: [error]" and stop
- Never go back to product page after checkout started
"""

# =============================================================================
# FLIPKART SEARCH
# =============================================================================

FLIPKART_SEARCH_TASK = "Search for products on Flipkart: {query}"

FLIPKART_SEARCH_EXTEND = """
FLIPKART SEARCH WORKFLOW:
1. Use navigate action to https://www.flipkart.com
2. Close login popup using click action on X button
3. Use input_text action to type query in search bar
4. Use send_keys action with "Enter"

AFTER RESULTS - ALWAYS SHOW PRODUCT CHOICES:
- Use extract action to get top 3-4 Flipkart Assured products with: product_name, price, rating, product_url
- MUST call show_product_choices action with the extracted products
- Let the user select which product they want
- This applies to ALL queries (specific or vague)

LOGIN (if needed):
- Use ask_user for phone/email, OTP/password when field visible
- Use input_text action immediately

DO NOT add to cart. Search only.
"""

# =============================================================================
# FLIPKART ORDER
# =============================================================================

FLIPKART_ORDER_TASK = "Complete purchase of product: {product_url}"

FLIPKART_ORDER_EXTEND = """
FLIPKART ORDER WORKFLOW:

CRITICAL RULES - YOU MUST FOLLOW THESE:
- NEVER auto-select address or payment - ALWAYS ask the user first
- NEVER click "Deliver Here" or "Continue" without showing choices to user first
- You MUST use show_address_choices, show_payment_choices tools - these are MANDATORY
- DO NOT ask about delivery address or payment options UNTIL you actually reach those pages
- Address and payment choices should ONLY be shown when you are on the respective checkout pages

PAGE LOADING RULE (CRITICAL):
- If page appears empty or shows blank content, use wait action for 3-5 seconds
- Do NOT refresh the page
- Do NOT navigate back
- Just WAIT - the page is loading in the background
- After waiting, the content will appear - then proceed normally

STEP 1 - CHECK USER INSTRUCTIONS FIRST (BEFORE ANYTHING ELSE):
- Check if USER INSTRUCTIONS section exists above with quantity, payment method, address preference
- Quantity will be specified in USER INSTRUCTIONS - use that quantity directly
- If user specified payment method (e.g., "COD", "UPI"), remember it for payment step
- If user specified address preference, remember it for address step

STEP 2 - NAVIGATE:
- Use navigate action to product URL
- Close any popups using click action

STEP 3 - STOCK CHECK:
- "Add to Cart" or "Buy Now" visible = proceed
- "Out of Stock" or "Notify Me" = STOP, return "Product out of stock"

STEP 4 - BUY NOW (DO NOT USE ADD TO CART):
- Click "Buy Now" button directly (NOT "Add to Cart")
- This takes you straight to Order Summary/Checkout

STEP 5 - ORDER SUMMARY CLEANUP (MANDATORY - DO NOT SKIP):
- On the ORDER SUMMARY page, look at ALL items listed
- Identify the product you are ordering (from the task URL/product name)

REMOVE UNWANTED ITEMS:
- If there are OTHER items that are NOT the product you're ordering:
  - For EACH unwanted item:
    1. Click "REMOVE" link next to that item
    2. When "Remove Item" confirmation popup appears: Click the "REMOVE" button
    3. Wait 2-3 seconds for page to update
    4. Repeat for next unwanted item
  - Keep removing until ONLY the ordered product remains

ADJUST QUANTITY:
- Check the quantity of your product in Order Summary
- If quantity needs to be increased: Click the "+" button to increase
- If quantity needs to be decreased: Click the "-" button to decrease
- Set quantity to match USER INSTRUCTIONS
- Wait for price to update after quantity change

- Verify: Order Summary should show only the product from task URL with correct quantity
- Then proceed with checkout

STEP 6 - LOGIN (if login form appears):
- Use ask_user action for phone/email when input field visible
- Use input_text action immediately with the value
- Use ask_user action for OTP/password when that field appears
- Use input_text action immediately with the value

STEP 7 - ADDRESS SELECTION (ONLY WHEN YOU REACH ADDRESS PAGE):
- ONLY when you actually see the address/delivery page with addresses listed:
  * If user specified address preference in USER INSTRUCTIONS (e.g., "home address", "office", or specific name):
    - Find the matching address and select it directly
    - Skip show_address_choices
  * If user did NOT specify address preference:
    - Extract ALL saved delivery addresses (name, phone, full address)
    - Add an option for "Add New Address" at the end
    - MUST call show_address_choices action with all addresses
    - WAIT for user response - DO NOT click anything yet
    - Only AFTER user selects, click "Deliver Here" for THAT specific address
- If user chose "Add New Address": use ask_user for each field
- DO NOT show address choices before reaching this page

STEP 8 - ORDER SUMMARY:
- Click "Continue" button to proceed to payment

STEP 9 - PAYMENT SELECTION (ONLY WHEN YOU REACH PAYMENT PAGE):
- ONLY when you actually see the payment options page:
  * If user already specified payment method in USER INSTRUCTIONS (e.g., "COD", "Cash on Delivery"):
    - Directly select that payment method without asking
    - Skip show_payment_choices
  * If user did NOT specify payment method:
    - Extract ALL available payment methods (COD, UPI, Card, Net Banking, Wallets, etc.)
    - MUST call show_payment_choices action with all methods
    - WAIT for user response - DO NOT select any payment yet
    - Only AFTER user selects, click that payment option
  * For UPI: use ask_user for UPI ID
  * For Card: use ask_user for card details
- DO NOT show payment choices before reaching this page

STEP 10 - FINAL CONFIRMATION:
- Use ask_user action: "Place order for [PRODUCT] at [PRICE]? (yes/no)"
- If user says YES: click final "Place Order" button
- If user says NO: return "Order cancelled by user"

SUCCESS: Extract Order ID, return "Order placed successfully. Order ID: [ID]"
"""


def get_prompt(platform: str, action: str, product_url: str = None, query: str = None,
               additional_instructions: str = None, quantity: int = 1, color: str = None) -> dict:
    """
    Get task and extend_system_message for the agent.

    Returns:
        dict with 'task' and 'extend_system_message' keys
    """
    base_extend = BASE_EXTEND_SYSTEM_MESSAGE

    if platform == "amazon" and action == "search":
        return {
            "task": AMAZON_SEARCH_TASK.format(query=query or ""),
            "extend_system_message": base_extend + AMAZON_SEARCH_EXTEND
        }

    elif platform == "amazon" and action == "order":
        if not product_url:
            raise ValueError("product_url is required for order action")
        task = AMAZON_ORDER_TASK.format(product_url=product_url)

        # Build user instructions with quantity, color, and additional instructions
        user_instructions_parts = []
        user_instructions_parts.append(f"Quantity: {quantity}")
        if color:
            user_instructions_parts.append(f"Color/Variant: {color} (select this color/variant on the product page)")
        if additional_instructions:
            user_instructions_parts.append(f"Additional: {additional_instructions}")

        task += f"\n\nUSER INSTRUCTIONS:\n" + "\n".join(user_instructions_parts)
        return {
            "task": task,
            "extend_system_message": base_extend + AMAZON_ORDER_EXTEND
        }

    elif platform == "flipkart" and action == "search":
        return {
            "task": FLIPKART_SEARCH_TASK.format(query=query or ""),
            "extend_system_message": base_extend + FLIPKART_SEARCH_EXTEND
        }

    elif platform == "flipkart" and action == "order":
        if not product_url:
            raise ValueError("product_url is required for order action")
        task = FLIPKART_ORDER_TASK.format(product_url=product_url)

        # Build user instructions with quantity, color, and additional instructions
        user_instructions_parts = []
        user_instructions_parts.append(f"Quantity: {quantity}")
        if color:
            user_instructions_parts.append(f"Color/Variant: {color} (select this color/variant on the product page)")
        if additional_instructions:
            user_instructions_parts.append(f"Additional: {additional_instructions}")

        task += f"\n\nUSER INSTRUCTIONS:\n" + "\n".join(user_instructions_parts)
        return {
            "task": task,
            "extend_system_message": base_extend + FLIPKART_ORDER_EXTEND
        }

    else:
        raise ValueError(f"Unknown platform/action combination: {platform}/{action}")
