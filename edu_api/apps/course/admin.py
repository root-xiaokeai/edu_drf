from django.contrib import admin
# Register your models here.
from course import models
admin.site.register(models.CourseCategory)
admin.site.register(models.Course)
admin.site.register(models.Teacher)
admin.site.register(models.CourseChapter)
admin.site.register(models.CourseLesson)
admin.site.register(models.CourseDiscountType)
admin.site.register(models.CourseDiscount)
admin.site.register(models.Activity)
admin.site.register(models.CoursePriceDiscount)
admin.site.register(models.CourseExpire)


