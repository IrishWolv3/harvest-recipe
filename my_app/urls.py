from django.urls import include
from django.views.generic import RedirectView

urlpatterns = [
    path('', views.index, name='index'),
    path('my_app/', include('my_app.urls')),
    path('', RedirectView.as_view(url='my_app/', permanent=True)),
]