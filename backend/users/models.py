from django.db import models


class Follow(models.Model):
    '''Following to authors.'''

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        null=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        null=False
    )

    class Meta:
        unique_together = ('user', 'author',)
