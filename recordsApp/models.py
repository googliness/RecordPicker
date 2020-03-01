from django.db import models


class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    year = models.IntegerField()
    rated = models.CharField(max_length=60)
    poster = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'movie'
