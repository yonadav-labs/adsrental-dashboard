from django.db import models


class BundlerTeam(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
