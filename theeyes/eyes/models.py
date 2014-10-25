from django.db import models

# Create your models here.


class Eye(models.Model):
    number = models.IntegerField()

    def __str__(self):
        return str(self.number)

    class Meta:
        ordering = ['number']


class EyeRelationship(models.Model):
    eye = models.ForeignKey(Eye, related_name="preferences")
    relative = models.ForeignKey(Eye, related_name="relatives")
    position = models.PositiveSmallIntegerField("Position", default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return str(self.eye.number) + " : " + str(self.relative.number)
