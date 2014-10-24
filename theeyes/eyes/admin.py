from django.contrib import admin
from grappelli.forms import GrappelliSortableHiddenMixin

from .models import (
    Eye,
    EyeRelationship
)


class EyeRelationshipInline(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = EyeRelationship
    fk_name = 'eye'
    extra = 0
    fields = ('relative', 'position')
    sortable_field_name = 'position'


class EyeAdmin(admin.ModelAdmin):
    model = Eye
    inlines = [EyeRelationshipInline]
    list_display = ('number', 'Preference')

    def Preference(self, obj):
        result = []
        for preference in obj.preferences.all():
            result.append(str(preference.relative.number))

        return ', '.join(result)


admin.site.register(Eye, EyeAdmin)
