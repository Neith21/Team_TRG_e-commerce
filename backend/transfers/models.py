from django.conf import settings
from django.db import models
from branch.models import Branch
from product.models import Product
from vehicle.models import Vehicle
from django.core.exceptions import ValidationError

class Transfer(models.Model):
    STATUS_CHOICES = (
        ('picking', 'En Preparación (Picking)'),
        ('transit', 'En Tránsito'),
        ('received', 'Recibida Completa'),
    )

    code = models.CharField(max_length=100, unique=True, editable=False, verbose_name="código")
    date = models.DateTimeField(verbose_name="fecha de traslado")
    
    source_branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='transfers_sent', verbose_name="origen")
    dest_branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='transfers_received', verbose_name="destino")
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, verbose_name="vehículo")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='picking', verbose_name="estado")
    
    # Auditoría
    active = models.BooleanField(default=True, verbose_name="activo")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+', verbose_name="creado por")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+', verbose_name="modificado por")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} ({self.source_branch} -> {self.dest_branch})"
    
    def clean(self):
        if not self.pk and self.status == 'transit':
            raise ValidationError({
                'status': "Una nueva transferencia debe iniciarse en estado 'Picking'. No se puede crear directamente en 'Tránsito'."
            })

        if self.source_branch == self.dest_branch:
            raise ValidationError({
                'dest_branch': "La sucursal de destino no puede ser la misma que la de origen."
            })
        
        if self.status in ['picking', 'transit'] and self.vehicle:    
            busy_transfer = Transfer.objects.filter(
                vehicle=self.vehicle,
                status__in=['picking', 'transit']
            )

            if self.pk:
                busy_transfer = busy_transfer.exclude(pk=self.pk)

            if busy_transfer.exists():
                conflict_code = busy_transfer.first().code
                raise ValidationError({
                    'vehicle': f"El vehículo '{self.vehicle}' ya está ocupado en la transferencia {conflict_code}."
                })

        if self.pk:
            old_status = Transfer.objects.filter(pk=self.pk).values_list('status', flat=True).first()
            if old_status:
                if old_status == 'transit':
                    if self.status == 'picking':
                        raise ValidationError({
                            'status': "No se puede revertir una transferencia 'En Tránsito' a 'Picking'."
                        })
                elif old_status == 'received':
                    if self.status != 'received':
                        raise ValidationError({
                            'status': "Una transferencia finalizada (Recibida) no se puede modificar ni cambiar de estado."
                        })

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.status not in ['picking', 'transit']:
                self.status = 'picking'
                
            super().save(*args, **kwargs)
            # Generar código: TRF-20251124-0001
            date_str = self.date.strftime('%Y%m%d')
            self.code = f"TRF-{date_str}-{self.pk:04d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Transferencia"
        verbose_name_plural = "Transferencias"
        ordering = ['-date']


class TransferDetail(models.Model):
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="producto")
    
    required_quantity = models.PositiveIntegerField(verbose_name="cantidad solicitada")
    sent_quantity = models.PositiveIntegerField(default=0, verbose_name="cantidad enviada")
    received_quantity = models.PositiveIntegerField(default=0, verbose_name="cantidad recibida")
    
    comment = models.CharField(max_length=200, blank=True, null=True, verbose_name="comentario")

    # Auditoría
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} ({self.sent_quantity})"