from django.shortcuts import render, get_object_or_404
import markdown
import re
from collections.abc import Iterable

from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q
# Create your views here.

from django.http import HttpResponse
from .models import Target, Compound
from django.views.generic import ListView

#home视图函数
def home(request):
    return render(request, 'vsgcdb/home.html')

#搜索页面
def search(request):
    q = request.GET.get('q')

    if not q:
        error_msg = "Pleace type in"
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return redirect('blog:index')

    compound_list = Compound.objects.filter(Q(name__exact=q) | Q(smiles__exact=q))
    return render(request, 'vsgcdb/search.html', {'compound_list' : compound_list})