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
# getting user model from get_user_model
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


class LoginView(TokenObtainPairView):
    """View for user login."""
    
    permission_classes = [permissions.AllowAny]


class TokenRefreshView(BaseTokenRefreshView):
    """View for refreshing JWT token."""
    
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for user profile."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


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
        queryset = Product.objects.all()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Search by name or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search) | queryset.filter(description__icontains=search)
        
        return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for the Review model."""
    
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.all()
        elif self.request.user.is_authenticated:
            return Review.objects.filter(user=self.request.user)
        return Review.objects.none()


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
        user = self.request.user
        return Cart.objects.filter(user=user)
    
    def list(self, request):
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        cart.items.all().delete()
        return Response({"message": "Cart cleared successfully"}, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.ModelViewSet):
    """ViewSet for the CartItem model."""
    
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        cart = get_object_or_404(Cart, user=user)
        return CartItem.objects.filter(cart=cart)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for the Order model."""
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.order_status in ['pending', 'processing']:
            order.order_status = 'cancelled'
            order.save()
            return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Cannot cancel this order"}, status=status.HTTP_400_BAD_REQUEST)


class CreatePaymentView(APIView):
    """View for creating a payment."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method')
        
        if not order_id or not payment_method:
            return Response({"error": "Order ID and payment method are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # In a real app, you would integrate with a payment gateway here
        # For this example, we'll just create a payment record
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


class ProcessPaymentView(APIView):
    """View for processing a payment."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            return Response({"error": "Payment ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(payment_id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # In a real app, you would process the payment with a payment gateway here
        # For this example, we'll just update the payment status
        payment.status = 'completed'
        payment.save()
        
        # Update order status
        order = payment.order
        order.payment_status = 'paid'
        order.order_status = 'processing'
        order.save()
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RefundRequestView(APIView):
    """View for requesting a refund."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = RefundSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            refund = serializer.save()
            return Response(RefundSerializer(refund).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin Dashboard Views
class DashboardSummaryView(APIView):
    """View for dashboard summary."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(payment_status='paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
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


class RecentOrdersView(generics.ListAPIView):
    """View for recent orders."""
    
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return Order.objects.all().order_by('-created_at')[:10]


class TopProductsView(APIView):
    """View for top products."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        top_products = Product.objects.annotate(
            order_count=Count('orderitem')
        ).order_by('-order_count')[:10]
        
        serializer = ProductSerializer(top_products, many=True)
        return Response(serializer.data)