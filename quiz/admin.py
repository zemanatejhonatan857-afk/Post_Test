from django.contrib import admin

from .models import Participante, Respuesta


class RespuestaInline(admin.TabularInline):

    model = Respuesta

    extra = 0

    readonly_fields = (
        'pregunta',
        'respuesta_usuario',
        'texto_respuesta',
        'respuesta_correcta',
        'correcta'
    )


@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):

    list_display = (
        'nombre',
        'identificacion',
        'cargo',
        'puntaje',
        'finalizado',
        'fecha'
    )

    search_fields = (
        'nombre',
        'identificacion',
        'cargo'
    )

    inlines = [RespuestaInline]


admin.site.register(Respuesta)
# Register your models here.
