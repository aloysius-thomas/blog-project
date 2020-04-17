from django.contrib import messages
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.base import View

from comment.forms import CommentForm
from comment.models import Comment
from .forms import ArticleForm
from .forms import ArticleImageForm
from .models import Article
from .models import ArticleImage


class ArticleObjectMixin(object):
    model = Article

    def get_object(self, queryset=None):
        pk = self.kwargs.get("id")
        return get_object_or_404(self.model, id=pk)


class ArticleCreateView(View):

    def post(self, request):

        ImageFormSet = modelformset_factory(ArticleImage,
                                            form=ArticleImageForm, extra=3)

        if request.method == 'POST':
            form = ArticleForm(request.POST, request.FILES)
            formset = ImageFormSet(request.POST, request.FILES,
                                   queryset=ArticleImage.objects.none())

            if form.is_valid() and formset.is_valid():
                post_form = form.save(commit=False)
                post_form.user = request.user
                post_form.save()

                for form in formset.cleaned_data:
                    image = form['image']
                    photo = ArticleImage(article=post_form, image=image)
                    photo.save()
                messages.success(request,
                                 "Posted!")
                return HttpResponseRedirect("/")
            else:
                print
                form.errors, formset.errors
        else:
            form = ArticleForm()
            formset = ImageFormSet(queryset=ArticleImage.objects.none())
        return render(request, 'blogapp/article_create.html',
                      {'form': form, 'formset': formset})

    def get(self, request):

        ImageFormSet = modelformset_factory(ArticleImage, form=ArticleImageForm, extra=3)

        if request.method == 'POST':
            form = ArticleForm(request.POST, request.FILES)
            formset = ImageFormSet(request.POST, request.FILES,
                                   queryset=ArticleImage.objects.none())

            if form.is_valid() and formset.is_valid():
                post_form = form.save(commit=False)
                post_form.user = request.user
                post_form.save()

                for form in formset.cleaned_data:
                    image = form['image']
                    photo = ArticleImage(article=post_form, image=image)
                    photo.save()
                messages.success(request,
                                 "Posted!")
                return HttpResponseRedirect("/")
            else:
                print
                form.errors, formset.errors
        else:
            form = ArticleForm()
            formset = ImageFormSet(queryset=ArticleImage.objects.none())
        return render(request, 'blogapp/article_create.html',
                      {'form': form, 'formset': formset})


class ArticleListView(ListView):
    queryset = Article.objects.all().order_by('-id')


class ArticleDetailView(ArticleObjectMixin, View):
    template_name = "blogapp/article_detail.html"
    context = dict()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj is not None:
            form = CommentForm(request.POST or None)
            self.context['form'] = form
            self.context['object'] = obj
            c = Comment.objects.filter(article=obj).order_by('-id')

            self.context['comments'] = c

        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj is not None:
            form = CommentForm(request.POST or None)
            if form.is_valid():
                s = form.save(commit=False)
                s.article = obj
                try:
                    s.added_by = request.user
                except Exception as e:
                    print(e)
                    return redirect('login')
                s.save()
                return HttpResponseRedirect(f'/blog/{obj.id}')
            c = Comment.objects.filter(article=obj).order_by('-id')
            self.context['object'] = obj
            self.context['comments'] = c
            self.context['form'] = form

        return render(request, self.template_name, self.context)


class ArticleUpdateView(UpdateView):
    form_class = ArticleForm
    template_name = 'blogapp/article_create.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get("id")
        return get_object_or_404(Article, id=pk)

    def get_success_url(self):
        success_url = "/blog/"
        return success_url


class ArticleDeleteView(DeleteView):
    success_url = "/blog/"

    def get_object(self, queryset=None):
        pk = self.kwargs.get("id")
        return get_object_or_404(Article, id=pk)
