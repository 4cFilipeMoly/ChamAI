import json
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from .models import Chamado, Colaborador, CategoriaConfig, Setor, Subsetor
from .forms import AbrirChamadoForm, CadastroForm, EditarChamadoForm, GestaoColaboradorForm, CategoriaForm

# ==============================================================================
# 1. AUTENTICAÇÃO E CADASTRO
# ==============================================================================

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Cadastro realizado! Bem-vindo.")
            return redirect('meus_tickets')
    else:
        form = CadastroForm()
    return render(request, 'tickets/registration/signup.html', {'form': form})

# ==============================================================================
# 2. AJAX (CARREGAMENTO DINÂMICO)
# ==============================================================================

def load_subsetores(request):
    setor_id = request.GET.get('setor_destino')
    if setor_id:
        subsetores = Subsetor.objects.filter(setor_pai_id=setor_id).order_by('nome')
    else:
        subsetores = Subsetor.objects.none()
    return render(request, 'tickets/partials/dropdown_subsetores.html', {'subsetores': subsetores})

def load_categorias(request):
    subsetor_id = request.GET.get('subsetor') 
    if subsetor_id:
        categorias = CategoriaConfig.objects.filter(subsetor_pertencente_id=subsetor_id).order_by('nome')
    else:
        categorias = CategoriaConfig.objects.none()
    return render(request, 'tickets/partials/dropdown_categorias.html', {'categorias': categorias})

# ==============================================================================
# 3. DASHBOARD E KPIs
# ==============================================================================

@login_required
def dashboard_geral(request):
    periodo = request.GET.get('periodo', '30')
    setor_id = request.GET.get('setor', '')
    status_filter = request.GET.get('status', '')
    
    try: 
        dias = int(periodo)
    except: 
        dias = 30
        
    data_limite = timezone.now() - timedelta(days=dias)
    chamados = Chamado.objects.filter(data_abertura__gte=data_limite)
    
    if setor_id: 
        chamados = chamados.filter(setor_destino_cache_id=setor_id)
        
    if status_filter:
        if status_filter == 'abertos': 
            chamados = chamados.exclude(status__in=['Fechado', 'Declinado', 'Evitado', 'Cancelado'])
        elif status_filter == 'fechados': 
            chamados = chamados.filter(status__in=['Fechado', 'Declinado', 'Evitado', 'Cancelado'])
        elif status_filter == 'flash': 
            chamados = chamados.filter(flash=True)
            
    total = chamados.count()
    fechados_count = chamados.filter(status__in=['Fechado', 'Declinado', 'Evitado', 'Cancelado']).count()
    
    context = {
        'kpis': {
            'total': total,
            'em_aberto': total - fechados_count,
            'fechados': fechados_count,
            'sla_estourado': chamados.filter(status='Em Produção', sla_prazo__lt=timezone.now()).count(),
            'flash': chamados.filter(flash=True).count(),
            'taxa_resolucao': round((fechados_count / total * 100), 1) if total > 0 else 0
        },
        'charts': {
            'status_labels': json.dumps([i['status'] for i in chamados.values('status').annotate(total=Count('status')).order_by('-total')]),
            'status_values': json.dumps([i['total'] for i in chamados.values('status').annotate(total=Count('status')).order_by('-total')]),
            'setor_labels': json.dumps([i['setor_destino_cache__nome'] for i in chamados.values('setor_destino_cache__nome').annotate(total=Count('id')).order_by('-total')]),
            'setor_values': json.dumps([i['total'] for i in chamados.values('setor_destino_cache__nome').annotate(total=Count('id')).order_by('-total')]),
        },
        'setores': Setor.objects.all(),
        'filtro_atual': {'periodo': str(dias), 'setor': int(setor_id) if setor_id else '', 'status': status_filter}
    }
    return render(request, 'tickets/dashboard.html', context)

# ==============================================================================
# 4. ÁREA DO CLIENTE (SOLICITANTE)
# ==============================================================================

@login_required
def abrir_chamado(request):
    try: 
        colaborador = request.user.colaborador
    except: 
        return redirect('signup')
        
    if request.method == 'POST':
        form = AbrirChamadoForm(request.POST, request.FILES)
        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.solicitante = colaborador
            
            if form.cleaned_data['tipo'] == 'Flash':
                chamado.flash = True
                chamado.impacto_solicitante = 10
            
            chamado.save()
            
            arquivos = request.FILES.getlist('arquivos')
            if arquivos:
                caminhos = []
                fs = FileSystemStorage()
                for arquivo in arquivos:
                    filename = fs.save(f"anexos/{chamado.id_chamado}/{arquivo.name}", arquivo)
                    caminhos.append(fs.url(filename))
                chamado.caminhos_anexos = {"anexos": caminhos}
                chamado.save()
                
            messages.success(request, f"Chamado #{chamado.id_chamado} criado!")
            return redirect('meus_tickets')
    else:
        form = AbrirChamadoForm()
    return render(request, 'tickets/abrir_chamado.html', {'form': form})

@login_required
def meus_tickets(request):
    chamados = Chamado.objects.filter(solicitante=request.user.colaborador).exclude(status__in=['Fechado', 'Cancelado', 'Declinado', 'Evitado']).order_by('-id_chamado')
    return render(request, 'tickets/meus_tickets.html', {'chamados': chamados})

@login_required
def historico_tickets(request):
    chamados = Chamado.objects.filter(solicitante=request.user.colaborador, status__in=['Fechado', 'Cancelado', 'Declinado', 'Evitado']).order_by('-data_fechamento')
    return render(request, 'tickets/historico.html', {'chamados': chamados})

@login_required
def ver_ticket(request, ticket_id):
    chamado = get_object_or_404(Chamado, id_chamado=ticket_id)
    return render(request, 'tickets/detalhe_ticket.html', {'chamado': chamado})

@login_required
def cancelar_chamado(request, ticket_id):
    chamado = get_object_or_404(Chamado, id_chamado=ticket_id)
    
    if chamado.solicitante != request.user.colaborador: 
        return redirect('meus_tickets')
        
    if not chamado.is_editable:
        messages.error(request, "Prazo expirado para cancelamento.")
        return redirect('meus_tickets')
        
    if request.method == 'POST':
        chamado.status = 'Cancelado'
        chamado.data_fechamento = timezone.now()
        chamado.descricao_resposta = f"{chamado.descricao_resposta or ''}\n[Sistema]: Cancelado em {timezone.now().strftime('%d/%m %H:%M')}."
        chamado.save()
        messages.success(request, "Chamado cancelado.")
        
    return redirect('meus_tickets')

@login_required
def editar_chamado(request, ticket_id):
    chamado = get_object_or_404(Chamado, id_chamado=ticket_id)
    
    if chamado.solicitante != request.user.colaborador:
        return redirect('meus_tickets')
    
    if not chamado.is_editable:
        messages.error(request, "Este chamado já está em atendimento e não pode ser editado.")
        return redirect('meus_tickets')

    if request.method == 'POST':
        form = EditarChamadoForm(request.POST, request.FILES, instance=chamado)
        if form.is_valid():
            ticket = form.save(commit=False)
            
            # --- Regras de Edição ---
            ticket.status = 'Em fila' # Garante que volte para a fila
            ticket.responsavel_tecnico = None # Remove técnico se houver
            ticket.flag_editado = True # Marca que foi editado
            
            ticket.save()
            messages.info(request, "Alterações salvas. O chamado voltou para a fila com uma marcação de edição.")
            return redirect('meus_tickets')
    else:
        form = EditarChamadoForm(instance=chamado)
    
    return render(request, 'tickets/editar_chamado.html', {'form': form, 'chamado': chamado})

@login_required
def meu_perfil(request):
    colab = request.user.colaborador
    total_abertos = Chamado.objects.filter(solicitante=colab).count()
    total_resolvidos = Chamado.objects.filter(responsavel_tecnico=colab, status='Fechado').count()
    return render(request, 'tickets/perfil_usuario.html', {'colab': colab, 'stats': {'abertos': total_abertos, 'resolvidos': total_resolvidos}})    

# ==============================================================================
# 5. ÁREA DO RESOLUTOR (TÉCNICO)
# ==============================================================================

@login_required
def area_resolutor(request):
    colab = request.user.colaborador
    fila = Chamado.objects.filter(status='Em fila', setor_destino_cache=colab.setor).order_by('-flash', 'data_abertura')
    producao = Chamado.objects.filter(status='Em Produção', responsavel_tecnico=colab).order_by('sla_prazo')
    return render(request, 'tickets/area_resolutor.html', {'stats': {'fila': fila.count(), 'meus_prod': producao.count()}, 'fila': fila, 'producao': producao})



@login_required
def realizar_triagem(request, ticket_id):
    chamado = get_object_or_404(Chamado, id_chamado=ticket_id)
    setores = Setor.objects.all()
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        colab = request.user.colaborador
        
        if acao == 'aprovar':
            confianca = int(request.POST.get('confianca', 5))
            facilidade = int(request.POST.get('facilidade', 5))
            sla_input = request.POST.get('sla_prazo')
            
            chamado.confianca_responsavel = confianca
            chamado.facilidade_responsavel = facilidade
            chamado.responsavel_tecnico = colab
            chamado.status = 'Em Produção'
            chamado.data_em_producao = timezone.now()
            
            if sla_input: 
                chamado.sla_prazo = datetime.strptime(sla_input, '%Y-%m-%dT%H:%M')
            else:
                score = (chamado.impacto_solicitante + confianca + facilidade) / 3
                horas = 48 if score < 5 else 24
                chamado.sla_prazo = timezone.now() + timedelta(hours=horas)
            
            chamado.save()
            messages.success(request, f"Chamado em produção! ICE Score: {chamado.ice_score_final}")
            return redirect('area_resolutor')

        elif acao in ['declinar', 'evitar']:
            chamado.status = 'Declinado' if acao == 'declinar' else 'Evitado'
            chamado.justificativa_recusa = request.POST.get('justificativa_recusa')
            chamado.responsavel_tecnico = colab
            chamado.data_fechamento = timezone.now()
            chamado.save()
            messages.warning(request, f"Chamado {chamado.status}.")
            return redirect('area_resolutor')

        elif acao == 'repassar':
            novo_setor = get_object_or_404(Setor, id=request.POST.get('novo_setor'))
            chamado.setor_destino_cache = novo_setor
            chamado.categoria = None
            chamado.descricao_resposta = f"{chamado.descricao_resposta or ''}\n[REPASSE]: Para {novo_setor.nome}. Motivo: {request.POST.get('justificativa_recusa')}"
            chamado.status = 'Em fila'
            chamado.responsavel_tecnico = None
            chamado.save()
            messages.info(request, "Repassado.")
            return redirect('area_resolutor')

    return render(request, 'tickets/triagem_ticket.html', {'chamado': chamado, 'setores': setores})

@login_required
@login_required
def acao_workflow(request, ticket_id, acao):
    chamado = get_object_or_404(Chamado, id_chamado=ticket_id)
    
    # Segurança: Só o responsável pode mexer (ou um gestor)
    if chamado.responsavel_tecnico != request.user.colaborador and not request.user.colaborador.is_manager:
        messages.error(request, "Você não é o responsável técnico deste chamado.")
        return redirect('area_resolutor')

    # 1. PAUSAR (STAND BY)
    if acao == 'pausar':
        if chamado.status != 'Stand By':
            chamado.pausar_sla() # Método do Model
            chamado.descricao_resposta = f"{chamado.descricao_resposta or ''}\n[{timezone.now().strftime('%d/%m %H:%M')}] Status: Stand By (Aguardando Cliente/Terceiro)."
            chamado.save()
            messages.warning(request, f"Chamado #{chamado.id_chamado} pausado. O SLA parou de contar.")

    # 2. RETOMAR (DE VOLTA PARA PRODUÇÃO)
    elif acao == 'retomar':
        if chamado.status == 'Stand By':
            chamado.retomar_sla() # Método do Model (Recalcula SLA)
            chamado.descricao_resposta = f"{chamado.descricao_resposta or ''}\n[{timezone.now().strftime('%d/%m %H:%M')}] Status: Em Produção (SLA Retomado)."
            chamado.save()
            messages.success(request, f"Chamado #{chamado.id_chamado} retomado! Novo prazo calculado.")

    # 3. ENVIAR PARA HOMOLOGAÇÃO
    elif acao == 'homologar':
        chamado.status = 'Homologação'
        chamado.descricao_resposta = f"{chamado.descricao_resposta or ''}\n[{timezone.now().strftime('%d/%m %H:%M')}] Status: Homologação (Enviado para validação)."
        chamado.save()
        messages.info(request, "Enviado para homologação do solicitante.")

    # 4. FECHAR CHAMADO
    elif acao == 'fechar':
        chamado.status = 'Fechado'
        chamado.data_fechamento = timezone.now()
        chamado.descricao_resposta = f"{chamado.descricao_resposta or ''}\n[{timezone.now().strftime('%d/%m %H:%M')}] Status: Fechado (Concluído)."
        chamado.save()
        messages.success(request, "Chamado encerrado com sucesso!")

    return redirect('area_resolutor')

# ==============================================================================
# 6. PAINEL DE GESTÃO (MANAGER)
# ==============================================================================

@login_required
def painel_gestor(request):
    try: 
        gestor = request.user.colaborador
    except: 
        return redirect('dashboard_geral')
        
    if not gestor.is_manager: 
        messages.error(request, "Acesso restrito.")
        return redirect('dashboard_geral')

    colaboradores = Colaborador.objects.filter(setor=gestor.setor).select_related('setor', 'subsetor').order_by('nome')
    categorias = CategoriaConfig.objects.filter(subsetor_pertencente__setor_pai=gestor.setor).order_by('subsetor_pertencente__nome', 'nome')
    
    aba_ativa = request.GET.get('aba', 'pessoas')
    user_id = request.GET.get('editar_user')
    cat_id = request.GET.get('editar_cat')
    
    form_user, form_cat, objeto_em_edicao = None, None, None

    if request.method == 'POST':
        tipo_acao = request.POST.get('tipo_acao')
        
        # --- SALVAR USUÁRIO ---
        if tipo_acao == 'salvar_user':
            colab = get_object_or_404(Colaborador, id=request.POST.get('user_id'), setor=gestor.setor)
            form_user = GestaoColaboradorForm(request.POST, instance=colab, setor_do_gestor=gestor.setor)
            
            if form_user.is_valid():
                colab_salvo = form_user.save()
                
                # SE É HEAD, TEM ACESSO A TUDO
                if colab_salvo.is_manager:
                    todas_cats = CategoriaConfig.objects.filter(subsetor_pertencente__setor_pai=gestor.setor)
                    colab_salvo.categorias_atribuidas.set(todas_cats)
                    colab_salvo.save()
                    messages.success(request, f"Permissões de {colab_salvo.nome} atualizadas! (Head recebe acesso total).")
                else:
                    messages.success(request, f"Permissões de {colab_salvo.nome} atualizadas!")
                
                return redirect(f"{request.path}?aba=pessoas")
            aba_ativa = 'pessoas'
        
        # --- SALVAR CATEGORIA ---
        elif tipo_acao == 'salvar_cat':
            cat_pk = request.POST.get('cat_id')
            if cat_pk:
                cat = get_object_or_404(CategoriaConfig, id=cat_pk, subsetor_pertencente__setor_pai=gestor.setor)
                form_cat = CategoriaForm(request.POST, instance=cat, setor_do_gestor=gestor.setor)
            else: 
                form_cat = CategoriaForm(request.POST, setor_do_gestor=gestor.setor)
            
            if form_cat.is_valid():
                cat_salva = form_cat.save()
                
                # Vincula aos Heads automaticamente
                heads = Colaborador.objects.filter(setor=gestor.setor, is_manager=True)
                for head in heads:
                    head.categorias_atribuidas.add(cat_salva)
                
                messages.success(request, "Categoria salva! (Vinculada automaticamente aos Heads).")
                return redirect(f"{request.path}?aba=categorias")
            aba_ativa = 'categorias'

    # GET (Carregamento)
    else:
        if user_id:
            colab = get_object_or_404(Colaborador, id=user_id, setor=gestor.setor)
            form_user = GestaoColaboradorForm(instance=colab, setor_do_gestor=gestor.setor)
            objeto_em_edicao = colab
            aba_ativa = 'pessoas'
        if cat_id:
            cat = get_object_or_404(CategoriaConfig, id=cat_id, subsetor_pertencente__setor_pai=gestor.setor)
            form_cat = CategoriaForm(instance=cat, setor_do_gestor=gestor.setor)
            objeto_em_edicao = cat
            aba_ativa = 'categorias'
        if request.GET.get('nova_cat'):
            form_cat = CategoriaForm(setor_do_gestor=gestor.setor)
            aba_ativa = 'categorias'

    return render(request, 'tickets/painel_gestor.html', {
        'colaboradores': colaboradores, 'categorias': categorias,
        'form_user': form_user, 'form_cat': form_cat,
        'objeto_em_edicao': objeto_em_edicao, 'aba_ativa': aba_ativa, 'setor_gestor': gestor.setor.nome
    })

@login_required
def gerenciar_workflow(request, ticket_id):
    if request.method != 'POST':
        return redirect('area_resolutor')

    chamado = get_object_or_404(Chamado, id_chamado=ticket_id)
    
    # Segurança
    if chamado.responsavel_tecnico != request.user.colaborador and not request.user.colaborador.is_manager:
        messages.error(request, "Você não é o responsável.")
        return redirect('area_resolutor')

    # Dados do Formulário
    acao = request.POST.get('acao_escolhida')
    justificativa = request.POST.get('justificativa', '').strip()
    arquivo = request.FILES.get('arquivo_anexo')
    
    # Monta o texto de histórico
    agora = timezone.now().strftime('%d/%m %H:%M')
    texto_historico = f"\n[{agora}] Ação: {acao.upper()}"
    if justificativa:
        texto_historico += f" | Motivo: {justificativa}"

    # Processamento do Arquivo (se houver)
    if arquivo:
        fs = FileSystemStorage()
        filename = fs.save(f"anexos/{chamado.id_chamado}/{arquivo.name}", arquivo)
        url_arquivo = fs.url(filename)
        
        # Atualiza o JSON de anexos
        if not chamado.caminhos_anexos:
            chamado.caminhos_anexos = {"anexos": []}
        
        # Garante que é uma lista antes de append
        lista_anexos = chamado.caminhos_anexos.get('anexos', [])
        lista_anexos.append(url_arquivo)
        chamado.caminhos_anexos['anexos'] = lista_anexos
        
        texto_historico += f" | (Arquivo anexado: {arquivo.name})"

    # Aplica a Lógica de Status
    if acao == 'pausar':
        if chamado.status != 'Stand By':
            chamado.pausar_sla()
            chamado.descricao_resposta = (chamado.descricao_resposta or '') + texto_historico
            chamado.save()
            messages.warning(request, f"Chamado #{ticket_id} pausado.")

    elif acao == 'retomar':
        chamado.retomar_sla()
        chamado.descricao_resposta = (chamado.descricao_resposta or '') + texto_historico
        chamado.save()
        messages.success(request, f"Chamado #{ticket_id} retomado.")

    elif acao == 'homologar':
        chamado.status = 'Homologação'
        chamado.descricao_resposta = (chamado.descricao_resposta or '') + texto_historico
        chamado.save()
        messages.info(request, "Enviado para homologação.")

    elif acao == 'fechar':
        chamado.status = 'Fechado'
        chamado.data_fechamento = timezone.now()
        chamado.descricao_resposta = (chamado.descricao_resposta or '') + texto_historico
        chamado.save()
        messages.success(request, "Chamado encerrado.")
    
    elif acao == 'voltar_producao': # Caso volte da homologação
        chamado.retomar_sla() # Serve para voltar status para produção
        chamado.descricao_resposta = (chamado.descricao_resposta or '') + texto_historico
        chamado.save()
        messages.info(request, "Chamado voltou para produção.")

    return redirect('area_resolutor')