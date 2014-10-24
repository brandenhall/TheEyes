from django.contrib import admin

from .models import (
    Creature,
    CreatureQuestion,
    CreatureQuestionResponse,
    UserCreatedCreature,
    HeroAnimation,
    Interaction,
)


class CreatureQuestionResponseInline(admin.TabularInline):
    model = CreatureQuestionResponse
    min_num = 2
    max_num = 2


class HeroAnimationAdmin(admin.ModelAdmin):
    model = HeroAnimation
    list_display = ('name',)


class InteractionAdmin(admin.ModelAdmin):
    model = Interaction
    list_display = ('timestamp', 'response')


class UserCreatedCreatureAdmin(admin.ModelAdmin):
    model = UserCreatedCreature
    list_display = ('timestamp',)


class CreatureAdmin(admin.ModelAdmin):
    model = Creature
    list_display = ('name',)


class CreatureQuestionAdmin(admin.ModelAdmin):
    model = CreatureQuestion
    inlines = [CreatureQuestionResponseInline]
    list_display = ('creature', 'question')

admin.site.register(Creature, CreatureAdmin)
admin.site.register(CreatureQuestion, CreatureQuestionAdmin)
admin.site.register(UserCreatedCreature, UserCreatedCreatureAdmin)
admin.site.register(HeroAnimation, HeroAnimationAdmin)
admin.site.register(Interaction, InteractionAdmin)
