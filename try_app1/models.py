from django.db import models

# Create your models here.
class Students(models.Model):

    id=models.IntegerField(primary_key=True)
    name=models.CharField(max_length=30)

    class Meta:
        managed = True
        db_table = 'students'

class Marks(models.Model):
    mid = models.ForeignKey('Students', on_delete = models.CASCADE)

    english = models.IntegerField()
    hindi = models.IntegerField()

    class meta:
        managed = True
        td_table = 'marks'