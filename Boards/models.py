from django.contrib.auth.models import User
from django.db import models
from django.utils.text import Truncator
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Board(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()
    
    def get_topics_count(self):
        return self.topics.count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()
    
    def save(self, *args, **kwargs):
        cache.delete(f'board_{self.id}')
        cache.delete('all_boards')
        super().save(*args, **kwargs)


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, related_name='topics', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        return Truncator(self.message).chars(30)

@receiver([post_save,post_delete], sender=Board)
def clear_board_cache(sender, instance, **kwargs):
    cache.delete(f'board_{instance.id}')
    cache.delete('all_boards')