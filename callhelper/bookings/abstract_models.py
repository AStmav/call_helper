from django.db import models

class BaseModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(
                    auto_now_add=True,
                    verbose_name="Created at",
                    help_text="Timestamp when the object was created"
                )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']