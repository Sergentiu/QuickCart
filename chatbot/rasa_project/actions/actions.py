from rasa_sdk import Action
import os
import django
import sys
from asgiref.sync import sync_to_async
from django.db.models import Q

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from shop.models import Product, FAQ, Policy
from cart.models import Order

# ---------------- FETCH PRODUCT NAMES FROM DATABASE ----------------
class ActionFetchProductNames(Action):
    def name(self):
        return "action_fetch_product_names"

    async def run(self, dispatcher, tracker, domain):
        try:
            products = await sync_to_async(list)(Product.objects.values_list('name', flat=True))
            print(f"DEBUG - Available products in database: {products}")
            if products:
                dispatcher.utter_message(f"Available products: {', '.join(products)}.")
            else:
                dispatcher.utter_message("No products found in the database.")
        except Exception as e:
            print(f"Error in ActionFetchProductNames: {str(e)}")
            dispatcher.utter_message("Sorry, I encountered an error while fetching the product list.")
        return []

# ---------------- FETCH PRODUCT PRICE ----------------
class ActionGetProductPrice(Action):
    def name(self):
        return "action_get_product_price"

    async def run(self, dispatcher, tracker, domain):
        product_name = tracker.get_slot("product_name")
        print(f"DEBUG - Received product name: {product_name}")

        if not product_name:
            dispatcher.utter_message("I couldn't understand which product you're asking about. Could you please specify the product name?")
            return []

        try:
            # Create a more flexible search query
            search_terms = product_name.lower().split()
            print(f"DEBUG - Search terms: {search_terms}")
            
            q_objects = Q()
            for term in search_terms:
                q_objects |= Q(name__icontains=term)
            
            # First, get all matching products to see what we're finding
            matching_products = await sync_to_async(list)(Product.objects.filter(q_objects).values_list('name', flat=True))
            print(f"DEBUG - Matching products: {matching_products}")
            
            product = await sync_to_async(lambda: Product.objects.filter(q_objects).first())()
            print(f"DEBUG - Selected product: {product.name if product else None}")
            
            if product:
                dispatcher.utter_message(f"The price of {product.name} is ${product.price}.")
            else:
                # Get all products for debugging
                all_products = await sync_to_async(list)(Product.objects.values_list('name', flat=True))
                print(f"DEBUG - All products in DB: {all_products}")
                dispatcher.utter_message(f"Sorry, I couldn't find {product_name} in our database. Available products: {', '.join(all_products)}")
        except Exception as e:
            print(f"Error in action_get_product_price: {str(e)}")
            dispatcher.utter_message("Sorry, I encountered an error while fetching the product price.")

        return []

# ---------------- FETCH PRODUCT DETAILS ----------------
class ActionGetProductDetails(Action):
    def name(self):
        return "action_get_product_details"

    async def run(self, dispatcher, tracker, domain):
        product_name = tracker.get_slot("product_name")

        if not product_name:
            dispatcher.utter_message("I couldn't understand which product you're asking about. Could you please specify the product name?")
            return []

        try:
            # Create a more flexible search query
            search_terms = product_name.lower().split()
            q_objects = Q()
            for term in search_terms:
                q_objects |= Q(name__icontains=term)
            
            product = await sync_to_async(lambda: Product.objects.filter(q_objects).first())()
            
            if product:
                dispatcher.utter_message(f"Details for {product.name}: {product.description}")
            else:
                dispatcher.utter_message(f"Sorry, I couldn't find details for {product_name}. Please try using a different name or check our product list.")
        except Exception as e:
            dispatcher.utter_message("Sorry, I encountered an error while fetching the product details.")
            print(f"Error in action_get_product_details: {str(e)}")

        return []

# ---------------- CHECK ORDER STATUS ----------------
class ActionCheckOrderStatus(Action):
    def name(self):
        return "action_check_order_status"

    async def run(self, dispatcher, tracker, domain):
        order_id = tracker.get_slot("order_id")

        if not order_id:
            dispatcher.utter_message("I couldn't understand which order you're asking about. Could you please provide the order ID?")
            return []

        try:
            order = await sync_to_async(Order.objects.filter(id=order_id).first)()
            if order:
                dispatcher.utter_message(f"Your order {order_id} is currently: {order.status}")
            else:
                dispatcher.utter_message(f"Sorry, I couldn't find order {order_id}.")
        except Exception as e:
            dispatcher.utter_message("Sorry, I encountered an error while checking the order status.")
            print(f"Error in action_check_order_status: {str(e)}")

        return []

# ---------------- FETCH FAQ FROM DATABASE ----------------
class ActionGetFAQ(Action):
    def name(self):
        return "action_get_faq"

    async def run(self, dispatcher, tracker, domain):
        try:
            faqs = await sync_to_async(list)(FAQ.objects.all())
            if faqs:
                faq_list = "\n".join([f"- {faq.question}: {faq.answer}" for faq in faqs])
                dispatcher.utter_message(f"Here are some frequently asked questions:\n{faq_list}")
            else:
                dispatcher.utter_message("Sorry, I couldn't find any FAQs.")
        except Exception as e:
            dispatcher.utter_message("Sorry, I encountered an error while fetching FAQs.")
            print(f"Error in action_get_faq: {str(e)}")

        return []

# ---------------- FETCH POLICIES FROM DATABASE ----------------
class ActionGetPolicies(Action):
    def name(self):
        return "action_get_policies"

    async def run(self, dispatcher, tracker, domain):
        try:
            policies = await sync_to_async(list)(Policy.objects.all())
            if policies:
                policy_list = "\n".join([f"- {policy.title}: {policy.description}" for policy in policies])
                dispatcher.utter_message(f"Here are our policies:\n{policy_list}")
            else:
                dispatcher.utter_message("Sorry, I couldn't find any policies.")
        except Exception as e:
            dispatcher.utter_message("Sorry, I encountered an error while fetching policies.")
            print(f"Error in action_get_policies: {str(e)}")

        return []