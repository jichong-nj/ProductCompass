from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin  # MPTT自带的树形拖拽Admin
from .models import AdminDiv, Customer
from django import forms

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
@admin.register(AdminDiv)
class AdminDivAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'indented_title', 'level', 'created_at']  # list_display允许显示non-editable字段
    list_filter = ['level']  # 列表筛选也允许用level
    search_fields = ['name']
    fieldsets = (
        # 移除fieldsets中的level字段（因为editable=False）
        ('基础信息', {'fields': ('name', 'parent')}),
        ('时间信息', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'updated_at']  # level不在其中（mptt自动维护，无需手动只读）
    mptt_level_indent = 20

    # 自定义只读字段，展示level值
    def show_level(self, obj):
        return obj.level  # 调用mptt自动生成的level字段
    show_level.short_description = '层级'  # 自定义显示名称


# 客户单位：应用带data-parent的树形下拉框
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'admin_div', 'created_at']
    list_filter = ['admin_div__level', 'admin_div__parent']
    search_fields = ['name', 'admin_div__name']
    fieldsets = (
        ('客户信息', {'fields': ('name', 'admin_div')}),
        ('时间信息', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'updated_at']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'admin_div':
            # 1. 指定自定义Widget（添加data-parent）
            kwargs['widget'] = AdminDivTreeSelect()

            # 2. 按树形排序，下拉框显示带缩进的名称
            kwargs['queryset'] = AdminDiv.objects.all().order_by('tree_id', 'lft')

            # 3. 自定义选项文本（带层级缩进符）
            kwargs['label_from_instance'] = lambda obj: f"{'—' * obj.level} {obj.name}"

        return super().formfield_for_foreignkey(db_field, request, **kwargs)