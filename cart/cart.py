from shop.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        # Retrieve the cart from the session, or create a new empty cart if it doesn't exist
        cart = request.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    ## 1. Products
    @property
    def products(self):
        # Fetch products from the database that are in the cart
        product_ids = self.cart.keys()
        cart_products = Product.objects.filter(id__in=product_ids)
        # Return a list of tuples (product, quantity)
        return [(prod, self.cart[str(prod.id)]) for prod in cart_products]

    ## 2. Length
    def __len__(self):
        # Get the total number of items in the cart (sum of all quantities)
        product_ids = self.cart.keys()
        cart_products = Product.objects.filter(id__in=product_ids)
        return sum([self.cart[str(prod.id)] for prod in cart_products])

    ## 3. Add product
    def add(self, productid, quantity):
        # Add or update the quantity of a product in the cart
        productid = str(productid)
        existing_quantity = self.cart.get(productid, 0)
        self.cart[productid] = quantity + existing_quantity
        self.save()

    ## 4. Empty cart
    def empty(self):
        # Clear the entire cart
        self.cart = {}
        self.save()

    ## 5. Total cart price
    @property
    def get_total_price(self):
        # Calculate the total price of all items in the cart
        product_ids = self.cart.keys()
        cart_products = Product.objects.filter(id__in=product_ids)
        return sum([prod.price * self.cart[str(prod.id)] for prod in cart_products])

    ## 6. Get items in the cart
    def get_items(self):
        items = []
        for product_id, quantity in self.cart.items():
            try:
                # Fetch product details for each item in the cart
                product = Product.objects.get(id=product_id)
                items.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'quantity': quantity,
                    'price': product.price,
                })
            except Product.DoesNotExist:
                continue  # Skip if product doesn't exist (error handling)
        return items

    def save(self):
        # Mark the session as modified to ensure changes are saved
        self.session.modified = True