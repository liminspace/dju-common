from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate(request, objects, count=10, param_name='page', param_perpage=None, **kwargs):
    default_last = kwargs.pop('default_last', False)
    if objects is None:
        objects = []
    if param_perpage and param_perpage in request.GET and request.GET[param_perpage].isdigit():
        count = int(request.GET[param_perpage])
    paginator = Paginator(objects, count, **kwargs)
    default_page = paginator.num_pages if default_last else 1
    try:
        page = paginator.page(request.GET.get(param_name, default_page))
    except PageNotAnInteger:
        page = paginator.page(default_page)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    page.param_name = param_name
    return page
