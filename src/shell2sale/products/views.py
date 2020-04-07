#from django.views import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404

from analytics.mixins import ObjectViewedMixin # remove to allow vistors to view product detail
from carts.models import Cart
from .models import Product


class ProductFeaturedListView(ListView):
	template_name = "products/list.html"

	def get_queryset(self, *args, **kwargs):
		request = self.request
		return Product.objects.all().featured()

# ObjectViewedMixin
class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
	template_name = "products/featured-detail.html"

	def get_queryset(self, *args, **kwargs):
		request = self.request
		return Product.objects.all().featured()



class UserProductHistoryView(LoginRequiredMixin, ListView):
	template_name = "products/user-history.html"

	def get_context_data(self, *args, **kwargs):
		context = super(UserProductHistoryView, self).get_context_data(*args, **kwargs)
		cart_obj, new_obj = Cart.objects.new_or_get(self.request)
		context['cart'] = cart_obj
		return context

	def get_queryset(self, *args, **kwargs):
		request = self.request
		views = request.user.objectviewed_set.by_model(Product, model_queryset=False)
		return views



class ProductListView(ListView):
    template_name = "products/list.html"

    # def get_context_data(self, *args, **kwargs):
    #     context = super(ProductListView, self).get_context_data(*args, **kwargs)
    #     print(context)
    #     return context

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()



# function based
def product_list_view(request):
	queryset = Product.objects.all()
	context = {
	    'object_list': queryset
	}
	return render(request, "products/list.html", context)

# ObjectViewedMixin
class ProductDetailSlugView(ObjectViewedMixin, DetailView):
	queryset = Product.objects.all()
	template_name = "products/detail.html"

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
		cart_obj, new_obj = Cart.objects.new_or_get(self.request)
		context['cart'] = cart_obj
		return context

	def get_object(self, *args, **kwargs):
		request = self.request
		slug = self.kwargs.get('slug')

		# instance = get_object_or_404(Product, slug=slug, active=True)
		try:
			instance = Product.objects.get(slug=slug, active=True)
		except Product.DoesNotExist:
			raise Http404('Oh product not found')
		except Product.MultipleObjectsReturned:
			qs = Product.objects.filter(slug=slug, active=True)
			instance = qs.first()
		except:
			raise Http404('I dunt know whats wrong...')

		# object_viewed_signal.send(instance.__class__, instance=instance, request=request) # signal sender, replace by Mixin to avoid repeat this code in every function
		return instance

# ObjectViewedMixin
class ProductDetailView(ObjectViewedMixin, DetailView):
	# queryset = Product.objects.all()
	template_name = "products/detail.html"

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
		# print(context)
		return context

    # way 1
	def get_object(self, *args, **kwargs):
		request = self.request
		pk = self.kwargs.get('pk')
		instance = Product.objects.get_by_id(pk)
		if instance is None:
			raise Http404("Oops product not exists")
		return instance

    # way 2
	# def get_queryset(self, *args, **kwargs):
	# 	request = self.request
	# 	pk = self.kwargs.get('pk')
	# 	return Product.objects.filter(pk=pk)


# function based
def product_detail_view(request, pk=None, *args, **kwargs):
	# instance = Product.objects.get(pk=pk, featured=True) #id
	# instance = get_object_or_404(Product, pk=pk)

	# way 1
	try:
		instance = Product.objects.get(id=pk)
	except Product.DoesNotExist:
		#print('Oops product not exists')
		raise Http404("Product doesn't exist")
	except:
		print('Oh something wrong')

	# way 2
	# qs = Product.objects.filter(id=pk)
	# print(qs)
	# if qs.exists() and qs.count() == 1:
	# 	instance = qs.first()
	# else:
	# 	raise Http404("Oops product not exists")

	context = {
	    'object': instance
	}
	return render(request, "products/detail.html", context)


