from django.contrib import admin
from django.contrib.auth.models import Permission

from judge.models import *

class TestInLine(admin.TabularInline):
	model = Test
	extra = 3

class ProblemAdmin(admin.ModelAdmin):
	fieldsets = [
		('Title', {'fields': ['title',]}),
		(None, {'fields': ['statement', 'custom_checker', 'max_score'], 
                    'classes': ['wide',]}),]

	inlines = [TestInLine]
	search_fields = ['title']

admin.site.register(Problem, ProblemAdmin)
admin.site.register(Solution)
admin.site.register(Test)
admin.site.register(TestResult)
admin.site.register(TestGroup)
admin.site.register(TestGroupResult)
admin.site.register(UserProblemData)
admin.site.register(UserStatts)

admin.site.register(Permission)
