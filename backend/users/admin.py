from django.contrib import admin

from .models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'username')
    list_display = ('email', 'username', 'followers_count', 
                    # 'recipes_count'
                    )
    readonly_fields = ('followers_count',
                        # 'recipes_count'
                        )

    def followers_count(self, obj):
        return Follow.objects.filter(following=obj).count()

    # def recipes_count(self, obj):
    #     return obj.recipes.count()

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')
    list_display_links = ('id', 'user', 'following')

admin.site.register(User, UserAdmin)