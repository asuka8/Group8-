from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    user_name = models.CharField(max_length=20, default = '', unique = True)

    USERNAME_FIELD = 'user_name'

    def __str__(self):
        return self.username
    
class UserProfile(models.Model):
    user_id = models.OneToOneField(User, on_delete = models.CASCADE)
    bio = models.TextField(max_length = 1000, default='')

    class Meta:
        verbose_name = '自己紹介'
        verbose_name_plural = '自己紹介'

    def __str__(self):
        return f'{self.user_id.user_name}:{self.bio[:50]}'
    
class Guide(models.Model):
    user_id = models.OneToOneField(User, on_delete = models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    content = models.TextField(max_length=2000, default='')
    created_at = models.DateField(auto_now_add = True)
    updated_at = models.DateField(auto_now = True)

    class Meta:
        verbose_name = 'コメント'
        verbose_name_plural = 'コメント'
    
    def __str__(self):
        return f'{self.user_id.user_name}:{self.content[:50]}'
    
class Like_Dislike(models.Model):
    user_id = models.OneToOneField(User, on_delete = models.CASCADE)
    guide_id = models.OneToOneField(Guide, on_delete= models.CASCADE)
    status = models.BooleanField(blank = True) # Like:0, Dislike:1

    def __str__(self):
        return f'{self.user_id.user_name}:{self.status}'

