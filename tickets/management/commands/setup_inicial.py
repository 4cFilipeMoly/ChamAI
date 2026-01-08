from django.core.management.base import BaseCommand
from tickets.models import Setor, Subsetor, Colaborador

class Command(BaseCommand):
    help = 'Popula a hierarquia de Setores e Subsetores e define Heads'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- INICIANDO SETUP ---")

        # 1. HIERARQUIA
        hierarquia = {
            "Comercial": [],
            "4Cia": ["Comunicai", "CX (Customer Experience)", "CS (Costumer Service)"],
            "Recuperai": ["Arena Atena", "Arena Héstia", "Arena Hermes", "Arena Zeus", "Arena Apolo"],
            "Qualidade (VigIA)": ["Treinamento & Desenvolvimento", "Monitoria"],
            "Financeiro": ["Contas a Pagar", "Contas a Receber", "Controladoria", "Contabilidade", "Departamento Pessoal"],
            "GenteGestão": [],
            "Juridico": ["Compliance"],
            "Marketing": [],
            "T.I": ["BI & Analytics", "Desenvolvimento", "Infraestrutura e segurança", "Integrações e Homologações", "Monitoramento e Performance", "ControlDesk"]
        }

        id_counter = 100
        
        for nome_setor, sub_lista in hierarquia.items():
            setor_obj, created = Setor.objects.get_or_create(
                nome=nome_setor,
                defaults={'id_setor': id_counter}
            )
            if created:
                id_counter += 10
                self.stdout.write(self.style.SUCCESS(f"[CRIADO] Setor: {nome_setor}"))
            
            # Garante subsetor Geral
            if not sub_lista:
                sub_lista = ["Geral"]

            for nome_sub in sub_lista:
                sub_obj, sub_created = Subsetor.objects.get_or_create(
                    nome=nome_sub,
                    setor_pai=setor_obj
                )
                if sub_created:
                    self.stdout.write(f"   -> [NOVO] Subsetor: {nome_sub}")

        # 2. DEFINIR HEADS
        emails_heads = [
            "danilo.bezerra@4cdigital.com.br",
            "dayvid.borges@4cdigital.com.br",
            "filipe.molinari@4cdigital.com.br", 
        ]

        self.stdout.write("\n--- ATUALIZANDO HEADS ---")
        for email in emails_heads:
            try:
                colab = Colaborador.objects.get(user__email=email)
                colab.is_manager = True
                colab.save()
                self.stdout.write(self.style.SUCCESS(f"[OK] {colab.nome} é HEAD."))
            except Colaborador.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"[AVISO] {email} ainda não se cadastrou no sistema."))

        self.stdout.write(self.style.SUCCESS("\n--- PROCESSO CONCLUÍDO ---"))