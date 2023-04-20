from djoser.urls.base import urlpatterns as djoser_urls

djoser_urls.pop(0)
djoser_urls.pop(0)
djoser_urls.pop()
djoser_urls.pop()
djoser_urls.pop()
djoser_urls.pop()
djoser_urls.pop(2)
djoser_urls.pop(2)

urlpatterns = djoser_urls
