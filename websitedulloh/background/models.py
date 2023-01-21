from django.db import models

class Background(models.Model):
    name = models.TextField()
    image = models.ImageField(upload_to = 'background/img')

    def __str__(self):
        return self.name
    
