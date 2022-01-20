from pickle import TRUE
from django.db import models

# Create your models here.


class UserTables(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100)
    user_email = models.CharField(max_length=100)
    table_name = models.CharField(unique=TRUE, max_length=60, null=False)
    table_schema = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_table"
