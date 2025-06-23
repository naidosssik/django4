from django.contrib import admin
from .models import Role, User, Nomination, Nominee, Vote, Jury, JuryEvaluation
from django.db.models import Count
from django.utils.html import format_html
from django.utils import timezone

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'get_role_name')
    list_filter = ('role',)
    search_fields = ('email', 'name', 'surname')

    # Используем raw_id_fields для связи с Role
    raw_id_fields = ('role',)

    @admin.display(description='Роль')
    def get_role_name(self, obj):
        return obj.role.name if obj.role else '-'

@admin.action(description='Завершить выбранные номинации')
def close_nominations(modeladmin, request, queryset):
    queryset.update(end_date=timezone.now())

@admin.action(description='Сделать выбранные номинации активными')
def reopen_nominations(modeladmin, request, queryset):
    queryset.update(end_date=None)

@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_currently_active', 'created_date', 'end_date', 'nominees_count')
    list_filter = ('created_date', 'name')
    search_fields = ('name',)
    readonly_fields = ('created_date',)
    date_hierarchy = 'end_date'
    ordering = ('-created_date',)
    actions = [close_nominations, reopen_nominations]

    def nominees_count(self, obj):
        return obj.nominees.count()
    nominees_count.short_description = 'Число номинантов'
    
    def is_currently_active(self, obj):
        return obj.end_date is None or obj.end_date > timezone.now()
    is_currently_active.short_description = 'Активна сейчас'
    

@admin.register(Nominee)
class NomineeAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'user', 'nomination', 'contact', 'created_at')
    list_filter = ('nomination', 'created_at')
    search_fields = ('project_name', 'user__username', 'contact')
    raw_id_fields = ('user', 'nomination')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'nominee', 'choice_display', 'voted_at')
    list_filter = ('choice', 'voted_at', 'nominee__nomination')
    search_fields = ('user__username', 'nominee__project_name')
    raw_id_fields = ('user', 'nominee')
    date_hierarchy = 'voted_at'
    ordering = ('-voted_at',)

    def choice_display(self, obj):
        return obj.get_choice_display()
    choice_display.short_description = 'Выбор'

@admin.register(Jury)
class JuryAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo_tag')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)

    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.photo.url)
        return "-"
    photo_tag.short_description = 'Фото'

class JuryEvaluationInline(admin.TabularInline):
    model = JuryEvaluation
    extra = 0
    raw_id_fields = ('nominee',)

@admin.register(JuryEvaluation)
class JuryEvaluationAdmin(admin.ModelAdmin):
    list_display = ('jury', 'nominee', 'score', 'evaluated_at')
    list_filter = ('score', 'evaluated_at', 'jury')
    search_fields = ('jury__user__username', 'nominee__project_name')
    raw_id_fields = ('jury', 'nominee')
    date_hierarchy = 'evaluated_at'
    ordering = ('-evaluated_at',)

from .models import NKexam

@admin.register(NKexam)
class NKexamAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam_date', 'is_public', 'created_at', 'exam_task')
    search_fields = ('name', 'email')
    list_filter = ('is_public', 'created_at')
    filter_horizontal = ('users',)
    date_hierarchy = 'exam_date'

