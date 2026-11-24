# NaNo Hub — UFRRJ

Aplicação de gestão laboratorial construída com Python, Streamlit e Supabase, usando a identidade visual NaNo & UFRRJ.

## Módulos incluídos
- Visão geral com indicadores, agenda do dia e alertas de estoque
- Cadastro de pesquisadores
- Escala semanal e reserva de equipamentos
- Cadastro e status de equipamentos
- Estoque de reagentes e insumos
- Projetos de pesquisa
- Caderno experimental
- Biblioteca científica
- Mural de avisos

## 1. Requisitos
Python 3.10 ou superior.

```bash
pip install -r requirements.txt
```

## 2. Configurar Supabase
1. Crie ou abra seu projeto no Supabase.
2. Abra **SQL Editor**.
3. Revise `schema.sql` e execute-o. Se você já possui tabelas com esses nomes, faça backup e compare as colunas antes; não execute alterações destrutivas.
4. Em **Project Settings → API**, copie a Project URL e a chave `anon` (public).
5. Copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e preencha:

```toml
SUPABASE_URL = "https://SEU-PROJETO.supabase.co"
SUPABASE_KEY = "SUA_CHAVE_ANON"
```

Não publique o arquivo `secrets.toml` no GitHub.

## 3. Executar localmente
```bash
streamlit run app.py
```

## 4. Publicar
Pode ser publicado no Streamlit Community Cloud, Render ou outro serviço compatível. Configure `SUPABASE_URL` e `SUPABASE_KEY` nos secrets/variáveis de ambiente da plataforma.

## Observações importantes
- Este pacote é uma primeira versão funcional de base. Faça testes com dados fictícios antes de migrar os dados reais do laboratório.
- O formulário de reserva faz uma checagem de conflito na aplicação, mas isso não elimina condições de corrida entre usuários. Para produção, implemente a validação transacional no PostgreSQL (por exemplo, constraint de exclusão usando `btree_gist`) ou uma função RPC.
- A aplicação ainda não implementa autenticação individual, trilha de auditoria nem políticas RLS. Antes de abrir o acesso à internet, configure Supabase Auth, RLS por perfil e permissões administrativas.
- Uploads de arquivos devem usar Supabase Storage; a biblioteca atual registra links/URLs, não faz upload direto.
- O caderno experimental é um registro operacional e não substitui caderno institucional validado, procedimentos de segurança ou registros oficiais.
- A estrutura de tabelas pode precisar de migração/adaptação para preservar as tabelas antigas `escala_laboratorio`, `reservas_equipamentos` e `mural_avisos`.
