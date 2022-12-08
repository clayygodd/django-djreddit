from .models import Category

def category_renderer(request):
    if request.user.is_authenticated and request.user.subscribed.all():
        return {
                "categories": Category.objects.all(),
                "subscribed_categories": request.user.subscribed.all(),
                }
    else:
        return {"categories": Category.objects.all(),}
