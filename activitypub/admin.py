from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Account, Note

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_image', 'feed')
    exclude = ('private_key', 'public_key')

    def icon_image(self, row):
        return mark_safe('<img src="/media/{}" style="width:100px;height:auto;">'.format(row.icon)) if row.icon else 'no image'

    def feed(self, row):
        return mark_safe('<a href="{}" target="_blank">{}</a>'.format(row.feed_url, row.feed_url)) if row.feed_url else 'no feed url'

    def get_actions(self, request):
        actions = super(AccountAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_model(self, request, obj):
        if isinstance(obj, list):
            for o in obj.all():
                o.delete()
        else:
           obj.delete()

    actions = [delete_model]
    delete_model.short_description = 'delete selected'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('account', 'content', 'link')

    def link(self, row):
        return mark_safe('<a href="{}" target="_blank">{}</a>'.format(row.url, row.url)) if row.url else 'no url'
