from django.core.management.base import BaseCommand
from tickets.models import Setor, Subsetor, CategoriaConfig

class Command(BaseCommand):
    help = 'Popula o banco de dados com a lista oficial e atualizada de Categorias e SLAs'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- INICIANDO CARGA DE CATEGORIAS ---")

        # Estrutura de Dados Limpa e Organizada
        # Formato: "Setor": { "Subsetor": [ ("Categoria", SLA), ... ] }
        dados = {
            "4Cia": {
                "CS (Costumer Service)": [
                    ("Dúvida Contratual", 24),
                    ("Onboarding de Cliente", 24),
                    ("Renovação de Contrato", 24),
                ],
                "CX (Customer Experience)": [
                    ("Alteração de cadastro", 24),
                    ("Alteração de jornada", 24),
                    ("Análise de NPS", 24),
                    ("Desenvolvimento de jornada", 24),
                    ("Feedback de Cliente", 24),
                    ("HTML", 24),
                    ("Jornada em Excel", 24),
                    ("Plano de Ação de Satisfação", 24),
                    ("Solicitação de extra", 24),
                ],
                "ComunicAI": [
                    ("Acionamento - Demais Empresas", 24),
                    ("Acionamento - Recuperai", 24),
                    ("Solicitação de Enriquecimento em lote", 24),
                    ("Solicitação de acesso à plataforma de SMS(White Label)", 24),
                    ("Criação de Artes", 24),
                    ("Disparo de E-mail Marketing", 24),
                    ("Gestão de Redes Sociais", 24),
                ],
                "Geral": [
                    ("Atualização de desktop", 24),
                    ("Atualização de minmax", 24),
                    ("Atualização de trigger e behavior", 24),
                    ("Homologação", 24),
                ]
            },
            "Financeiro": {
                "Contabilidade": [
                    ("Balanço", 24),
                    ("Certidões negativas / regularização fiscal", 24),
                    ("Contabilidade", 24),
                    ("Dúvidas Fiscais", 24),
                    ("Dúvidas sobre encargos / tributos", 24),
                    ("Envio de declarações", 24),
                    ("Impostos", 24),
                ],
                "Contas a Pagar": [
                    ("Aprovação de Despesa", 24),
                    ("Atualização de dados bancários", 24),
                    ("Comprovante de pagamento", 24),
                    ("Contabilidade", 24),
                    ("Controladoria", 24),
                    ("Departamento Pessoal", 24),
                    ("Pagamento de Fornecedor", 24),
                    ("Reagendamento de vencimento", 24),
                    ("Reembolso", 24),
                    ("Solicitação de pagamento", 24),
                    ("Solicitação de reembolsos", 24),
                ],
                "Contas a Receber": [
                    ("Ajuste em valores contratados", 24),
                    ("Atualização de cadastro de cliente", 24),
                    ("Baixa de Boleto", 24),
                    ("Confirmação de pagamento", 24),
                    ("Dúvida sobre boleto ou fatura", 24),
                    ("Emissão de Nota Fiscal", 24),
                    ("Negociação de Dívida", 24),
                    ("Negociação de prazos", 24),
                    ("Solicitação de nota fiscal", 24),
                ],
                "Controladoria": [
                    ("Análise de desvios orçamentários", 24),
                    ("Auditoria Interna", 24),
                    ("Controladoria", 24),
                    ("Dúvida sobre KPI / DASH", 24),
                    ("Dúvidas Relacionadas a Serviços Extras", 24),
                    ("Envio de Documentos Contratuais", 24),
                    ("Inclusão, ajuste ou aprovação de despesas no orçamento", 24),
                    ("Informação Contratual", 24),
                    ("Orçamento (Budget)", 24),
                    ("Orçamento: Inclusão, ajuste ou aprovação de despesas", 24),
                    ("Outros", 24),
                    ("Precificações", 24),
                    ("Relatório Gerencial", 24),
                    ("Solicitação de centro de custo ou reclassificação de despesas", 24),
                    ("Solicitação de relatório financeiro", 24),
                    ("Solicitação de relatórios financeiros e gerenciais", 24),
                ],
                "Departamento Pessoal": [
                    ("Adiantamento salarial", 24),
                    ("Admissão/Demissão", 24),
                    ("Agendamento de férias", 24),
                    ("Ajuste de ponto", 24),
                    ("Alteração de horário de trabalho", 24),
                    ("Atestados e declarações médicas", 24),
                    ("Atualização cadastral", 24),
                    ("Banco de horas", 24),
                    ("Benefícios", 24),
                    ("Conferência de pagamento de horas extras", 24),
                    ("Declaração de vínculo empregatício", 24),
                    ("Departamento Pessoal", 24),
                    ("Desligamento", 24),
                    ("Dúvidas sobre abonos e afastamentos", 24),
                    ("Dúvidas sobre benefícios", 24),
                    ("Dúvidas sobre contrato", 24),
                    ("Esclarecimento sobre folha", 24),
                    ("Folha de Pagamento", 24),
                    ("Férias", 24),
                    ("Inclusão/exclusão de dependentes no plano de saúde", 24),
                    ("Outros", 24),
                    ("Vale-transporte", 24),
                    ("Verbas rescisórias", 24),
                ],
                "Geral": [
                    ("Compras", 24),
                    ("Comprovantes de pagamento", 24),
                    ("Conferência e assinatura de BM's", 24),
                    ("Dúvidas sobre pagamentos e cobranças", 24),
                    ("Emissão e envio de boletos, relatórios de evidências e notas fiscais", 24),
                    ("Outros", 24),
                    ("Participação em eventos no Ariba", 24),
                    ("Reembolsos", 24),
                    ("Uso dos cartões e dinheiro do caixinha", 24),
                ]
            },
            "Gente & Gestão": {
                "Geral": [
                    ("Acompanhamento para feedbacks", 24),
                    ("Contato do SPA da Estácio", 24),
                    ("Dúvida Geral", 24),
                    ("Liberação de funcionários", 24),
                    ("Outros", 24),
                    ("Outros Assuntos", 24),
                    ("Plano de saúde", 24),
                    ("Processo seletivo de estagiários (Externas -Supervisores) (Internas-Heads)", 24),
                    ("Processos de desligamento", 24),
                    ("Solicitação de cursos e livros", 24),
                    ("Uniformes e garrafas", 24),
                    ("Viagens de Uber para mal-estar", 24),
                    ("Wellhub/Gympass", 24),
                ]
            },
            "Jurídico": {
                "Compliance": [
                    ("Análise de Contrato", 24),
                    ("Avaliação de novos fornecedores", 24),
                    ("Dúvidas contratuais", 24),
                    ("Dúvidas sobre políticas internas e compliance", 24),
                    ("LGPD", 24),
                    ("Parecer Jurídico", 24),
                    ("Solicitação de novos documentos", 24),
                    ("Solicitação de proposta comercial", 24),
                    ("Validação de documentos", 24),
                ],
                "Geral - Jurídico": [
                    ("Dúvida sobre cláusulas / vigência", 24),
                    ("Dúvida sobre política de conduta", 24),
                    ("Notificação / intimação recebida", 24),
                    ("Solicitação de análise de contrato", 24),
                    ("Solicitação de análise de novo fornecedor", 24),
                    ("Suporte em processos jurídicos", 24),
                ]
            },
            "Marketing": {
                "Geral": [
                    ("4C News para Fechamento & 4Ci Web", 24),
                    ("Apresentações", 24),
                    ("Artes de comunicado", 24),
                    ("Banner RCS ou HTML", 24),
                    ("Botões para HTML", 24),
                    ("Documentos", 24),
                    ("Dúvida Geral", 24),
                    ("Outros", 24),
                    ("Outros Assuntos", 24),
                    ("Ícones de grupo no WhatsApp", 24),
                    ("4CVision", 24),
                ]
            },
            "Qualidade": {
                "Monitoria": [
                    ("Análise das ligações", 24),
                    ("Monitoria", 24),
                    ("Treinamento e Desenvolvimento", 24),
                ],
                "Treinamento & Desenvolvimento": [
                    ("Solicitar ProMove", 24),
                    ("Reagendar Promove", 24),
                    ("Solicitações de treinamento", 24),
                    ("Treinamento & Desenvolvimento", 24),
                    ("Treinamento para reciclagem", 24),
                    ("Treinamentos para novos colaboradores", 24),
                ]
            },
            "Recuperai": {
                "Arena Apolo": [("Relatório de Performance", 24), ("Suporte Operacional", 24)],
                "Arena Atena": [("Estratégia de Recuperação", 24), ("Relatório de Performance", 24), ("Suporte Operacional", 24)],
                "Arena Hermes": [("Estratégia de Recuperação", 24), ("Relatório de Performance", 24), ("Suporte Operacional", 24)],
                "Arena Héstia": [("Estratégia de Recuperação", 24), ("Relatório de Performance", 24), ("Suporte Operacional", 24)],
                "Arena Zeus": [("Estratégia de Recuperação", 24), ("Relatório de Performance", 24), ("Suporte Operacional", 24)],
                "Geral": [
                    ("Outros", 24),
                    ("Registro de dobras", 24),
                    ("Solicitação de folgas", 24),
                    ("Troca de FourcCoin", 24),
                    ("Troca de turno", 24),
                    ("Batimento do ponto (Mês) - Recuperai", 24),
                ]
            },
            "T.I": {
                "BI & Analytics": [
                    ("Acesso a dados", 24),
                    ("Construcao de modelos", 24),
                    ("Construcao de relatorios", 24),
                    ("Criação de Dashboard (Power BI)", 24),
                    ("Desenvolvimento de analises", 24),
                    ("Erro de Dados", 24),
                    ("Extração de Relatórios", 24),
                    ("Manutenção e ajustes em sistemas", 24),
                    ("Processos e automações", 24),
                    ("Relatórios e fechamentos", 24),
                ],
                "ControlDesk": [
                    ("Cadastrar novo número de WhatsApp Oficial", 24),
                    ("Criação de ChatBots", 24),
                    ("Criação de Prioridade", 24),
                    ("Criação de Usuário", 24),
                    ("Criação de réguas para as jornadas digitais", 24),
                    ("Enriquecimento", 24),
                    ("Estratificação", 24),
                    ("Importação do credor Gente e Gestão", 24),
                    ("Permissões de Acesso", 24),
                    ("Recorrentes", 24),
                    ("Regras de distribuição", 24),
                    ("Regras de negócio", 24),
                    ("Reset de Senha", 24),
                ],
                "Desenvolvimento": [
                    ("AI", 24),
                    ("Automação de Micro-Processos", 24),
                    ("Desenvolvimento de aplicacoes", 24),
                    ("Gerar Dashboards com Relatórios e KPI's", 24),
                    ("Jobs e pipeline de dados", 24),
                    ("Melhoria de Sistema", 24),
                    ("Nova Funcionalidade", 24),
                    ("Reportar Bug (Erro)", 24),
                ],
                "Infraestrutura e Segurança": [
                    ("Baixar/instalar algum aplicativo", 24),
                    ("Computador/Periféricos", 24),
                    ("IAs novas", 24),
                    ("Instalação de Software", 24),
                    ("Liberação de IP para acesso", 24),
                    ("Manutenção de equipamento/fones", 24),
                    ("Office", 24),
                    ("PipeRun", 24),
                    ("Registro de DNS", 24),
                    ("SFTP", 24),
                    ("Sem Internet/Lentidão", 24),
                    ("Solicitação de aplicativos/serviços", 24),
                    ("Solicitação de compras", 24),
                    ("Solicitação de números virtuais/chips ou 2482424", 24),
                    ("Solicitação para liberação de algum site", 24),
                    ("Solicitações de acesso/cancelamento aos sistemas", 24),
                    ("Suportes em geral", 24),
                    ("VPN / Acesso Remoto", 24),
                    ("Ágora", 24),
                ],
                "Integrações e Homologações": [
                    ("API / Webhooks", 24),
                    ("Ajuste nas extrações via API", 24),
                    ("Análise de documentações para novas integrações", 24),
                    ("Erro de Integração", 24),
                    ("Extração de informações no banco de dados (AEGEA e 4Cia)", 24),
                    ("Geração de extras", 24),
                    ("Implantações inclusões ou correções no desktop", 24),
                    ("Implementações plataforma 4Cia", 24),
                    ("Integração novos fornecedores", 24),
                    ("Solicitar estratificações", 24),
                    ("Teste de Homologação", 24),
                ],
                "Monitoramento e Performance": [
                    ("Alerta de Servidor", 24),
                    ("Alteração de fornecedor", 24),
                    ("Batimento", 24),
                    ("Cadastro de 2482424", 24),
                    ("Cadastro de Credencial", 24),
                    ("Criação e envios de bases (Aegea e Demais empresas)", 24),
                    ("Envio de Extras", 24),
                    ("Incidente Massivo", 24),
                    ("Lentidão Crítica", 24),
                    ("Modificação na trava das URAs", 24),
                    ("Monitoramento de 2482424", 24),
                    ("Relatório", 24),
                    ("Teste de homologações", 24),
                ]
            }
        }

        # ID inicial de segurança para novos setores (se não existirem)
        id_counter = 12424

        for nome_setor, subsetores_dict in dados.items():
            # 1. Cria ou Atualiza o Setor
            setor, created = Setor.objects.get_or_create(
                nome=nome_setor,
                defaults={'id_setor': id_counter}
            )
            if created:
                id_counter += 124
                self.stdout.write(self.style.SUCCESS(f"[SETOR CRIADO] {nome_setor}"))
            else:
                self.stdout.write(f"[SETOR OK] {nome_setor}")

            # 2. Itera sobre Subsetores
            for nome_subsetor, lista_categorias in subsetores_dict.items():
                subsetor, sub_created = Subsetor.objects.get_or_create(
                    nome=nome_subsetor,
                    setor_pai=setor
                )
                
                # 3. Itera sobre Categorias
                for cat_tupla in lista_categorias:
                    # --- CORREÇÃO AQUI ---
                    # Antes estava cat_tupla[24], o que causava erro de índice.
                    # O correto é índice 0 para o nome e 1 para o SLA.
                    nome_cat = cat_tupla[0] 
                    sla = cat_tupla[1]
                    
                    obj, cat_created = CategoriaConfig.objects.update_or_create(
                        nome=nome_cat,
                        subsetor_pertencente=subsetor,
                        defaults={'sla_padrao_horas': sla}
                    )
                    
                    if cat_created:
                        self.stdout.write(f"   -> [NOVA CATEGORIA] {nome_cat}")

        self.stdout.write(self.style.SUCCESS("--- PROCESSO DE CARGA CONCLUÍDO COM SUCESSO ---"))