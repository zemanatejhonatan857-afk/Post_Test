
import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from .models import Participante, Respuesta
from .questions import PREGUNTAS


# ==========================================
# VERIFICACIÓN DE ADMINISTRADOR
# ==========================================

def es_administrador(user):
    return user.is_authenticated and user.is_staff


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

def inicio(request):
    return render(request, 'quiz/inicio.html')


# ==========================================
# JUEGO DE PREGUNTAS
# ==========================================

def jugar(request):

    total_preguntas = len(PREGUNTAS)

    # PROCESAR FORMULARIOS POST

    if request.method == 'POST':

        # REGISTRO DEL PARTICIPANTE

        if request.POST.get('registro') == 'si':

            nombre = request.POST.get('nombre', '').strip()
            identificacion = request.POST.get('identificacion', '').strip()
            cargo = request.POST.get('cargo', '').strip()

            if not nombre or not identificacion or not cargo:
                return redirect('inicio')

            participante = Participante.objects.create(
                nombre=nombre,
                identificacion=identificacion,
                cargo=cargo
            )

            request.session['participante_id'] = participante.id
            request.session['pregunta_actual'] = 0

            return redirect('jugar')

        # VALIDAR PARTICIPANTE

        participante_id = request.session.get('participante_id')

        if not participante_id:
            return redirect('inicio')

        participante = get_object_or_404(
            Participante,
            id=participante_id,
            finalizado=False
        )

        indice = request.session.get('pregunta_actual', 0)

        if indice >= total_preguntas:
            return redirect('inicio')

        pregunta = PREGUNTAS[indice]

        seleccion = request.POST.get('respuesta')

        # VALIDAR RESPUESTA

        if seleccion not in pregunta['opciones']:

            pregunta_publica = {
                'pregunta': pregunta['pregunta'],
                'opciones': pregunta['opciones']
            }

            return render(request, 'quiz/pregunta.html', {
                'pregunta': pregunta_publica,
                'numero': indice + 1,
                'total': total_preguntas,
                'progreso': int(indice / total_preguntas * 100),
                'error': 'Debes seleccionar una respuesta.'
            })

        # COMPROBAR RESPUESTA CORRECTA

        correcta = seleccion == pregunta['correcta']

        # GUARDAR RESPUESTA

        Respuesta.objects.update_or_create(
            participante=participante,
            numero_pregunta=indice + 1,
            defaults={
                'pregunta': pregunta['pregunta'],
                'respuesta_usuario': seleccion,
                'texto_respuesta': pregunta['opciones'][seleccion],
                'respuesta_correcta': pregunta['correcta'],
                'correcta': correcta
            }
        )

        # AVANZAR PREGUNTA

        indice += 1

        request.session['pregunta_actual'] = indice

        # FINALIZAR JUEGO

        if indice >= total_preguntas:

            participante.puntaje = participante.respuestas.filter(
                correcta=True
            ).count()

            participante.finalizado = True
            participante.save()

            request.session.pop('participante_id', None)
            request.session.pop('pregunta_actual', None)

            return redirect(
                'resultado',
                participante_id=participante.id
            )

        return redirect('jugar')

    # MOSTRAR PREGUNTA

    participante_id = request.session.get('participante_id')

    if not participante_id:
        return redirect('inicio')

    participante = get_object_or_404(
        Participante,
        id=participante_id,
        finalizado=False
    )

    indice = request.session.get('pregunta_actual', 0)

    if indice >= total_preguntas:
        return redirect('inicio')

    pregunta = PREGUNTAS[indice]

    # No enviar la respuesta correcta al navegador

    pregunta_publica = {
        'pregunta': pregunta['pregunta'],
        'opciones': pregunta['opciones']
    }

    return render(request, 'quiz/pregunta.html', {
        'pregunta': pregunta_publica,
        'numero': indice + 1,
        'total': total_preguntas,
        'progreso': int(indice / total_preguntas * 100)
    })


# ==========================================
# RESULTADOS DEL JUEGO
# ==========================================

def resultado(request, participante_id):

    participante = get_object_or_404(
        Participante,
        id=participante_id,
        finalizado=True
    )

    return render(request, 'quiz/resultado.html', {
        'participante': participante
    })


# ==========================================
# INICIO DE SESIÓN ADMINISTRADOR
# ==========================================

def administrador_login(request):

    if request.method == 'POST':

        usuario = request.POST.get('usuario')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=usuario,
            password=password
        )

        if user and user.is_staff:

            login(request, user)

            return redirect('panel')

        return render(request, 'quiz/login.html', {
            'error': 'Usuario o contraseña incorrectos.'
        })

    return render(request, 'quiz/login.html')


# ==========================================
# CERRAR SESIÓN ADMINISTRADOR
# ==========================================

@login_required
@user_passes_test(es_administrador)
def administrador_logout(request):

    logout(request)

    return redirect('administrador_login')


# ==========================================
# PANEL ADMINISTRATIVO
# ==========================================

@login_required
@user_passes_test(es_administrador)
def panel(request):

    participantes = Participante.objects.all().order_by('-id')

    finalizados = participantes.filter(finalizado=True)

    total = participantes.count()

    cantidad_finalizados = finalizados.count()

    promedio = (
        sum(p.puntaje for p in finalizados) / cantidad_finalizados
        if cantidad_finalizados else 0
    )

    return render(request, 'quiz/panel.html', {
        'participantes': participantes,
        'total': total,
        'finalizados': cantidad_finalizados,
        'promedio': round(promedio, 1)
    })


# ==========================================
# DETALLE DE PARTICIPANTE
# ==========================================

@login_required
@user_passes_test(es_administrador)
def detalle(request, participante_id):

    participante = get_object_or_404(
        Participante,
        id=participante_id
    )

    respuestas = participante.respuestas.all().order_by(
        'numero_pregunta'
    )

    for r in respuestas:

        indice = r.numero_pregunta - 1

        if 0 <= indice < len(PREGUNTAS):

            opciones = PREGUNTAS[indice]['opciones']

            r.texto_respuesta_correcta = opciones.get(
                r.respuesta_correcta,
                'No disponible'
            )

        else:

            r.texto_respuesta_correcta = 'No disponible'

    return render(request, 'quiz/detalle.html', {
        'participante': participante,
        'respuestas': respuestas
    })


# ==========================================
# EXPORTAR RESULTADOS CSV
# ==========================================

@login_required
@user_passes_test(es_administrador)
def exportar(request):

    respuesta = HttpResponse(
        content_type='text/csv; charset=utf-8'
    )

    respuesta['Content-Disposition'] = (
        'attachment; filename="resultados_guardianes_del_macizo.csv"'
    )

    # Compatibilidad con Excel para caracteres especiales

    respuesta.write('\ufeff')

    escritor = csv.writer(respuesta, delimiter=';')

    escritor.writerow([
        'Nombre',
        'Identificación',
        'Cargo',
        'Calificacion',
    ])

# LISTA DE PARTICIPANTES
    participantes = Participante.objects.all().order_by('-id')

    for participante in participantes:

        calificacion = (
            f'{participante.puntaje}/{len(PREGUNTAS)}'
            if participante.finalizado
            else 'En curso'
        )

        escritor.writerow([
            participante.nombre,
            participante.identificacion,
            participante.cargo,
            calificacion
        ])


    return respuesta


# ==========================================
# ELIMINAR PARTICIPANTE
# ==========================================

@login_required
@user_passes_test(es_administrador)
@require_POST
def eliminar_participante(request, participante_id):

    participante = get_object_or_404(
        Participante,
        id=participante_id
    )

    participante.delete()

    return redirect('panel')
