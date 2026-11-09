from django.db import models

class Participante(models.Model):

    nombre = models.CharField(max_length=150)

    identificacion = models.CharField(
        max_length=40,
        db_index=True
    )

    cargo = models.CharField(max_length=120)

    puntaje = models.IntegerField(default=0)

    finalizado = models.BooleanField(default=False)

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Respuesta(models.Model):

    participante = models.ForeignKey(
        Participante,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )

    numero_pregunta = models.IntegerField()

    pregunta = models.TextField()

    respuesta_usuario = models.CharField(max_length=1)

    texto_respuesta = models.TextField()

    respuesta_correcta = models.CharField(max_length=1)

    correcta = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.participante.nombre} - Pregunta {self.numero_pregunta}'
# Create your models here.
