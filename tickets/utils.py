from datetime import datetime, timedelta
import pytz
from django.utils import timezone

# Dicionário de Categorias (Copiado do seu código original)
CATEGORIAS_POR_SETOR = {
    "Departamento Pessoal": [
        "Vale-transporte", "Inclusão/exclusão de dependentes no plano de saúde",
        "Dúvidas sobre benefícios", "Esclarecimento sobre folha", "Adiantamento salarial",
        "Conferência de pagamento de horas extras", "Agendamento de férias",
        "Atestados e declarações médicas", "Dúvidas sobre abonos e afastamentos",
        "Atualização cadastral", "Declaração de vínculo empregatício", "Ajuste de ponto",
        "Banco de horas", "Alteração de horário de trabalho", "Dúvidas sobre contrato",
        "Desligamento", "Verbas rescisórias", "Outros"
    ],
    "Marketing": [
        "Banner RCS ou HTML", "Botões para HTML", "Artes de comunicado", "Apresentações",
        "Documentos", "Ícones de grupo no WhatsApp", "4C News para Fechamento & 4Ci Web", "Outros"
    ],
    "Qualidade (VigIA)": ["Análise de ligação", "Treinamento para reciclagem", "Solicitações de treinamento", "Outros"],
    "Financeiro": ["Emissão de notas fiscais", "Comprovantes de pagamento", "Reembolsos", "Dúvidas sobre pagamentos", "Outros"],
    "BI & Analytics": ["Relatórios e fechamentos", "Manutenção e ajustes em sistemas", "Processos e automações", "Outros"],
    "CX (Customer Experience)": ["Alteração de jornada", "Solicitação de extra", "Desenvolvimento de jornada", "Outros"],
    "Gente&Gestão": ["Solicitação de cursos", "Plano de saúde", "Wellhub/Gympass", "Processos de desligamento", "Outros"],
    "Controladoria": ["Informação Contratual", "Precificações", "Orçamento", "Outros"],
    "Compliance": ["Solicitação de proposta comercial", "Validação de documentos", "Dúvidas contratuais", "Outros"],
    "4Cia": ["Atualização de desktop", "Atualização de minmax", "Homologação", "Outros"],
    "T.I": ["Desenvolvimento", "Permissões de acesso", "Infraestrutura", "Outros"],
    "Recuperai": ["Troca de FourcCoin", "Troca de turno", "Solicitação de folgas", "Outros"],
    "Comercial": ["Prospecção", "Outros"]
}

def get_sao_paulo_now():
    """Retorna data/hora atual com timezone de SP"""
    return timezone.now().astimezone(pytz.timezone("America/Sao_Paulo"))

def calcular_data_resposta(ice_score, is_flash=False):
    """Calcula o prazo da primeira resposta"""
    agora = get_sao_paulo_now()
    
    if is_flash:
        return agora + timedelta(hours=1)
    
    # Lógica para chamados normais
    if ice_score >= 7:
        prazo = agora + timedelta(hours=2)
    elif ice_score >= 4:
        prazo = agora + timedelta(hours=6)
    else:
        prazo = agora + timedelta(days=1)
        
    # Ajuste simples de horário comercial (simplificado para o exemplo)
    if prazo.hour >= 18:
        prazo += timedelta(hours=14) # Joga para o dia seguinte de manhã
        
    return prazo

def calcular_prioridade_ice(imp, conf, fac):
    """Calcula a média do ICE Score"""
    try:
        media = (float(imp) + float(conf) + float(fac)) / 3
        return round(media, 2)
    except (TypeError, ValueError):
        return 0.0