from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView


class TextPlainView(TemplateView):
    def render_to_response(self, context, **kwargs):
        return super(TextPlainView, self).render_to_response(context, content_type='text/plain', **kwargs)


urlpatterns = patterns('',
    # Examples:
    url(r'^a/$', 'todoapp1.mobile1.views.index', name='indexa'),
    url(r'^$', 'todoapp1.mobile1.views.index', name='index'),
    url("^robots.txt$", TextPlainView.as_view(template_name="robots.txt")),
)
