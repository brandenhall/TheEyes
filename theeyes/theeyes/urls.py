from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from eyes.views import EyeViewSet
from creatures.views import (
    CreatureSet,
    HeroAnimationSet,
    UserCreatedCreatureSet,
    InteractionSet,
)


router = routers.DefaultRouter()
router.register(r'eyes', EyeViewSet)
router.register(r'creatures', CreatureSet)
router.register(r'heroanimations', HeroAnimationSet)
router.register(r'usercreatedcreatures', UserCreatedCreatureSet)
router.register(r'interactions', InteractionSet)

urlpatterns = patterns(
    '',
    url(r'^backend/api/', include(router.urls)),
    url(r'^backend/grappelli/', include('grappelli.urls')),
    url(r'^backend/admin/', include(admin.site.urls)),
    url(r'^backend/api-auth/', include('rest_framework.urls', namespace='rest_framework')),

)
