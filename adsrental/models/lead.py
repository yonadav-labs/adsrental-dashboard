from django.db import models


class Lead(models.Model):
    name = models.CharField(max_length=255, db_column='Name', db_index=True)
    title = models.CharField(max_length=255, db_column='Title')
    address = models.CharField(max_length=255, db_column='Address')
    annual_revenue = models.BigIntegerField(db_column='AnnualRevenue')

    def __str__(self):
        return self.name
