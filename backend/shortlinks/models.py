import hashlib

from django.db import models

from constants import CODE_LEN


class ShortLink(models.Model):
    """Модель для хранения коротких ссылок."""
    original_url = models.URLField(unique=True)
    short_code = models.CharField(max_length=CODE_LEN, unique=True)

    def generate_short_code(self):
        """Генерация короткого кода на основе оригинального URL."""
        return hashlib.md5(self.original_url.encode()).hexdigest()[:CODE_LEN]

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_short_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.original_url} -> {self.short_code}'
