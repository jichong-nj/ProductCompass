from django.db import models


# 厂商模型
class Vendor(models.Model):
    name = models.CharField(verbose_name='厂商名称', max_length=100)
    remark = models.TextField(verbose_name='备注', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '厂商'
        verbose_name_plural = '厂商'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# 产品模型
class Product(models.Model):
    # 产品类型枚举
    PRODUCT_TYPE_CHOICES = [
        ('PLATFORM_SOFTWARE', '平台软件'),
        ('PC_TERMINAL_SOFTWARE', 'PC终端软件'),
        ('HARDWARE', '硬件'),
        ('STANDALONE_SOFTWARE', '单机板软件'),
        ('MOBILE_APP', '移动APP'),
    ]

    product_name = models.CharField(verbose_name='产品名称', max_length=100)
    product_type = models.CharField(
        verbose_name='产品类型',
        max_length=30,
        choices=PRODUCT_TYPE_CHOICES
    )

    product_description = models.TextField(
        verbose_name='产品说明',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '产品'
        verbose_name_plural = '产品'
        ordering = ['-created_at']

    def __str__(self):
        return self.product_name


# 产品组件模型
class ProductComponent(models.Model):
    # 组件类型枚举
    COMPONENT_TYPE_CHOICES = [
        ('SOFTWARE_MODULE', '软件模块'),
        ('HARDWARE', '硬件'),
    ]

    product = models.ForeignKey(
        Product,
        verbose_name='所属产品',
        on_delete=models.CASCADE,
        related_name='components'
    )
    component_name = models.CharField(verbose_name='组件名称', max_length=100)
    component_type = models.CharField(
        verbose_name='组件类型',
        max_length=20,
        choices=COMPONENT_TYPE_CHOICES
    )
    component_description = models.TextField(
        verbose_name='组件说明',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '产品组件'
        verbose_name_plural = '产品组件'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.product_name} - {self.component_name}'


# 产品型号模型
class ProductModel(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='产品',
        on_delete=models.CASCADE,
        related_name='models'
    )
    model_name = models.CharField(verbose_name='型号', max_length=100)
    remark = models.TextField(verbose_name='备注', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '产品型号'
        verbose_name_plural = '产品型号'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.product_name} - {self.model_name}'