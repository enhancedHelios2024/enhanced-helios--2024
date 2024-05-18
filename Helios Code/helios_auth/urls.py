
"""
Authentication URLs

Ben Adida (ben@adida.net)
"""

from django.conf.urls import url

from settings import AUTH_ENABLED_SYSTEMS
from . import views, url_names
from .views import (
    login_view,
    logout_view,
    home_view,
    find_user_view,
)


urlpatterns = [
    # basic static stuff
    # url(r'^admin$', d, name=url_names.AUTH_ADMINISTER),
    url(r'^$', views.index, name=url_names.AUTH_INDEX),
    url(r'^logout$', views.logout, name=url_names.AUTH_LOGOUT),
    url(r'^start/(?P<system_name>.*)$', views.start, name=url_names.AUTH_START),
    # # weird facebook constraint for trailing slash
    url(r'^after/$', views.after, name=url_names.AUTH_AFTER),
    url(r'^why$', views.perms_why, name=url_names.AUTH_WHY),
    url(r'^after_intervention$', views.after_intervention, name=url_names.AUTH_AFTER_INTERVENTION),
    url(r'^facial_recognition/classify/$',find_user_view, name='classify'),
    url(r'^facial_recognition/$',views.facial_recognition, name='facial_recognition'),
    # url(r'^facial_recognition/verify/$',views.facial_recognition_verify, name='verify'),
    url(r'^recombine_shares/$', views.recombine_shares, name="recombine_shares"),
    url(r'^classify_face/$', views.classify_face_view, name='classify_face'),

    url(r'^get_other_shares/$', views.get_other_shares, name='get_other_shares'),

]

# password auth
if 'password' in AUTH_ENABLED_SYSTEMS:
    from .auth_systems.password import urlpatterns as password_patterns
    urlpatterns.extend(password_patterns)

# twitter
if 'twitter' in AUTH_ENABLED_SYSTEMS:
    from .auth_systems.twitter import urlpatterns as twitter_patterns
    urlpatterns.extend(twitter_patterns)

# ldap
if 'ldap' in AUTH_ENABLED_SYSTEMS:
    from .auth_systems.ldapauth import urlpatterns as ldap_patterns
    urlpatterns.extend(ldap_patterns)