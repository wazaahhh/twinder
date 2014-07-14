from django.conf.urls import patterns, include, url
from django.contrib import admin
import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'twinder2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^mark/$', views.mark, name='mark'),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^survey/$', views.survey, name='survey'),
    url(r'^tweets/$', views.index2, name='index2'),
    url(r'^stat/$', views.statistics, name='stat'),
    url(r'^usure/$', views.usure, name='usure'),
)