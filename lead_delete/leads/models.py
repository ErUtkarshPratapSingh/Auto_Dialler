from django.db import models

class Lead(models.Model):
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, default = 'pending')
    received_at = models.DateTimeField(auto_now_add=True)
    delete_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.phone_number} - {self.status}"
     
