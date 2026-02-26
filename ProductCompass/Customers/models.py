from django.db import models
from mptt.models import MPTTModel, TreeForeignKey  # 必须导入MPTTModel和TreeForeignKey

class AdminDiv(MPTTModel):  # 继承MPTTModel，而非普通models.Model
    name = models.CharField('行政区划名称', max_length=100, unique=True)
    # 父级关联：必须用TreeForeignKey，且on_delete设为CASCADE/SET_NULL
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='父级行政区划'
    )
    level = models.IntegerField('层级', default=0, editable=False)  # 可选（mptt会自动维护）
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    # 关键：指定mptt的父级字段（必须配置）
    class MPTTMeta:
        order_insertion_by = ['name']  # 按名称排序子节点
        parent_attr = 'parent'  # 显式指定父级字段（默认就是parent，可省略，但建议显式写）

    class Meta:
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        # return self.name

        ancestors = self.get_ancestors(include_self=True)  # 获取所有祖先（包含自身）
        # 拼接路径，用/分隔
        return '/'.join([ancestor.name for ancestor in ancestors])


class Customer(models.Model):
    """客户单位模型"""
    name = models.CharField(max_length=200, verbose_name='客户单位名称')
    admin_div = models.ForeignKey(
        AdminDiv,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name='customers',
        verbose_name='所属行政区划'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '客户单位'
        verbose_name_plural = '客户单位'
        ordering = ['name']
        unique_together = ['name', 'admin_div']  # 同一区划下客户名称唯一

    def __str__(self):
        return f'{self.name}（{self.admin_div}）'
