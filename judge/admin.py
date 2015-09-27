from django.contrib import admin

from judge.models import *

class TestInLine(admin.TabularInline):
	model = Test
	extra = 3

class ProblemAdmin(admin.ModelAdmin):
	fieldsets = [
		('Title', {'fields': ['title',]}),
		(None, {'fields': ['statement', 'customChecker'], 
                    'classes': ['wide',]}),]

	inlines = [TestInLine]
	search_fields = ['title']

admin.site.register(Problem, ProblemAdmin)
admin.site.register(Solution)
admin.site.register(Test)
admin.site.register(TestResult)
admin.site.register(UserProblemData)
admin.site.register(UserStatts)
