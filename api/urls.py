from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet, basename='cart-item')
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'addresses', views.AddressViewSet, basename='address')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Router generated URLs
    path('', include(router.urls)),
    
    # Product reviews
    path('products/<int:product_id>/reviews/', views.ProductReviewsView.as_view(), name='product-reviews'),
    
    # Payment endpoints
    path('payments/create/', views.CreatePaymentView.as_view(), name='create-payment'),
    path('payments/process/', views.ProcessPaymentView.as_view(), name='process-payment'),
    path('payments/refund/', views.RefundRequestView.as_view(), name='refund-request'),
    
    # Dashboard endpoints (for admin)
    path('dashboard/summary/', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/recent-orders/', views.RecentOrdersView.as_view(), name='recent-orders'),
    path('dashboard/top-products/', views.TopProductsView.as_view(), name='top-products'),
] 