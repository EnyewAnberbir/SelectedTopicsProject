from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from products.models import Category, Product, ProductImage, Review
from users.models import Address
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from payments.models import Payment, Refund

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    
        class Meta:        model = User        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'password')        extra_kwargs = {'password': {'write_only': True}}        def validate_email(self, value):        """Validate that the email is unique during registration."""        if self.instance is None:  # Only check during creation, not update            if User.objects.filter(email=value).exists():                raise serializers.ValidationError("A user with this email address already exists.")        return value        def create(self, validated_data):
        # Make email and password required for user creation
        if not validated_data.get('email'):
            raise serializers.ValidationError({"email": "Email is required when creating a user"})
        if not validated_data.get('password'):
            raise serializers.ValidationError({"password": "Password is required when creating a user"})
        
        # Check if user with this email already exists
        email = validated_data.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email address already exists."})
        
        user = User.objects.create_user(**validated_data)
        Cart.objects.create(user=user)  # Create cart for new user
        return user
    
    def update(self, instance, validated_data):
        # Handle password update separately if provided
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
            
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for the Address model."""
    
    class Meta:
        model = Address
        fields = ('id', 'address_type', 'street_address', 'apartment_address', 'city', 
                  'state', 'country', 'postal_code', 'is_default')
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image')


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for the ProductImage model."""
    
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_primary')


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model."""
    
    user_email = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False)
    
    class Meta:
        model = Review
        fields = ('id', 'product', 'user', 'rating', 'comment', 'created_at', 'user_email', 'user_name')
        read_only_fields = ('user',)
        extra_kwargs = {'product': {'required': False}}
    
    def get_user_email(self, obj):
        return obj.user.email
    
    def get_user_name(self, obj):
        return obj.user.full_name
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # The product will be set by the view's perform_create method if not in validated_data
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model."""
    
    category_name = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'category', 'category_name', 'description', 
                  'price', 'discount_price', 'stock', 'is_available', 'is_featured', 
                  'created_at', 'images', 'average_rating', 'get_discount_percent')
    
    def get_category_name(self, obj):
        return obj.category.name
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for the CartItem model."""
    
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'total_price')
    
    def create(self, validated_data):
        user = self.context['request'].user
        cart, created = Cart.objects.get_or_create(user=user)
        
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': validated_data.get('quantity', 1)}
        )
        
        if not created:
            cart_item.quantity += validated_data.get('quantity', 1)
            cart_item.save()
        
        return cart_item


class CartSerializer(serializers.ModelSerializer):
    """Serializer for the Cart model."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price', 'total_items', 'updated_at')


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for the OrderItem model."""
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_price', 'quantity', 'total_price')
        read_only_fields = ('product_name', 'product_price', 'total_price')


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for the Order model."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address_id = serializers.IntegerField(write_only=True)
    billing_address_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'user', 'shipping_address', 'billing_address',
                  'shipping_address_id', 'billing_address_id', 'order_status', 
                  'payment_status', 'shipping_cost', 'total_price', 'items',
                  'payment_method', 'payment_id', 'notes', 'tracking_number',
                  'created_at', 'updated_at')
        read_only_fields = ('order_number', 'user', 'shipping_address', 'billing_address',
                           'order_status', 'payment_status', 'total_price')
    
    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Get addresses with proper error handling
        try:
            shipping_address_id = validated_data.pop('shipping_address_id')
            billing_address_id = validated_data.pop('billing_address_id')
            
            # Verify addresses exist and belong to the user
            shipping_address = Address.objects.filter(id=shipping_address_id, user=user).first()
            if not shipping_address:
                raise serializers.ValidationError({"shipping_address_id": "Invalid shipping address ID"})
                
            billing_address = Address.objects.filter(id=billing_address_id, user=user).first()
            if not billing_address:
                raise serializers.ValidationError({"billing_address_id": "Invalid billing address ID"})
        except Exception as e:
            raise serializers.ValidationError({"address": str(e)})
        
        # Get user's cart with error handling
        try:
            cart = Cart.objects.get(user=user)
            if not cart.items.exists():
                raise serializers.ValidationError({"cart": "Your cart is empty"})
        except Cart.DoesNotExist:
            # Create a cart if it doesn't exist
            cart = Cart.objects.create(user=user)
            raise serializers.ValidationError({"cart": "Your cart is empty"})
        except Exception as e:
            raise serializers.ValidationError({"cart": str(e)})
        
        # Calculate total price with error handling
        try:
            # Manually calculate total price to avoid dependency on Cart.total_price property
            total_price = sum(
                (item.product.current_price or item.product.price) * item.quantity 
                for item in cart.items.all()
            )
            shipping_cost = validated_data.get('shipping_cost', 0)
            if shipping_cost is None:
                shipping_cost = 0
        except Exception as e:
            raise serializers.ValidationError({"price": str(e)})
        
        # Create order with error handling
        try:
            # Remove shipping_cost and any other duplicate parameters from validated_data
            if 'shipping_cost' in validated_data:
                validated_data.pop('shipping_cost')
            if 'user' in validated_data:
                validated_data.pop('user')
            if 'shipping_address' in validated_data:
                validated_data.pop('shipping_address')
            if 'billing_address' in validated_data:
                validated_data.pop('billing_address')
            if 'total_price' in validated_data:
                validated_data.pop('total_price')
                
            order = Order.objects.create(
                user=user,
                shipping_address=shipping_address,
                billing_address=billing_address,
                total_price=total_price + shipping_cost,
                shipping_cost=shipping_cost,
                **validated_data
            )
        except Exception as e:
            raise serializers.ValidationError({"order": str(e)})
        
        # Create order items from cart items with error handling
        try:
            for cart_item in cart.items.all():
                try:
                    # Make sure product has a valid current_price
                    product_price = cart_item.product.current_price
                    if product_price is None or product_price <= 0:
                        product_price = cart_item.product.price
                    
                    # Create order item with proper error handling
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        product_name=cart_item.product.name,
                        product_price=product_price,
                        quantity=cart_item.quantity,
                        total_price=product_price * cart_item.quantity
                    )
                except Exception as e:
                    # Log the specific item error but continue with other items
                    print(f"Error processing cart item {cart_item.id}: {str(e)}")
            
            # Clear cart after order is created
            cart.items.all().delete()
        except Exception as e:
            # Roll back if there's an error with order items
            order.delete()
            raise serializers.ValidationError({"items": str(e)})
        
        return order


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model."""
    
    class Meta:
        model = Payment
        fields = ('id', 'payment_id', 'user', 'order', 'amount', 'currency',
                  'payment_method', 'status', 'created_at')
        read_only_fields = ('payment_id', 'user', 'created_at')


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for the Refund model."""
    
    order_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Refund
        fields = ('id', 'order', 'order_id', 'payment', 'amount', 'reason', 'status',
                  'refund_id', 'created_at')
        read_only_fields = ('order', 'payment', 'status', 'refund_id', 'created_at')
    
    def create(self, validated_data):
        user = self.context['request'].user
        order_id = validated_data.pop('order_id')
        order = Order.objects.get(id=order_id, user=user)
        
        # Find the associated payment
        try:
            payment = Payment.objects.filter(order=order, status='completed').first()
        except Payment.DoesNotExist:
            payment = None
        
        refund = Refund.objects.create(
            order=order,
            payment=payment,
            amount=validated_data.get('amount', order.total_price),
            reason=validated_data.get('reason', '')
        )
        
        return refund 