from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin  # MPTT自带的树形拖拽Admin
from .models import AdminDiv, Customer, CustomerProduct
from django import forms
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse

# 自定义Select Widget：为<option>添加data-parent属性
class AdminDivTreeSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        # 先调用父类生成基础option数据
        option = super().create_option(name, value, label, selected, index, subindex, attrs)

        # 若value不为空（排除空选项），添加data-parent属性
        if value:
            try:
                admin_div = AdminDiv.objects.get(pk=value)
                # 赋值父级ID（无父级则为0）
                option['attrs']['data-parent'] = admin_div.parent_id or 0
            except AdminDiv.DoesNotExist:
                option['attrs']['data-parent'] = 0

        return option

# 行政区划：树形展示+拖拽排序（原生MPTT功能，无需额外插件）
class AdminDivAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'indented_title', 'level', 'created_at']  # list_display允许显示non-editable字段
    list_filter = ['level']  # 列表筛选也允许用level
    search_fields = ['name']
    autocomplete_fields = ['parent']  # 添加自动完成功能，实现可输入可选择
    fieldsets = (
        # 移除fieldsets中的level字段（因为editable=False）
        ('基础信息', {'fields': ('name', 'parent')}),
        ('时间信息', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'updated_at']  # level不在其中（mptt自动维护，无需手动只读）
    mptt_level_indent = 20
    list_per_page = 20


    # 自定义只读字段，展示level值
    def show_level(self, obj):
        return obj.level  # 调用mptt自动生成的level字段
    show_level.short_description = '层级'  # 自定义显示名称
    
    # 自定义indented_title字段的显示名称
    def indented_title(self, obj):
        return super().indented_title(obj)
    indented_title.short_description = '名称'


# 客户单位：应用带data-parent的树形下拉框
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'admin_div', 'created_at']
    list_filter = ['admin_div__level', 'admin_div__parent']
    search_fields = ['name', 'admin_div__name']
    fieldsets = (
        ('客户信息', {'fields': ('name', 'admin_div', 'intro')}),
        ('时间信息', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'admin_div':
            # 1. 指定自定义Widget（添加data-parent）
            # kwargs['widget'] = AdminDivTreeSelect()

            # 2. 按树形排序，下拉框显示带缩进的名称
            kwargs['queryset'] = AdminDiv.objects.all().order_by('tree_id', 'lft')

            # 3. 自定义选项文本（带层级缩进符）
            # kwargs['label_from_instance'] = lambda obj: f"{'—' * obj.level} {obj.name}"

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('customer-profile/', self.admin_site.admin_view(self.customer_profile_view), name='customer_profile'),
            path('api/admin-divs/', self.admin_site.admin_view(self.get_admin_divs), name='api_admin_divs'),
            path('api/customer/<int:customer_id>/', self.admin_site.admin_view(self.get_customer_info), name='api_customer_info'),
        ]
        return custom_urls + urls
    
    def customer_profile_view(self, request):
        from django.shortcuts import render
        return render(request, 'admin/customers/customer_profile.html')
    
    def get_admin_divs(self, request):
        from django.http import JsonResponse
        # 获取所有行政区划，按树形结构组织
        admin_divs = []
        
        def build_tree(node):
            item = {
                'id': node.id,
                'name': node.name,
                'children': []
            }
            # 添加该行政区划下的客户
            for customer in node.customers.all():
                item['children'].append({
                    'id': f'customer_{customer.id}',
                    'name': customer.name,
                    'is_customer': True,
                    'customer_id': customer.id
                })
            # 递归处理子行政区划
            for child in node.children.all():
                item['children'].append(build_tree(child))
            return item
        
        # 从根节点开始构建
        for root in AdminDiv.objects.filter(parent__isnull=True):
            admin_divs.append(build_tree(root))
        
        return JsonResponse(admin_divs, safe=False)
    
    def get_customer_info(self, request, customer_id):
        from django.http import JsonResponse
        try:
            customer = Customer.objects.get(id=customer_id)
            # 客户基本信息
            basic_info = {
                'name': customer.name,
                'admin_div': str(customer.admin_div),
                'intro': customer.intro or '',
                'created_at': customer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': customer.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            # 客户产品清单
            products = []
            for cp in customer.products.all():
                products.append({
                    'product_model': str(cp.product_model),
                    'vendor': str(cp.vendor),
                    'integrator': str(cp.integrator) if cp.integrator else '',
                    'purchase_date': cp.purchase_date.strftime('%Y-%m-%d') if cp.purchase_date else '',
                    'quantity': cp.quantity,
                    'remark': cp.remark or ''
                })
            return JsonResponse({
                'basic_info': basic_info,
                'products': products
            })
        except Customer.DoesNotExist:
            return JsonResponse({'error': '客户不存在'}, status=404)


class CustomerProductAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product_model', 'vendor', 'integrator', 'purchase_date', 'quantity', 'created_at', 'updated_at')
    list_filter = ('customer', 'vendor', 'integrator', 'purchase_date')
    search_fields = ('customer__name', 'product_model__model_name', 'product_model__product__product_name', 'vendor__name', 'integrator__name', 'remark')
    autocomplete_fields = ('customer', 'product_model', 'vendor', 'integrator')
    fieldsets = (
        ('基本信息', {
            'fields': ('customer', 'product_model', 'vendor', 'integrator', 'purchase_date', 'quantity', 'remark')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20




# 添加自定义菜单
from django.contrib.admin import AdminSite

# 扩展AdminSite类
class CustomAdminSite(AdminSite):
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # 添加自定义菜单
        custom_app = {
            'name': '自定义功能',
            'app_label': 'custom',
            'models': [
                {
                    'name': '客户档案',
                    'object_name': 'CustomerProfile',
                    'perms': {'change': True},
                    'admin_url': '/admin/Customers/customer/customer-profile/',
                    'add_url': None
                }
            ]
        }
        app_list.insert(0, custom_app)
        return app_list

# 替换默认的admin site
from django.contrib import admin
admin.site = CustomAdminSite(name='admin')

# 重新注册所有模型
from .models import AdminDiv, Customer, CustomerProduct
from Products.models import Vendor, Product, ProductComponent, ProductModel

# 重新注册模型
admin.site.register(AdminDiv, AdminDivAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerProduct, CustomerProductAdmin)

# 注册Products模型
from Products.admin import VendorAdmin, ProductAdmin, ProductComponentAdmin, ProductModelAdmin
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductComponent, ProductComponentAdmin)
admin.site.register(ProductModel, ProductModelAdmin)