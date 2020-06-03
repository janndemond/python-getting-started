from django.db.models.signals import post_save, post_init

from django.contrib.auth.models import User
from   django.dispatch import receiver
from .models import profile
@receiver(post_save,sender=User)
def create_profile(sender,instance, created,**kwargs ):
    if created:
        profile.objects.create(user=instance)

@receiver(post_init,sender=User)
def create_profile(sender,instance, created,**kwargs ):
    if created:
        profile.objects.create(user=instance)
@receiver(post_save,sender=User)
def seva_profile(sender,instance,**kwargs):
    instance.profile.save()
