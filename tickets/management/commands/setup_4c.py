from django.core.management.base import BaseCommand
from tickets.models import Setor, CategoriaConfig

class Command(BaseCommand):
    help = 'Configura os Setores e Categorias da 4C Digital baseados no CSV e Python fornecidos'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando importação de dados 4C Digital...")

        # --- 1. SETORES (Baseado no arquivo data-2026...csv) ---
        # Formato: (ID, Nome, Email)
        # Nota: Para setores com múltiplos emails no CSV, pegamos o primeiro para evitar erros.
        setores_data = [
            (1, "Comercial", "comunicacao.comercial@4cdigital.com.br"),
            (2, "4Cia", "comunicacaodigital@4cdigital.com.br"),
            (3, "Recuperai", "comunicacaosupervisores@4cdigital.com.br"),
            (4, "T.I", "comunicacao.tecnologia@4cdigital.com.br"),
            (5, "Marketing", "marketing@4cdigital.com.br"),
            (6, "Qualidade (VigIA)", "comunicacaovigia@4cdigital.com.br"),
            (7, "Financeiro", "comunicacao.financeiro@4cdigital.com.br"),
            (8, "GenteGestão", "comunicacao.genteegestao@4cdigital.com.br"),
            (9, "Controladoria", "comunicacao.controladoria@4cdigital.com.br"),
            (10, "BI & Analytics", "comunicacao.mis@4cdigital.com.br"),
            (11, "CX (Customer Experience)", "hellen.medeiros@4cdigital.com.br"),
            (13, "Contabilidade", "lucas.diano@4cdigital.com.br"),
            (14, "Comunicai", "comunicacao.comunicai@4cdigital.com.br"),
            (15, "Teste / Admin", "filipe.molinari@4cdigital.com.br"),
            (16, "Compliance", "larissa.freire@4cdigital.com.br"),
            
            # Setor Extra (Mapeado manualmente pois existe nas Categorias mas não no CSV principal com ID próprio)
            # Usando ID 17 para evitar conflito e o mesmo email de GenteGestão como fallback
            (17, "Departamento Pessoal", "comunicacao.genteegestao@4cdigital.com.br"),
        ]

        for id_set, nome, email in setores_data:
            Setor.objects.update_or_create(
                id_setor=id_set,
                defaults={'nome': nome, 'email_setor': email}
            )
            self.stdout.write(f"Setor processado: {nome}")

        # --- 2. CATEGORIAS (Baseado no arquivo abrir_chamados.py) ---
        # Mapeia o Nome do Setor no Dicionário -> ID do Setor no Banco
        mapa_setores = {
            "Departamento Pessoal": 17, # Criado manualmente acima
            "Marketing": 5,
            "Qualidade (VigIA)": 6,
            "Financeiro": 7,
            "BI & Analytics": 10,
            "CX (Customer Experience)": 11,
            "Gente&Gestão": 8, # Nota: No CSV é "GenteGestão", no Python é "Gente&Gestão"
            "Controladoria": 9,
            "4Cia": 2,
            "T.I": 4,
            "Recuperai": 3,
            "Comercial": 1
        }

        # Dicionário completo de categorias
        categorias_por_setor = {
            "Departamento Pessoal": [
                "Vale-transporte",
                "Inclusão/exclusão de dependentes no plano de saúde",
                "Dúvidas sobre benefícios",
                "Esclarecimento sobre folha",
                "Adiantamento salarial",
                "Conferência de pagamento de horas extras",
                "Agendamento de férias",
                "Atestados e declarações médicas",
                "Dúvidas sobre abonos e afastamentos",
                "Atualização cadastral",
                "Declaração de vínculo empregatício",
                "Ajuste de ponto",
                "Banco de horas",
                "Alteração de horário de trabalho",
                "Dúvidas sobre contrato",
                "Desligamento",
                "Verbas rescisórias",
                "Outros"
            ],
            "Marketing": [
                "Banner RCS ou HTML",
                "Botões para HTML",
                "Artes de comunicado",
                "Apresentações",
                "Documentos",
                "Ícones de grupo no WhatsApp",
                "4C News para Fechamento & 4Ci Web",
                "Outros"
            ],
            "Qualidade (VigIA)": [
                "Análise de ligação",
                "Treinamento para reciclagem",
                "Solicitações de treinamento",
                "Treinamentos para novos colaboradores",
                "Cronograma Promove",
                "Outros"
            ],
            "Financeiro": [
                "Emissão e envio de boletos, relatórios de evidências e notas fiscais",
                "Comprovantes de pagamento",
                "Conferência e assinatura de BM's",
                "Participação em eventos no Ariba",
                "Compras",
                "Reembolsos",
                "Dúvidas sobre pagamentos e cobranças",
                "Uso dos cartões e dinheiro do caixinha",
                "Outros"
            ],
            "BI & Analytics": [
                "Relatórios e fechamentos",
                "Manutenção e ajustes em sistemas",
                "Processos e automações",
                "Gestão e prioridades",
                "Outros"
            ],
            "CX (Customer Experience)": [
                "Alteração de jornada",
                "Solicitação de extra",
                "Desenvolvimento de jornada",
                "Jornada em Excel",
                "Alteração de cadastro",
                "HTML",
                "Outros"
            ],
            "Gente&Gestão": [
                "Solicitação de cursos e livros",
                "Plano de saúde",
                "Wellhub/Gympass",
                "Uniformes e garrafas",
                "Contato do SPA da Estácio",
                "Processo seletivo de estagiários (Externas -Supervisores) (Internas-Heads)",
                "Acompanhamento para feedbacks",
                "Processos de desligamento",
                "Liberação de funcionários",
                "Viagens de Uber para mal-estar",
                "Outros"
            ],
            "Controladoria": [
                "Informação Contratual",
                "Dúvidas Relacionadas a Serviços Extras",
                "Envio de Documentos Contratuais",
                "Outros"
            ],
            "4Cia": [
                "Atualização de desktop",
                "Atualização de minmax",
                "Atualização de trigger e behavior",
                "Homologação",
                "Outros"
            ],
            "T.I": [
                "Desenvolvimento",
                "Implantação de Jornadas",
                "Atualização de Jornadas",
                "Relatórios",
                "Permissões de acesso",
                "Infraestrutura",
                "Outros"
            ],
            "Recuperai": [
                "Troca de FourcCoin",
                "Troca de turno",
                "Solicitação de folgas",
                "Registro de dobras",
                "Outros"
            ],
            "Comercial": [
                "Prospecção",
                "Outros"
            ]
        }

        count = 0
        for nome_setor_key, lista_categorias in categorias_por_setor.items():
            id_setor = mapa_setores.get(nome_setor_key)
            if id_setor:
                try:
                    setor_obj = Setor.objects.get(id_setor=id_setor)
                    for cat_nome in lista_categorias:
                        CategoriaConfig.objects.get_or_create(
                            nome=cat_nome,
                            setor_dono=setor_obj
                        )
                        count += 1
                except Setor.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Setor ID {id_setor} não encontrado para {nome_setor_key}"))
            else:
                self.stdout.write(self.style.WARNING(f"Setor '{nome_setor_key}' não mapeado para ID"))

        self.stdout.write(self.style.SUCCESS(f"Importação concluída! {count} categorias configuradas."))