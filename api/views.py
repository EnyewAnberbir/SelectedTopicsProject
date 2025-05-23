from django.db.models import Count, Sum, Avg
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView as BaseTokenRefreshView
from rest_framework.decorators import action
from products.models import Category, Product, Review
from users.models import Address
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from payments.models import Payment, Refund
from .serializers import (
    UserSerializer, AddressSerializer, CategorySerializer, ProductSerializer,
    ReviewSerializer, CartSerializer, CartItemSerializer, OrderSerializer,
    OrderItemSerializer, PaymentSerializer, RefundSerializer
)
import logging

# Configure logging
logger = logging.getLogger(__name__)

def handle_exception(exc, context=None, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
    """
    Utility function to handle exceptions and return consistent error responses.
    Also logs the error for monitoring.
    """
    error_message = str(exc)
    if hasattr(exc, 'detail'):
        error_message = exc.detail
    
    # Log the error with context if available
    if context:
        logger.error(f"Error: {error_message}, Context: {context}")
    else:
        logger.error(f"Error: {error_message}")
    
    return Response(
        {"error": error_message},
        status=status_code
    )

def validate_required_fields(data, required_fields):
    """
    Utility function to validate required fields in request data.
    Returns (is_valid, error_response)
    """
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
        return False, Response(
            {"error": error_msg},
            status=status.HTTP_400_BAD_REQUEST
        )
    return True, None

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class RegisterView(generics.CreateAPIView):
    """View for user registration."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['username', 'email', 'password']
            )
            if not is_valid:
                return error_response

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'RegisterView', 'data': request.data},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class LoginView(TokenObtainPairView):
    """View for user login."""
    
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['username', 'password']
            )
            if not is_valid:
                return error_response

            return super().post(request, *args, **kwargs)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'LoginView'},
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class TokenRefreshView(BaseTokenRefreshView):
    """View for refreshing JWT token."""
    
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['refresh']
            )
            if not is_valid:
                return error_response

            return super().post(request, *args, **kwargs)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'TokenRefreshView'},
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for user profile."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            return Response(UserSerializer(user).data)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'UserProfileView', 'user_id': request.user.id},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for the Address model."""
    
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for the Category model."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for the Product model."""
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        try:
            queryset = Product.objects.all()
            
            # Filter by category
            category = self.request.query_params.get('category')
            if category:
                queryset = queryset.filter(category__slug=category)
            
            # Filter by price range
            min_price = self.request.query_params.get('min_price')
            max_price = self.request.query_params.get('max_price')
            if min_price:
                try:
                    min_price = float(min_price)
                    queryset = queryset.filter(price__gte=min_price)
                except ValueError:
                    logger.warning(f"Invalid min_price value: {min_price}")
            if max_price:
                try:
                    max_price = float(max_price)
                    queryset = queryset.filter(price__lte=max_price)
                except ValueError:
                    logger.warning(f"Invalid max_price value: {max_price}")
            
            # Filter by featured
            featured = self.request.query_params.get('featured')
            if featured and featured.lower() == 'true':
                queryset = queryset.filter(is_featured=True)
            
            # Search by name or description
            search = self.request.query_params.get('search')
            if search:
                queryset = queryset.filter(name__icontains=search) | queryset.filter(description__icontains=search)
            
            return queryset
        except Exception as e:
            logger.error(f"Error in ProductViewSet.get_queryset: {str(e)}")
            return Product.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['name', 'price', 'category']
            )
            if not is_valid:
                return error_response

            return super().create(request, *args, **kwargs)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'ProductViewSet.create', 'data': request.data},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'ProductViewSet.update', 'data': request.data},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for the Review model."""
    
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        try:
            if self.request.user.is_staff:
                return Review.objects.all()
            elif self.request.user.is_authenticated:
                return Review.objects.filter(user=self.request.user)
            return Review.objects.none()
        except Exception as e:
            logger.error(f"Error in ReviewViewSet.get_queryset: {str(e)}")
            return Review.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['product', 'rating', 'comment']
            )
            if not is_valid:
                return error_response

            # Check if user has already reviewed this product
            product_id = request.data.get('product')
            existing_review = Review.objects.filter(
                user=request.user,
                product_id=product_id
            ).first()
            
            if existing_review:
                return Response(
                    {"error": "You have already reviewed this product"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'ReviewViewSet.create', 'data': request.data},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Ensure user owns the review
            if instance.user != request.user and not request.user.is_staff:
                return Response(
                    {"error": "You don't have permission to edit this review"},
                    status=status.HTTP_403_FORBIDDEN
                )

            return super().update(request, *args, **kwargs)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'ReviewViewSet.update', 'data': request.data},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Ensure user owns the review
            if instance.user != request.user and not request.user.is_staff:
                return Response(
                    {"error": "You don't have permission to delete this review"},
                    status=status.HTTP_403_FORBIDDEN
                )

            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'ReviewViewSet.destroy'},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ProductReviewsView(generics.ListCreateAPIView):
    """View for listing and creating reviews for a specific product."""
    
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(product_id=product_id)
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        serializer.save(user=self.request.user, product=product)


class CartViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for the Cart model."""
    
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            user = self.request.user
            return Cart.objects.filter(user=user)
        except Exception as e:
            logger.error(f"Error in CartViewSet.get_queryset: {str(e)}")
            return Cart.objects.none()
    
    def list(self, request):
        try:
            user = request.user
            cart, created = Cart.objects.get_or_create(user=user)
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'CartViewSet.list', 'user_id': request.user.id},
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        try:
            user = request.user
            cart = get_object_or_404(Cart, user=user)
            cart.items.all().delete()
            return Response(
                {"message": "Cart cleared successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'CartViewSet.clear', 'user_id': request.user.id},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class CartItemViewSet(viewsets.ModelViewSet):
    """ViewSet for the CartItem model."""
    
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            user = self.request.user
            cart = get_object_or_404(Cart, user=user)
            return CartItem.objects.filter(cart=cart)
        except Exception as e:
            logger.error(f"Error in CartItemViewSet.get_queryset: {str(e)}")
            return CartItem.objects.none()

    def create(self, request, *args, **kwargs):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['product', 'quantity']
            )
            if not is_valid:
                return error_response

            # Get or create user's cart
            cart, _ = Cart.objects.get_or_create(user=request.user)
            
            # Check if product exists and is in stock
            product_id = request.data.get('product')
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            quantity = int(request.data.get('quantity', 1))
            if quantity <= 0:
                return Response(
                    {"error": "Quantity must be greater than 0"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if item already exists in cart
            cart_item = CartItem.objects.filter(cart=cart, product=product).first()
            if cart_item:
                cart_item.quantity += quantity
                cart_item.save()
                serializer = self.get_serializer(cart_item)
            else:
                serializer = self.get_serializer(data={
                    'cart': cart.id,
                    'product': product_id,
                    'quantity': quantity
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'CartItemViewSet.create', 'data': request.data},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['quantity']
            )
            if not is_valid:
                return error_response

            instance = self.get_object()
            quantity = int(request.data.get('quantity'))
            
            if quantity <= 0:
                return Response(
                    {"error": "Quantity must be greater than 0"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            instance.quantity = quantity
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'CartItemViewSet.update', 'data': request.data},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for the Order model."""
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            user = self.request.user
            if user.is_staff:
                return Order.objects.all()
            return Order.objects.filter(user=user)
        except Exception as e:
            logger.error(f"Error in OrderViewSet.get_queryset: {str(e)}")
            return Order.objects.none()
    
    def create(self, request, *args, **kwargs):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['shipping_address', 'payment_method']
            )
            if not is_valid:
                return error_response

            # Get user's cart
            cart = get_object_or_404(Cart, user=request.user)
            if not cart.items.exists():
                return Response(
                    {"error": "Cannot create order with empty cart"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save(
                user=request.user,
                total_price=cart.total_price
            )

            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )

            # Clear the cart
            cart.items.all().delete()

            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'OrderViewSet.create', 'data': request.data},
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        try:
            order = self.get_object()
            
            if order.order_status not in ['pending', 'processing']:
                return Response(
                    {"error": "Cannot cancel this order - invalid status"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if order.user != request.user and not request.user.is_staff:
                return Response(
                    {"error": "You don't have permission to cancel this order"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            order.order_status = 'cancelled'
            order.save()
            
            return Response(
                {"message": "Order cancelled successfully"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'OrderViewSet.cancel', 'order_id': pk},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class CreatePaymentView(APIView):
    """View for creating a payment."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['order_id', 'payment_method']
            )
            if not is_valid:
                return error_response

            order_id = request.data.get('order_id')
            payment_method = request.data.get('payment_method')
            
            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if order.payment_status == 'paid':
                return Response(
                    {"error": "Order is already paid"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create payment record
            payment = Payment.objects.create(
                user=request.user,
                order=order,
                payment_id=f"PAY-{order.order_number}",
                amount=order.total_price,
                payment_method=payment_method,
                status='pending'
            )
            
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'CreatePaymentView', 'data': request.data},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ProcessPaymentView(APIView):
    """View for processing a payment."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['payment_id']
            )
            if not is_valid:
                return error_response

            payment_id = request.data.get('payment_id')
            
            try:
                payment = Payment.objects.get(payment_id=payment_id, user=request.user)
            except Payment.DoesNotExist:
                return Response(
                    {"error": "Payment not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if payment.status == 'completed':
                return Response(
                    {"error": "Payment is already processed"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process payment (in a real app, this would integrate with a payment gateway)
            payment.status = 'completed'
            payment.save()
            
            # Update order status
            order = payment.order
            order.payment_status = 'paid'
            order.order_status = 'processing'
            order.save()
            
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'ProcessPaymentView', 'payment_id': payment_id},
                status_code=status.HTTP_400_BAD_REQUEST
            )


class RefundRequestView(APIView):
    """View for requesting a refund."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            is_valid, error_response = validate_required_fields(
                request.data,
                ['order_id', 'reason']
            )
            if not is_valid:
                return error_response

            order_id = request.data.get('order_id')
            reason = request.data.get('reason')
            
            try:
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if order.payment_status != 'paid':
                return Response(
                    {"error": "Cannot request refund for unpaid order"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if Refund.objects.filter(order=order).exists():
                return Response(
                    {"error": "Refund request already exists for this order"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            refund = Refund.objects.create(
                order=order,
                user=request.user,
                reason=reason,
                amount=order.total_price,
                status='pending'
            )
            
            serializer = RefundSerializer(refund)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'RefundRequestView', 'data': request.data},
                status_code=status.HTTP_400_BAD_REQUEST
            )


# Admin Dashboard Views
class DashboardSummaryView(APIView):
    """View for dashboard summary."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        try:
            total_orders = Order.objects.count()
            total_revenue = Order.objects.filter(payment_status='paid').aggregate(
                Sum('total_price')
            )['total_price__sum'] or 0
            total_customers = User.objects.filter(is_staff=False).count()
            total_products = Product.objects.count()
            
            pending_orders = Order.objects.filter(order_status='pending').count()
            processing_orders = Order.objects.filter(order_status='processing').count()
            shipped_orders = Order.objects.filter(order_status='shipped').count()
            delivered_orders = Order.objects.filter(order_status='delivered').count()
            
            return Response({
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'total_customers': total_customers,
                'total_products': total_products,
                'order_status': {
                    'pending': pending_orders,
                    'processing': processing_orders,
                    'shipped': shipped_orders,
                    'delivered': delivered_orders
                }
            })
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'DashboardSummaryView'},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecentOrdersView(generics.ListAPIView):
    """View for recent orders."""
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        try:
            return Order.objects.all().order_by('-created_at')[:10]
        except Exception as e:
            logger.error(f"Error in RecentOrdersView.get_queryset: {str(e)}")
            return Order.objects.none()


class TopProductsView(APIView):
    """View for top products."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        try:
            top_products = Product.objects.annotate(
                order_count=Count('orderitem')
            ).order_by('-order_count')[:10]
            
            serializer = ProductSerializer(top_products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return handle_exception(
                e,
                context={'view': 'TopProductsView'},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )