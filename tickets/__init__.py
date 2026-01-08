def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # --- 1. HABILITA UPLOAD MÚLTIPLO (ESSENCIAL) ---
        # Adiciona o atributo 'multiple' no HTML via código para não travar o Django
        self.fields['arquivos'].widget.attrs.update({'multiple': True})
        
        # --- 2. LÓGICA DO SELECT EM CASCATA ---
        # Começa vazio para obrigar o usuário a escolher o setor primeiro
        self.fields['categoria'].queryset = CategoriaConfig.objects.none()

        # Se o formulário foi enviado (tem dados no POST)
        if 'setor_destino' in self.data:
            try:
                setor_id = int(self.data.get('setor_destino'))
                # Filtra categorias pelo setor escolhido
                self.fields['categoria'].queryset = CategoriaConfig.objects.filter(setor_dono_id=setor_id).order_by('nome')
            except (ValueError, TypeError):
                pass 
        
        # Se for edição de um chamado que já existe
        elif self.instance.pk:
            if self.instance.setor_destino:
                self.fields['categoria'].queryset = CategoriaConfig.objects.filter(setor_dono=self.instance.setor_destino).order_by('nome')