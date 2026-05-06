"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.urls import include
from rest_framework.routers import DefaultRouter
from sportSchool.api import (
    UserViewSet,
    DepartmentViewSet,
    CoachViewSet,
    GroupViewSet,
    AthleteViewSet,
    AttendanceViewSet,
    TrainingHourViewSet,      # Обратите внимание на имя
    TrainingTypeViewSet,
    TrainingPlanViewSet,      # Если будешь использовать планы
    CompetitionViewSet,
    CompetitionResultViewSet,
    AdministrativeDocViewSet,
    RankAssignmentOrderViewSet,
    AthleteRankAssignmentViewSet,
    StatisticsViewSet,
    LoginView,
    LogoutView,
    MeView
)
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import path, re_path



router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'coaches', CoachViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'athletes', AthleteViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'training-hours', TrainingHourViewSet)
router.register(r'training-types', TrainingTypeViewSet)
router.register(r'competitions', CompetitionViewSet)
router.register(r'competition-results', CompetitionResultViewSet)
router.register(r'admin-docs', AdministrativeDocViewSet)
router.register(r'rankassignmentorders', RankAssignmentOrderViewSet)
router.register(r'athlete-rank-assignments', AthleteRankAssignmentViewSet)
router.register(r'statistics', StatisticsViewSet)
router.register(r'training-plans', TrainingPlanViewSet, basename='trainingplan')


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'detail': 'CSRF cookie set'})

urlpatterns = [
    
    path("api/auth/csrf/", get_csrf_token),
    path("api/auth/login/", LoginView.as_view()),
    path("api/auth/logout/", LogoutView.as_view()),
    path("api/auth/me/", MeView.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)