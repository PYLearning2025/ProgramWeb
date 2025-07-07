from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import NewsUnit

def news_list(request):
    news_list = NewsUnit.objects.all().order_by('-published_date')
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/list.html', locals())

def news_unit(request, slug):
    try:
        news_unit = NewsUnit.objects.get(slug=slug)
    except NewsUnit.DoesNotExist:
        return redirect('NewsList')
    
    return render(request, 'news/unit.html', locals())