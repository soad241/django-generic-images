import django.dispatch

image_saved = django.dispatch.Signal(providing_args=["instance"])
image_deleted = django.dispatch.Signal(providing_args=["instance"])