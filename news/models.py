from django.db import models
from accounts.models import User

class NewsUnit(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.ManyToManyField('NewsTag', blank=True, related_name='news_units')
    category = models.ForeignKey('NewsCategory', on_delete=models.CASCADE, related_name='news_units')
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug")
    image = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name="Image")
    views_count = models.IntegerField(default=0, verbose_name="Views Count")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='news_units', verbose_name="Author")
    source_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Source Name")
    source_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="Source URL")
    is_published = models.BooleanField(default=True, verbose_name="Is Published")
    published_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "News Unit"
        verbose_name_plural = "News Units"
        ordering = ['-published_date']

class NewsCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    c_name = models.CharField(max_length=100, unique=True, verbose_name="Chinese Name")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "News Category"
        verbose_name_plural = "News Categories"
        ordering = ['name']

class NewsTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    c_name = models.CharField(max_length=100, unique=True, verbose_name="Chinese Name")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "News Tag"
        verbose_name_plural = "News Tags"
        ordering = ['name']