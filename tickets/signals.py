from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Colaborador

@receiver(post_save, sender=Colaborador)
def criar_user_django(sender, instance, created, **kwargs):
    """
    Quando um Colaborador é criado (importado ou cadastro manual),
    cria um User do Django para ele poder logar.
    """
    if created and not instance.user:
        # Cria usuário com o email como username (ou parte dele)
        username = instance.email.split('@')[0]
        # Garante username único
        if User.objects.filter(username=username).exists():
            username = f"{username}_{str(instance.id)[:4]}"
            
        user = User.objects.create_user(
            username=username,
            email=instance.email,
            password='mudar123',  # Senha padrão inicial
            first_name=instance.nome.split()[0]
        )
        instance.user = user
        instance.save()