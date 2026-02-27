from django.contrib import admin
from .models import Product, ProductComponent, Vendor, ProductModel

# 定义Inline类，实现组件在产品页面的内嵌维护
class ProductComponentInline(admin.TabularInline):
    model = ProductComponent
    extra = 1  # 默认显示1个空白组件表单
    verbose_name = '产品组件'
    verbose_name_plural = '产品组件'
    fields = ('component_name', 'component_type', 'component_description')
    readonly_fields = ('created_at', 'updated_at')

# 注册产品模型，并关联Inline组件
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_type',  'created_at', 'updated_at')  # 列表页显示字段
    list_filter = ('product_type',)  # 列表页筛选条件
    search_fields = ('product_name', 'product_description')  # 列表页搜索字段
    fieldsets = (  # 详情页字段分组
        ('基础信息', {
            'fields': ('product_name', 'product_type', 'product_description')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # 可折叠
        }),
    )
    readonly_fields = ('created_at', 'updated_at')  # 只读字段
    inlines = [ProductComponentInline]  # 关联内嵌组件

class ProductComponentAdmin(admin.ModelAdmin):
    list_display = ('product', 'component_name', 'component_type', 'created_at')
    list_filter = ('component_type', 'product__product_type')
    search_fields = ('component_name', 'component_description', 'product__product_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'remark')
    fieldsets = (
        ('基础信息', {
            'fields': ('name', 'remark')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('product', 'model_name', 'created_at', 'updated_at')
    list_filter = ('product',)
    search_fields = ('model_name', 'remark', 'product__product_name')
    fieldsets = (
        ('基本信息', {
            'fields': ('product', 'model_name', 'remark')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')