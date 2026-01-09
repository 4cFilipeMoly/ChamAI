from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Chamado, CategoriaConfig, Setor, Colaborador, Subsetor

# --- CADASTRO ---
class CadastroForm(UserCreationForm):
    nome_completo = forms.CharField(max_length=100, required=True, label="Nome Completo", widget=forms.TextInput(attrs={'placeholder': 'Ex: João da Silva'}))
    email = forms.EmailField(required=True, label="Email Corporativo", widget=forms.EmailInput(attrs={'placeholder': 'joao@4cdigital.com.br'}))
    
    # CORREÇÃO: Removido filtro de ID para mostrar TODOS os setores
    setor = forms.ModelChoiceField(
        queryset=Setor.objects.all().order_by('nome'), 
        required=True, 
        label="Seu Setor", 
        empty_label="Selecione seu setor..." 
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'nome_completo', 'setor']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Colaborador.objects.create(user=user, nome=self.cleaned_data['nome_completo'], setor=self.cleaned_data['setor'])
        return user

# --- ABERTURA ---
class AbrirChamadoForm(forms.ModelForm):
    setor_destino = forms.ModelChoiceField(
        queryset=Setor.objects.all().order_by('nome'),
        label="1. Para qual setor é o chamado?",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_setor_destino'}),
        empty_label="Selecione o setor..."
    )
    
    # NOVO CAMPO: SUBSETOR
    subsetor = forms.ModelChoiceField(
        queryset=Subsetor.objects.none(),
        label="2. Qual a área específica?",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_subsetor'}),
        empty_label="Selecione o subsetor..."
    )

    categoria = forms.ModelChoiceField(
        queryset=CategoriaConfig.objects.none(), 
        label="3. Qual o tipo de solicitação?", 
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_categoria'}), 
        empty_label="Selecione a categoria..."
    )

    tipo = forms.ChoiceField(
        choices=[('Normal', 'Normal'), ('Flash', 'Flash')], 
        widget=forms.Select(attrs={'class': 'form-select', 'onchange': 'toggleForm()'}), 
        label="Tipo de Prioridade"
    )
    
    arquivos = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), 
        required=False, 
        label="Evidências/Anexos"
    )
    
    impacto_solicitante = forms.IntegerField(
        min_value=1, max_value=10, initial=5, 
        widget=forms.NumberInput(attrs={'type': 'range', 'class': 'form-range', 'min': '1', 'max': '10', 'step': '1'}), 
        label="Impacto no seu trabalho (1-10)"
    )

    class Meta:
        model = Chamado
        fields = ['setor_destino', 'subsetor', 'categoria', 'titulo', 'descricao', 'impacto_solicitante'] # Adicionado subsetor na lista, mas não salva no model
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Erro ao acessar a VPN'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Descreva detalhadamente...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['arquivos'].widget.attrs.update({'multiple': True})
        
        # Lógica para popular os campos se houver dados (POST ou Edição)
        
        # 1. Popula Subsetor se Setor estiver escolhido
        if 'setor_destino' in self.data:
            try:
                setor_id = int(self.data.get('setor_destino'))
                self.fields['subsetor'].queryset = Subsetor.objects.filter(setor_pai_id=setor_id).order_by('nome')
            except (ValueError, TypeError): pass
        elif self.instance.pk and self.instance.setor_destino_cache:
             # Caso de edição (recupera do cache ou da categoria)
             self.fields['subsetor'].queryset = Subsetor.objects.filter(setor_pai=self.instance.setor_destino_cache).order_by('nome')

        # 2. Popula Categoria se Subsetor estiver escolhido
        if 'subsetor' in self.data:
            try:
                subsetor_id = int(self.data.get('subsetor'))
                self.fields['categoria'].queryset = CategoriaConfig.objects.filter(subsetor_pertencente_id=subsetor_id).order_by('nome')
            except (ValueError, TypeError): pass
        elif self.instance.pk and self.instance.categoria:
            # Caso de edição
            self.fields['subsetor'].initial = self.instance.categoria.subsetor_pertencente
            self.fields['categoria'].queryset = CategoriaConfig.objects.filter(subsetor_pertencente=self.instance.categoria.subsetor_pertencente).order_by('nome')

class EditarChamadoForm(AbrirChamadoForm):
    class Meta(AbrirChamadoForm.Meta):
        # GARANTA QUE 'subsetor' NÃO ESTEJA AQUI
        fields = ['setor_destino', 'categoria', 'titulo', 'descricao', 'impacto_solicitante', 'arquivos'] 
        exclude = ['tipo']

# --- GESTÃO PESSOAS ---
class GestaoColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ['subsetor', 'categorias_atribuidas']
        widgets = {
            'subsetor': forms.Select(attrs={'class': 'form-select'}),
            'categorias_atribuidas': forms.CheckboxSelectMultiple(),
        }
    def __init__(self, *args, **kwargs):
        setor_do_gestor = kwargs.pop('setor_do_gestor', None)
        super().__init__(*args, **kwargs)
        self.fields['subsetor'].label = "Alocar em qual Subsetor?"
        self.fields['categorias_atribuidas'].label = "Permissões de Atendimento"
        if setor_do_gestor:
            self.fields['subsetor'].queryset = Subsetor.objects.filter(setor_pai=setor_do_gestor)
            self.fields['categorias_atribuidas'].queryset = CategoriaConfig.objects.filter(subsetor_pertencente__setor_pai=setor_do_gestor)
        self.fields['subsetor'].empty_label = "Selecione..."

# --- GESTÃO CATEGORIAS ---
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = CategoriaConfig
        # AQUI: Adicionamos o 'sla_padrao_horas' nos campos editáveis
        fields = ['nome', 'subsetor_pertencente', 'sla_padrao_horas']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Erro de Acesso'}),
            'subsetor_pertencente': forms.Select(attrs={'class': 'form-select'}),
            'sla_padrao_horas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Horas'}),
        }
        labels = {
            'nome': 'Nome da Categoria',
            'subsetor_pertencente': 'Subsetor',
            'sla_padrao_horas': 'SLA Padrão (Horas)'
        }

    def __init__(self, *args, **kwargs):
        # Recebe o setor do gestor para filtrar apenas os subsetores dele
        setor_do_gestor = kwargs.pop('setor_do_gestor', None)
        super(CategoriaForm, self).__init__(*args, **kwargs)
        
        if setor_do_gestor:
            self.fields['subsetor_pertencente'].queryset = Subsetor.objects.filter(setor_pai=setor_do_gestor)