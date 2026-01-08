"""
Aplicativo Streamlit para cadastro e validação de componentes curriculares.
Interface principal para professores e coordenadores de curso.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
from utils.calculos import (
    calcular_ch_total,
    calcular_ch_total_curso,
    calcular_ch_por_nucleo,
    calcular_percentual_extensao,
    calcular_percentual_pratica_pedagogica,
    obter_ch_minima_por_nucleo,
    validar_ch_minima_nucleo
)
from utils.validacoes import validar_componente, validar_curso_completo
from utils.exportacoes import exportar_csv, exportar_xlsx, exportar_pdf, gerar_resumo_por_semestre_nucleo, gerar_matriz_por_periodo

# Configuração da página
st.set_page_config(
    page_title="Sistema de Componentes Curriculares",
    page_icon="📚",
    layout="wide"
)

# Estilos personalizados CSS
st.markdown(
"""
<style>
:root{
  --ufal-blue:#0B5FA5;
  --ufal-blue-hover:#084C84;
  --ufal-blue-active:#063A66;

  --ufal-bg:#FFFFFF;
  --ufal-surface:#F7F9FB;
  --ufal-border:#D7DEE6;

  --ufal-text:#1F2A37;
  --ufal-muted:#5B6B7A;

  --ufal-danger:#C62828;
  --ufal-danger-bg:#FDECEC;
}

/* Base do app */
html, body, .stApp{
  background:var(--ufal-bg) !important;
  color:var(--ufal-text) !important;
  font-family: system-ui, -apple-system, "Segoe UI", Arial, Helvetica, sans-serif !important;
  font-size:13.5px !important;
  line-height:1.45 !important;
}

/* Texto geral */
.stMarkdown, .stText, .stCaption, p, div, span, label{
  color:var(--ufal-text) !important;
  font-family: system-ui, -apple-system, "Segoe UI", Arial, Helvetica, sans-serif !important;
}

/* Títulos */
h1{
  font-size:1.30rem !important;
  font-weight:600 !important;
  margin:0.25rem 0 !important;
}
h2{
  font-size:1.12rem !important;
  font-weight:600 !important;
  margin:0.75rem 0 0.25rem 0 !important;
}
h3{
  font-size:1.02rem !important;
  font-weight:600 !important;
  margin:0.50rem 0 0.25rem 0 !important;
}

/* Divisórias */
hr{
  border:none !important;
  border-top:1px solid var(--ufal-border) !important;
  margin:0.75rem 0 !important;
}

/* Links */
a, a:visited{
  color:var(--ufal-blue) !important;
  text-decoration:underline !important;
}
a:hover{
  color:var(--ufal-blue-hover) !important;
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
div[data-baseweb="select"] > div{
  border:1px solid var(--ufal-border) !important;
  border-radius:6px !important;
  background:#FFFFFF !important;
  color:var(--ufal-text) !important;
}

/* Foco acessível */
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
div[data-baseweb="select"] [role="combobox"]:focus,
button:focus,
button:focus-visible{
  outline:3px solid rgba(11,95,165,0.35) !important;
  outline-offset:2px !important;
}

/* Botões – padrão único azul */
.stButton > button,
div[data-testid="stDownloadButton"] > button,
button[kind="primary"]{
  background-color:var(--ufal-blue) !important;
  border:1px solid var(--ufal-blue) !important;
  color:#FFFFFF !important;
  border-radius:6px !important;
  padding:0.45rem 0.9rem !important;
  font-weight:600 !important;
}

.stButton > button *,
div[data-testid="stDownloadButton"] > button *,
button[kind="primary"] *{
  color:#FFFFFF !important;
}

.stButton > button:hover,
div[data-testid="stDownloadButton"] > button:hover,
button[kind="primary"]:hover{
  background-color:var(--ufal-blue-hover) !important;
  border-color:var(--ufal-blue-hover) !important;
}

.stButton > button:active,
div[data-testid="stDownloadButton"] > button:active,
button[kind="primary"]:active{
  background-color:var(--ufal-blue-active) !important;
  border-color:var(--ufal-blue-active) !important;
}

.stButton > button:disabled,
div[data-testid="stDownloadButton"] > button:disabled{
  opacity:0.55 !important;
  cursor:not-allowed !important;
}

/* Dropdown / Selectbox – fonte compacta e legível */
div[data-baseweb="select"],
div[data-baseweb="select"] *{
  font-family: system-ui, -apple-system, "Segoe UI", Arial, Helvetica, sans-serif !important;
  font-size:13px !important;
}

/* Dropdown opções */
div[data-baseweb="select"] ul[role="listbox"] li{
  color:var(--ufal-text) !important;
}

/* Opção selecionada */
div[data-baseweb="select"] ul[role="listbox"] li[aria-selected="true"]{
  background-color:var(--ufal-blue) !important;
}
div[data-baseweb="select"] ul[role="listbox"] li[aria-selected="true"] *{
  color:#FFFFFF !important;
}

/* Tags do multiselect */
div[data-baseweb="tag"]{
  background-color:var(--ufal-blue) !important;
  border:1px solid var(--ufal-blue) !important;
  color:#FFFFFF !important;
}
div[data-baseweb="tag"] *{
  color:#FFFFFF !important;
}

/* Tabelas */
.stDataFrame{
  border:1px solid var(--ufal-border) !important;
  border-radius:6px !important;
  overflow:hidden !important;
}

/* Layout */
.stImage{ margin-bottom:0 !important; }
[data-testid="column"]{ padding-right:10px !important; }

/* Backup expander flutuante */
#ufal-backup-menu{
  position:relative !important;
  z-index:9999 !important;
}

#ufal-backup-menu div[data-testid="stExpander"] details[open] > div,
#ufal-backup-menu div[data-testid*="expanderContent"]{
  position:absolute !important;
  right:0 !important;
  top:calc(100% + 6px) !important;
  background:#FFFFFF !important;
  border:1px solid var(--ufal-border) !important;
  border-radius:6px !important;
  box-shadow:0 8px 24px rgba(0,0,0,0.18) !important;
  padding:12px !important;
  min-width:500px !important;
  max-width:500px !important;
  z-index:10001 !important;
}

/* Remover ícone quebrado do expander */
div[data-testid="stExpander"] summary span[data-testid="stExpanderIcon"]{
  display:none !important;
}
</style>
""",
unsafe_allow_html=True
)

# Temas do Núcleo I (Art. 13 a-i da Res. CNE/CP nº 4/2024)
TEMAS_NUCLEO_I = [
    "a) Princípios e fundamentos sociológicos, filosóficos, históricos e epistemológicos da educação",
    "b) Princípios, valores e atitudes comprometidos com a justiça social, reconhecimento, respeito e apreço à diversidade, promoção da participação, da equidade e da inclusão e gestão democrática",
    "c) Observação, análise, planejamento, desenvolvimento e avaliação de processos educativos, experiências pedagógicas e de situações de ensino e aprendizagem em instituições de Educação Básica",
    "d) Conhecimento multidimensional e interdisciplinar sobre o ser humano e práticas educativas, incluindo conhecimento de processos de desenvolvimento de crianças, adolescentes, jovens e adultos, nas dimensões física, cognitiva, afetiva, estética, cultural, lúdica, artística, ética e biopsicossocial",
    "e) Diagnóstico e análise das necessidades e aspirações dos diferentes segmentos da sociedade, relativas à educação, sendo capaz de identificar diferentes forças e interesses, de captar contradições e de considerá-los nos planos pedagógicos, no ensino e, consequentemente, nos processos de aprendizagem",
    "f) Pesquisa e estudo da legislação educacional, dos processos de organização e gestão do trabalho dos profissionais do magistério da educação escolar básica, das políticas de financiamento, da avaliação e do currículo",
    "g) Pesquisa e estudo das relações entre educação e trabalho, educação e diversidade, educação e comunicação, direitos humanos, cidadania, educação ambiental, entre outras problemáticas centrais da sociedade contemporânea",
    "h) Estudos de aspectos éticos, didáticos e comportamentais no contexto do exercício profissional, articulando o saber acadêmico, a pesquisa, a extensão e a prática educativa",
    "i) Conhecimento sobre diferentes estratégias de planejamento e avaliação das aprendizagens, centradas no desenvolvimento pleno dos estudantes da Educação Básica"
]

# Tipos de componentes disponíveis
TIPOS_COMPONENTES = [
    "Disciplina",
    "Módulo",
    "Bloco",
    "Estágio",
    "TCC",
    "Extensão",
    "Outro"
]

# Inicializar estado da sessão
if "componentes" not in st.session_state:
    st.session_state.componentes = []

if "ultimo_id" not in st.session_state:
    st.session_state.ultimo_id = 0


def limpar_formulario():
    """Limpa os campos do formulário após adicionar um componente."""
    # Usar update para evitar conflito com widgets instanciados
    valores_limpos = {}
    for key in ["form_nome", "form_tipo", "form_aulas_semanais", "form_ch_manual", "form_ch_teorica", 
                "form_ch_pratica", "form_ch_extensao", "form_nucleo", "form_temas_nucleo_i",
                "form_diretrizes_nucleo_ii", "form_descricao_extensao", "form_local_realizacao",
                "form_etapa_estagio_opcao", "form_etapa_estagio_outro", "form_bloco", 
                "form_observacoes", "form_nucleo_selecionado", "form_ch_preview"]:
        if key == "form_semestre":
            valores_limpos[key] = 1
        elif key in ["form_aulas_semanais", "form_ch_manual", "form_ch_teorica", 
                    "form_ch_pratica", "form_ch_extensao", "form_ch_preview"]:
            valores_limpos[key] = 0.0
        elif key == "form_temas_nucleo_i":
            valores_limpos[key] = []
        elif key == "form_nucleo_selecionado":
            valores_limpos[key] = ""
        else:
            valores_limpos[key] = ""
    
    # Marcar para limpar na próxima renderização (usar flag)
    st.session_state["limpar_formulario"] = True
    st.session_state["valores_limpos"] = valores_limpos


def adicionar_componente(dados: dict):
    """Adiciona um novo componente à lista."""
    st.session_state.ultimo_id += 1
    dados["id"] = st.session_state.ultimo_id
    st.session_state.componentes.append(dados.copy())


def remover_componente(id_componente: int):
    """Remove um componente da lista."""
    st.session_state.componentes = [
        comp for comp in st.session_state.componentes 
        if comp.get("id") != id_componente
    ]


def exportar_backup_json(componentes: list, ultimo_id: int) -> str:
    """
    Exporta os dados do curso para um arquivo JSON (backup).
    
    Args:
        componentes: Lista de componentes
        ultimo_id: Último ID usado
    
    Returns:
        String JSON serializada
    """
    dados_backup = {
        "componentes": componentes,
        "ultimo_id": ultimo_id,
        "data_backup": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "versao": "1.0"
    }
    return json.dumps(dados_backup, ensure_ascii=False, indent=2)


def importar_backup_json(arquivo_json: str) -> tuple[list, int, bool, str]:
    """
    Importa dados de backup a partir de um arquivo JSON.
    
    Args:
        arquivo_json: String JSON com os dados
    
    Returns:
        Tupla (componentes, ultimo_id, sucesso, mensagem)
    """
    try:
        dados = json.loads(arquivo_json)
        
        if "componentes" not in dados or "ultimo_id" not in dados:
            return [], 0, False, "Formato de arquivo inválido. O arquivo deve conter 'componentes' e 'ultimo_id'."
        
        componentes = dados["componentes"]
        ultimo_id = dados.get("ultimo_id", 0)
        
        if not isinstance(componentes, list):
            return [], 0, False, "Formato inválido: 'componentes' deve ser uma lista."
        
        if not isinstance(ultimo_id, (int, float)):
            return [], 0, False, "Formato inválido: 'ultimo_id' deve ser um número."
        
        return componentes, int(ultimo_id), True, f"Backup restaurado com sucesso! {len(componentes)} componente(s) carregado(s)."
    
    except json.JSONDecodeError as e:
        return [], 0, False, f"Erro ao ler arquivo JSON: {str(e)}"
    except Exception as e:
        return [], 0, False, f"Erro ao importar backup: {str(e)}"


def obter_explicacao_nucleo(nucleo: str) -> str:
    """Retorna explicação detalhada sobre as regras do núcleo."""
    explicacoes = {
        "I": """
        **NÚCLEO I – Formação Pedagógica**
        
        O Núcleo I deve ter **mínimo de 880 horas** e compreende a Formação Pedagógica.
        
        **Requisitos:**
        - Deve selecionar **pelo menos um tema** do Art. 13 da Res. CNE/CP nº 4/2024
        - Os temas cobrem princípios, fundamentos, didática, gestão e práticas educativas
        
        **Temas disponíveis (Art. 13 a-i):**
        - Princípios e fundamentos sociológicos, filosóficos, históricos e epistemológicos da educação
        - Princípios de justiça social, diversidade, equidade e inclusão
        - Processos educativos e experiências pedagógicas
        - Conhecimento multidimensional sobre o ser humano e práticas educativas
        - Diagnóstico e análise das necessidades educacionais
        - Legislação educacional, organização e gestão do trabalho docente
        - Relações entre educação e trabalho, diversidade, comunicação, direitos humanos
        - Aspectos éticos, didáticos e comportamentais no exercício profissional
        - Estratégias de planejamento e avaliação das aprendizagens
        """,
        "II": """
        **NÚCLEO II – Formação Específica da Área de Conhecimento**
        
        O Núcleo II deve ter **mínimo de 1600 horas** e compreende a Formação Específica da Área.
        
        **Requisitos:**
        - Deve indicar a **vinculação com as Diretrizes da área de conhecimento específica**
        - Campo de texto livre para descrever como o componente se relaciona com as diretrizes curriculares da área
        - Não há lista fixa de temas, mas deve estar alinhado com as diretrizes nacionais da área
        
        **Características:**
        - Flexível e adaptável às necessidades específicas de cada curso
        - Deve contemplar conhecimentos específicos da área de formação
        - Integração com as práticas pedagógicas da área
        """,
        "III": """
        **NÚCLEO III – Atividades de Extensão**
        
        O Núcleo III deve ter **mínimo de 320 horas** e representa as Atividades de Extensão.
        
        **Requisitos:**
        - Deve representar **pelo menos 10% da CH total do curso**
        - Componente deve ter **vínculo explícito com projeto extensionista**
        - Campo obrigatório para descrever o vínculo com o projeto de extensão
        
        **Características:**
        - Articulação entre ensino, pesquisa e extensão
        - Interação com a comunidade
        - Aplicação de conhecimentos em contextos reais
        - Se o componente tiver CH de Extensão > 0, deve obrigatoriamente pertencer a este núcleo
        """,
        "IV": """
        **NÚCLEO IV – Estágios Supervisionados**
        
        O Núcleo IV deve ter **mínimo de 400 horas** e compreende os Estágios Supervisionados.
        
        **Requisitos:**
        - Componentes do tipo **Estágio** devem obrigatoriamente pertencer a este núcleo
        - Estágios devem ter **mínimo de 400 horas totais**
        - **Local de realização** é obrigatório (ex: escolas, centros de educação)
        - **Etapa do estágio** é obrigatória (Observação, Regência Parcial, Regência Final, etc.)
        
        **Características:**
        - Vivência prática em ambientes escolares
        - Supervisão docente
        - Progressão das etapas formativas
        - Articulação entre teoria e prática
        """
    }
    return explicacoes.get(nucleo, "")


def exibir_regras_ppc():
    """Exibe todas as regras para construção do PPC."""
    st.header("Regras para Construção do PPC")
    st.markdown("---")
    
    with st.expander("Cargas Horárias Mínimas por Núcleo", expanded=True):
        st.markdown("""
        | Núcleo | Descrição | CH Mínima |
        |--------|-----------|-----------|
        | **I** | Formação Pedagógica | 880h |
        | **II** | Formação Específica da Área | 1600h |
        | **III** | Atividades de Extensão | 320h |
        | **IV** | Estágios Supervisionados | 400h |
        | **Total** | Carga horária total do curso | **≥3200h** |
        """)
    
    with st.expander("Regras de Percentuais", expanded=True):
        st.markdown("""
        - **Extensão (Núcleo III)**: Deve representar **pelo menos 10% da CH total do curso**
        - **Prática Pedagógica**: Percentual calculado como (CH Prática ÷ CH Total) × 100
        """)
    
    with st.expander("Associações Obrigatórias", expanded=True):
        st.markdown("""
        - **Componentes com CH de Extensão > 0** → Devem pertencer ao **Núcleo III**
        - **Componentes do tipo Estágio** → Devem pertencer ao **Núcleo IV**
        - **Estágios** → Devem ter carga horária **mínima de 400h**
        """)
    
    with st.expander("Campos Obrigatórios por Núcleo", expanded=True):
        st.markdown("""
        **Núcleo I:**
        - Seleção de pelo menos um tema do Art. 13 (a-i)
        
        **Núcleo II:**
        - Indicação das Diretrizes Específicas da Área
        
        **Núcleo III:**
        - Vínculo com Projeto Extensionista
        
        **Núcleo IV:**
        - Local de Realização
        - Etapa do Estágio (Observação, Regência Parcial, Regência Final, etc.)
        """)
    
    with st.expander("Cálculo de Carga Horária", expanded=True):
        st.markdown("""
        - **Disciplinas**: CH Total = Aulas Semanais × 18 horas
        - **Outros tipos** (Módulo, Bloco, Estágio, TCC, Extensão, Outro): CH Total informada manualmente
        
        **Campos opcionais (podem ajudar nas análises):**
        - CH Teórica
        - CH Prática
        - CH Extensão
        """)
    
    with st.expander("Validações Automáticas", expanded=True):
        st.markdown("""
        O sistema valida automaticamente:
        
        - CH mínima por núcleo (I ≥880h, II ≥1600h, III ≥320h, IV ≥400h)
        - CH total do curso (≥3200h)
        - Percentual de extensão (≥10%)
        - Associações obrigatórias (Extensão→Núcleo III, Estágio→Núcleo IV)
        - Campos obrigatórios por núcleo
        - Mínimo de 400h para estágios
        
        **Status visual:**
        - Verde: Conforme com as regras
        - Vermelho: Não conforme (mostra o que falta)
        """)


def main():
    """Função principal da aplicação."""
    
    col_logo, col_title, col_aviso = st.columns([0.10, 0.75, 0.15])
    with col_logo:
        logo_path = "assets/logo_ufal.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
    
    with col_title:
        st.markdown('<h1 style="margin-top: 30px; margin-bottom: 0; padding-left: 10px;">Sistema de Componentes Curriculares</h1>', unsafe_allow_html=True)
    
    with col_aviso:
        st.markdown('<div id="ufal-backup-menu" style="margin-top:35px; text-align:right; position:relative;">',unsafe_allow_html=True)

        with st.expander("⚠️ Não perca seus dados, backup", expanded=False):
            st.markdown("""
            **⚠️ IMPORTANTE**
        
            O site **não salva seus dados automaticamente**.
        
            Realize o **backup manual** na aba "Exportar" para não perder seus dados!
        
            Caso feche o site sem backup, os dados **não serão restaurados**.
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Como Usar",
        "Cadastrar", 
        "Componentes", 
        "Prévia - Matriz", 
        "Prévia - Por Núcleo",
        "Exportar", 
        "Regras"
    ])
    
    with tab1:
        st.header("Como Usar o Sistema")
        st.markdown("---")
        
        st.subheader("Visão Geral")
        st.markdown("""
        Este sistema foi desenvolvido para auxiliar professores e coordenadores de curso no cadastro, 
        validação e organização de componentes curriculares de cursos de Licenciatura, seguindo as 
        diretrizes da Resolução CNE/CP nº 4/2024.
        
        O sistema permite cadastrar componentes curriculares, validar automaticamente a conformidade 
        com as normas, visualizar a matriz curricular organizada por período e núcleo, e exportar 
        relatórios em diferentes formatos.
        """)
        
        st.subheader("Passo a Passo para Criar um PPC")
        
        st.markdown("""
        **1. Cadastrar Componentes Curriculares**
        
        Acesse a aba "Cadastrar" e preencha o formulário para cada componente do curso:
        
        - **Semestre**: Informe em qual período o componente será oferecido (1 a 20)
        - **Nome do Componente**: Digite o nome completo da disciplina, módulo, estágio, etc.
        - **Tipo**: Selecione o tipo (Disciplina, Módulo, Bloco, Estágio, TCC, Extensão, Outro)
        - **Carga Horária**: 
          - Para Disciplinas: informe o número de aulas semanais (a CH total será calculada automaticamente: aulas × 18h)
          - Para outros tipos: informe a CH total manualmente
        - **Núcleo**: Selecione o núcleo curricular (I, II, III ou IV)
        
        Após selecionar o núcleo, clique em "Atualizar Informações" para ver os campos específicos:
        
        - **Núcleo I (Formação Pedagógica)**: Selecione pelo menos um tema do Art. 13 (a-i)
        - **Núcleo II (Formação Específica)**: Descreva a vinculação com as Diretrizes da área
        - **Núcleo III (Extensão)**: Descreva o vínculo com projeto extensionista
        - **Núcleo IV (Estágios)**: Informe local de realização e etapa do estágio
        
        Campos opcionais que podem ajudar nas análises:
        - CH Teórica, CH Prática, CH Extensão
        - Bloco (se o componente faz parte de um grupo)
        - Observações
        
        Clique em "Adicionar Componente" para salvar.
        
        **2. Visualizar Componentes Cadastrados**
        
        Na aba "Componentes", você pode:
        - Ver todos os componentes cadastrados
        - Visualizar o resumo por semestre e núcleo
        - Remover componentes se necessário
        
        **3. Verificar a Matriz Curricular**
        
        A aba "Prévia - Matriz" mostra a organização completa do curso:
        - Componentes organizados por período/semestre
        - Linha "TOTAL DO PERÍODO" após cada semestre
        - Resumo geral no rodapé (CH Total, CH Teórica, CH Prática, CH Extensão)
        
        **4. Analisar por Núcleo**
        
        A aba "Prévia - Por Núcleo" permite:
        - Visualizar quadro-resumo de CH por semestre e núcleo
        - Ver indicadores de conformidade (verde para conforme, vermelho para não conforme)
        - Inspecionar detalhes de cada núcleo através dos expanders
        
        **5. Validar Conformidade**
        
        No painel lateral esquerdo, o sistema exibe em tempo real:
        - Carga horária total do curso
        - CH por núcleo com validação (verde/vermelho)
        - Percentuais de extensão e prática pedagógica
        - Status geral do curso
        
        Regras de validação:
        - Núcleo I: mínimo de 880h
        - Núcleo II: mínimo de 1600h
        - Núcleo III: mínimo de 320h e pelo menos 10% da CH total
        - Núcleo IV: mínimo de 400h
        - CH total do curso: mínimo de 3200h
        
        **6. Exportar Relatórios**
        
        Na aba "Exportar", você pode gerar:
        - **CSV**: Formato para migração no sistema SIGAA (UTF-8 com BOM, delimitador ponto e vírgula)
        - **XLSX**: Planilha Excel com múltiplas abas (Matriz, Por Núcleo, Componentes)
        - **PDF**: Relatório completo com matriz curricular, resumo por núcleo e conformidade
        
        Clique no botão correspondente e depois em "Download" para salvar o arquivo.
        
        **7. Consultar Regras**
        
        A aba "Regras" contém todas as informações sobre:
        - Cargas horárias mínimas por núcleo
        - Regras de percentuais
        - Associações obrigatórias
        - Campos obrigatórios por núcleo
        - Cálculo de carga horária
        - Validações automáticas
        """)
        
        st.subheader("Dicas Importantes")
        st.markdown("""
        - O sistema valida automaticamente as regras de conformidade. Preste atenção aos alertas 
        vermelhos no painel lateral e corrija os problemas antes de exportar.
        
        - Para Disciplinas, o cálculo de CH é automático (aulas semanais × 18h). Para outros tipos, 
        informe a CH total manualmente.
        
        - Componentes do tipo "Estágio" são automaticamente associados ao Núcleo IV.
        
        - Componentes com CH de Extensão maior que zero devem pertencer ao Núcleo III.
        
        - Os dados são mantidos apenas durante a sessão do navegador. Após fechar o navegador, 
        os dados são perdidos. Sempre exporte os relatórios após concluir o cadastro.
        
        - Use a visualização "Por Núcleo" para verificar se todos os núcleos estão preenchidos 
        corretamente e se atingem os mínimos exigidos.
        """)
        
        st.subheader("Ajuda Adicional")
        st.markdown("""
        Em caso de dúvidas sobre as regras e normas, consulte a aba "Regras" ou a documentação 
        oficial da Resolução CNE/CP nº 4/2024.
        
        Para problemas técnicos ou sugestões, entre em contato com a coordenação do curso ou 
        o suporte técnico da universidade.
        """)
    
    with st.sidebar:
        st.header("Validações e Resumo")
        
        if st.session_state.componentes:
            ch_total = calcular_ch_total_curso(st.session_state.componentes)
            ch_i = calcular_ch_por_nucleo(st.session_state.componentes, "I")
            ch_ii = calcular_ch_por_nucleo(st.session_state.componentes, "II")
            ch_iii = calcular_ch_por_nucleo(st.session_state.componentes, "III")
            ch_iv = calcular_ch_por_nucleo(st.session_state.componentes, "IV")
            perc_extensao = calcular_percentual_extensao(st.session_state.componentes)
            perc_pratica = calcular_percentual_pratica_pedagogica(st.session_state.componentes)
            
            st.subheader("Carga Horária Total")
            st.metric("CH Total", f"{ch_total:.0f}h", delta="≥3200h mínimo" if ch_total >= 3200 else None, delta_color="normal")
            
            st.subheader("CH por Núcleo")
            
            for nucleo in ["I", "II", "III", "IV"]:
                ch_atual = calcular_ch_por_nucleo(st.session_state.componentes, nucleo)
                ch_minima = obter_ch_minima_por_nucleo(nucleo)
                valido, mensagem = validar_ch_minima_nucleo(ch_atual, ch_minima)
                
                if valido:
                    st.success(f"**Núcleo {nucleo}**: {mensagem}")
                else:
                    st.error(f"**Núcleo {nucleo}**: {mensagem}")
            
            st.subheader("Percentuais")
            st.write(f"**Extensão:** {perc_extensao:.2f}% (mínimo 10%)")
            if perc_extensao >= 10:
                st.success("Conforme")
            else:
                st.error(f"Faltam {10 - perc_extensao:.2f}%")
            
            st.write(f"**Prática Pedagógica:** {perc_pratica:.2f}%")
            
            # Validação resumida (sem mostrar todos os erros)
            st.subheader("Status do Curso")
            resultado_validacao = validar_curso_completo(st.session_state.componentes)
            
            if resultado_validacao["valido"]:
                st.success("Curso conforme com todas as normas")
            else:
                num_erros = len(resultado_validacao["erros"])
                st.warning(f"Curso não conforme ({num_erros} problema(s) encontrado(s))")
                st.caption("Os erros serão validados na exportação")
        else:
            st.info("Adicione componentes curriculares para ver o resumo e validações.")
    
    with tab6:
        st.header("Exportar Relatórios e Backup")
        
        st.subheader("Backup e Restauração de Dados")
        st.info("**Importante**: Faça backup regularmente dos seus dados! Os dados são mantidos apenas durante a sessão do navegador. Use os botões abaixo para salvar e restaurar seus dados.")
        
        col_backup1, col_backup2 = st.columns(2)
        
        with col_backup1:
            st.markdown("**Fazer Backup (Salvar Dados)**")
            st.caption("Baixe um arquivo JSON com todos os componentes cadastrados para guardar em segurança.")
            if st.button("Exportar Backup JSON", key="btn_backup", type="primary"):
                if st.session_state.componentes:
                    backup_json = exportar_backup_json(st.session_state.componentes, st.session_state.ultimo_id)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nome_arquivo = f"backup_componentes_{timestamp}.json"
                    
                    st.success("Backup gerado com sucesso!")
                    st.download_button(
                        label="Download Backup JSON",
                        data=backup_json,
                        file_name=nome_arquivo,
                        mime="application/json",
                        key="dl_backup"
                    )
                else:
                    st.warning("Não há componentes cadastrados para fazer backup.")
        
        with col_backup2:
            st.markdown("**Restaurar Backup (Carregar Dados)**")
            st.caption("Faça upload de um arquivo JSON de backup anterior para restaurar seus dados.")
            arquivo_backup = st.file_uploader(
                "Selecione o arquivo JSON de backup",
                type=["json"],
                key="upload_backup",
                help="Selecione um arquivo de backup gerado anteriormente pelo sistema"
            )
            
            if arquivo_backup is not None:
                try:
                    conteudo = arquivo_backup.read().decode("utf-8")
                    componentes_restaurados, ultimo_id_restaurado, sucesso, mensagem = importar_backup_json(conteudo)
                    
                    if sucesso:
                        st.success(mensagem)
                        if st.button("Restaurar Dados", key="btn_restaurar", type="primary"):
                            st.session_state.componentes = componentes_restaurados
                            st.session_state.ultimo_id = ultimo_id_restaurado
                            st.success("Dados restaurados com sucesso! Os componentes foram carregados.")
                            st.rerun()
                    else:
                        st.error(mensagem)
                except Exception as e:
                    st.error(f"Erro ao processar arquivo: {str(e)}")
        
        st.markdown("---")
        st.subheader("Exportar Relatórios")
        
        if not st.session_state.componentes:
            st.warning("Adicione pelo menos um componente antes de exportar relatórios.")
            st.info("Use a aba 'Cadastrar' para adicionar componentes curriculares.")
        else:
            os.makedirs("exportacoes", exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            st.info("**Como exportar**: Clique nos botões abaixo para gerar os arquivos. Os arquivos são salvos na pasta `exportacoes/` e podem ser baixados diretamente.")
            
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                st.subheader("CSV (Migração SIGAA)")
                st.caption("Formato para importação no sistema SIGAA. Codificação UTF-8 com BOM, delimitador ponto e vírgula.")
                if st.button("Exportar CSV", key="btn_csv"):
                    caminho_csv = f"exportacoes/componentes_{timestamp}.csv"
                    exportar_csv(st.session_state.componentes, caminho_csv)
                    st.success("Arquivo CSV gerado!")
                    
                    with open(caminho_csv, "rb") as f:
                        st.download_button(
                            label="Download CSV",
                            data=f.read(),
                            file_name=f"componentes_{timestamp}.csv",
                            mime="text/csv",
                            key="dl_csv"
                        )
            
            with col_exp2:
                st.subheader("XLSX (Planilha)")
                st.caption("Planilha Excel com múltiplas abas: Matriz, Por Núcleo e Componentes. Ideal para verificação e análise.")
                if st.button("Exportar XLSX", key="btn_xlsx"):
                    caminho_xlsx = f"exportacoes/componentes_{timestamp}.xlsx"
                    exportar_xlsx(st.session_state.componentes, caminho_xlsx)
                    st.success("Arquivo XLSX gerado!")
                    
                    with open(caminho_xlsx, "rb") as f:
                        st.download_button(
                            label="Download XLSX",
                            data=f.read(),
                            file_name=f"componentes_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="dl_xlsx"
                        )
            
            with col_exp3:
                st.subheader("PDF (Relatório)")
                st.caption("Relatório completo em PDF com matriz curricular, resumo por núcleo e conformidade. Formato A4 paisagem.")
                if st.button("Gerar PDF", key="btn_pdf"):
                    caminho_pdf = f"exportacoes/relatorio_{timestamp}.pdf"
                    exportar_pdf(st.session_state.componentes, caminho_pdf)
                    st.success("Arquivo PDF gerado!")
                    
                    with open(caminho_pdf, "rb") as f:
                        st.download_button(
                            label="Download PDF",
                            data=f.read(),
                            file_name=f"relatorio_{timestamp}.pdf",
                            mime="application/pdf",
                            key="dl_pdf"
                        )
    
    with tab7:
        exibir_regras_ppc()
    
    with tab2:
        st.header("Cadastro de Componente Curricular")
        st.info("**Como preencher**: Preencha os campos obrigatórios (marcados com *). Selecione o tipo de componente e o núcleo. O sistema valida automaticamente as regras de conformidade.")
        
        if st.session_state.get("limpar_formulario", False):
            valores_limpos = st.session_state.get("valores_limpos", {})
            for key, value in valores_limpos.items():
                if key in st.session_state:
                    del st.session_state[key]
            if "limpar_formulario" in st.session_state:
                del st.session_state["limpar_formulario"]
            if "valores_limpos" in st.session_state:
                del st.session_state["valores_limpos"]
            st.rerun()
        
        for key in ["form_semestre", "form_nome", "form_tipo", "form_aulas_semanais", "form_ch_manual", 
                   "form_ch_teorica", "form_ch_pratica", "form_ch_extensao", "form_nucleo", 
                   "form_temas_nucleo_i", "form_diretrizes_nucleo_ii", "form_descricao_extensao",
                   "form_local_realizacao", "form_etapa_estagio_opcao", "form_etapa_estagio_outro",
                   "form_bloco", "form_observacoes", "form_nucleo_selecionado", "form_ch_preview"]:
            if key not in st.session_state:
                if key == "form_semestre":
                    st.session_state[key] = 1
                elif key == "form_aulas_semanais":
                    st.session_state[key] = 2  # Valor padrão para disciplinas
                elif key in ["form_ch_manual", "form_ch_teorica", 
                            "form_ch_pratica", "form_ch_extensao", "form_ch_preview"]:
                    st.session_state[key] = 0.0
                elif key == "form_temas_nucleo_i":
                    st.session_state[key] = []
                elif key in ["form_nucleo_selecionado", "form_nucleo", "form_etapa_estagio_opcao"]:
                    st.session_state[key] = ""
                else:
                    st.session_state[key] = ""
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            semestre = st.number_input(
                "Semestre *",
                min_value=1,
                max_value=20,
                step=1,
                key="form_semestre"
            )
            
            nome = st.text_input(
                "Nome do Componente *",
                placeholder="Ex: Didática Geral",
                key="form_nome"
            )
            
            tipo_index = 0
            if st.session_state.form_tipo in TIPOS_COMPONENTES:
                tipo_index = TIPOS_COMPONENTES.index(st.session_state.form_tipo)
            
            tipo = st.selectbox(
                "Tipo de Componente *",
                options=TIPOS_COMPONENTES,
                index=tipo_index,
                key="form_tipo"
            )
            
            if tipo == "Disciplina":
                aulas_semanais = st.number_input(
                    "Número de Aulas Semanais *",
                    min_value=1,
                    max_value=10,
                    step=1,
                    key="form_aulas_semanais"
                )
                ch_manual = 0
                ch_total_calc = calcular_ch_total(tipo, int(aulas_semanais))
                st.session_state.form_ch_preview = ch_total_calc
            else:
                aulas_semanais = None
                ch_manual = st.number_input(
                    "CH Total (horas) *",
                    min_value=0.0,
                    step=1.0,
                    key="form_ch_manual"
                )
                ch_total_calc = ch_manual
                st.session_state.form_ch_preview = ch_total_calc
            
            if tipo == "Estágio" and st.session_state.form_nucleo != "IV":
                st.session_state.form_nucleo = "IV"
            
            if st.session_state.form_ch_extensao > 0 and st.session_state.form_nucleo != "III":
                st.session_state.form_nucleo = "III"
            
            nucleo_index = 0
            if st.session_state.form_nucleo in ["I", "II", "III", "IV"]:
                nucleo_index = ["I", "II", "III", "IV"].index(st.session_state.form_nucleo)
            
            nucleo = st.selectbox(
                "Núcleo *",
                options=["I", "II", "III", "IV"],
                index=nucleo_index,
                key="form_nucleo"
            )
            
            atualizar_info = st.button("Atualizar Informações", type="primary", use_container_width=True)
            if atualizar_info:
                st.session_state.form_nucleo_selecionado = nucleo
                st.session_state.form_ch_preview = ch_total_calc
                st.rerun()
            
            st.markdown("---")
            st.subheader("Preview da Carga Horária")
            st.metric("CH Total do Componente", f"{st.session_state.form_ch_preview:.0f}h", 
                     delta="Disciplina: Aulas Semanais × 18h" if tipo == "Disciplina" else "CH informada manualmente",
                     delta_color="normal")
            if tipo != "Disciplina":
                st.caption("Para Disciplinas, a CH é calculada automaticamente (Aulas Semanais × 18h)")
        
        with col2:
            ch_teorica = st.number_input(
                "CH Teórica (opcional)",
                min_value=0.0,
                step=1.0,
                key="form_ch_teorica"
            )
            
            ch_pratica = st.number_input(
                "CH Prática (opcional)",
                min_value=0.0,
                step=1.0,
                key="form_ch_pratica"
            )
            
            ch_extensao = st.number_input(
                "CH Extensão (opcional)",
                min_value=0.0,
                step=1.0,
                key="form_ch_extensao",
                help="Se > 0, o componente deve pertencer ao Núcleo III"
            )
            
            if "form_faz_parte_bloco" not in st.session_state:
                st.session_state.form_faz_parte_bloco = False
            
            faz_parte_bloco = st.checkbox(
                "Faz parte de um Bloco?",
                value=st.session_state.form_faz_parte_bloco,
                key="form_faz_parte_bloco",
                help="Marque se este componente faz parte de um bloco (grupo de disciplinas/módulos)"
            )
            
            if faz_parte_bloco:
                bloco = st.text_input(
                        "Nome do Bloco *",
                        placeholder="Ex: Bloco Temático I, Módulo Integrador",
                        value=st.session_state.form_bloco if "form_bloco" in st.session_state else "",
                        key="form_bloco",
                        help="Informe o nome do bloco ao qual este componente pertence"
                    )
            else:
                bloco = ""
                if "form_bloco" in st.session_state:
                    st.session_state.form_bloco = ""
            
            observacoes = st.text_area(
                "Observações (opcional)",
                height=100,
                key="form_observacoes"
            )
        
        st.markdown("---")
        
        nucleo_atual = st.session_state.form_nucleo_selecionado if st.session_state.form_nucleo_selecionado else st.session_state.form_nucleo
        
        if nucleo_atual:
            with st.expander(f"Informações sobre o Núcleo {nucleo_atual}", expanded=True):
                st.markdown(obter_explicacao_nucleo(nucleo_atual))
        
        st.markdown("---")
        st.subheader("Campos Específicos por Núcleo")
        st.info("**Importante**: Selecione o Núcleo acima e clique em 'Atualizar Informações' para ver os campos específicos. Cada núcleo tem requisitos obrigatórios diferentes.")
        
        if nucleo_atual == "I":
            temas_nucleo_i = st.multiselect(
                "Temas do Art. 13 (selecione pelo menos um) *",
                options=TEMAS_NUCLEO_I,
                key="form_temas_nucleo_i"
            )
            diretrizes_nucleo_ii = ""
            descricao_extensao = ""
            local_realizacao = ""
            etapa_estagio = ""
        
        elif nucleo_atual == "II":
            diretrizes_nucleo_ii = st.text_area(
                "Diretrizes Específicas da Área (texto livre) *",
                height=100,
                placeholder="Descreva a vinculação com as Diretrizes da área de conhecimento específica do curso",
                key="form_diretrizes_nucleo_ii"
            )
            temas_nucleo_i = []
            descricao_extensao = ""
            local_realizacao = ""
            etapa_estagio = ""
        
        elif nucleo_atual == "III":
            descricao_extensao = st.text_area(
                "Vínculo com Projeto Extensionista *",
                height=100,
                placeholder="Descreva o vínculo do componente com o projeto de extensão",
                key="form_descricao_extensao"
            )
            temas_nucleo_i = []
            diretrizes_nucleo_ii = ""
            local_realizacao = ""
            etapa_estagio = ""
        
        elif nucleo_atual == "IV":
            local_realizacao = st.text_input(
                "Local de Realização *",
                placeholder="Ex: Escola Municipal X, Centro de Educação Infantil Y",
                key="form_local_realizacao"
            )
            etapa_opcoes = ["Observação", "Regência Parcial", "Regência Final", "Outro"]
            etapa_index = 0
            if st.session_state.form_etapa_estagio_opcao in etapa_opcoes:
                etapa_index = etapa_opcoes.index(st.session_state.form_etapa_estagio_opcao)
            
            etapa_opcao = st.selectbox(
                "Etapa do Estágio *",
                options=etapa_opcoes,
                index=etapa_index,
                key="form_etapa_estagio_opcao"
            )
            etapa_estagio = etapa_opcao
            if etapa_opcao == "Outro":
                etapa_estagio_outro = st.text_input(
                    "Especifique a etapa do estágio *",
                    placeholder="Ex: Gestão Escolar, Coordenação Pedagógica",
                    key="form_etapa_estagio_outro"
                )
                if etapa_estagio_outro:
                    etapa_estagio = etapa_estagio_outro
            temas_nucleo_i = []
            diretrizes_nucleo_ii = ""
            descricao_extensao = ""
        
        else:
            temas_nucleo_i = []
            diretrizes_nucleo_ii = ""
            descricao_extensao = ""
            local_realizacao = ""
            etapa_estagio = ""
            
        
        st.markdown("---")
        pode_adicionar = st.session_state.form_nucleo_selecionado != ""
        
        col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 2])
        with col_submit1:
            if pode_adicionar:
                submit = st.button("Adicionar Componente", type="primary", use_container_width=True)
            else:
                submit = st.button("Adicionar Componente", disabled=True, use_container_width=True, 
                                 help="Clique em 'Atualizar Informações' primeiro")
        
        if submit:
            if st.session_state.form_faz_parte_bloco and not st.session_state.form_bloco:
                st.error("Se o componente faz parte de um bloco, informe o nome do bloco.")
                st.stop()
            
            componente = {
                "semestre": st.session_state.form_semestre,
                "nome": st.session_state.form_nome,
                "tipo": st.session_state.form_tipo,
                "aulas_semanais": int(st.session_state.form_aulas_semanais) if st.session_state.form_tipo == "Disciplina" else None,
                "ch_total": st.session_state.form_ch_preview,
                "ch_teorica": st.session_state.form_ch_teorica,
                "ch_pratica": st.session_state.form_ch_pratica,
                "ch_extensao": st.session_state.form_ch_extensao,
                "nucleo": st.session_state.form_nucleo_selecionado,
                "temas_nucleo_i": temas_nucleo_i if nucleo_atual == "I" else [],
                "diretrizes_nucleo_ii": diretrizes_nucleo_ii if nucleo_atual == "II" else "",
                "descricao_extensao": descricao_extensao if nucleo_atual == "III" else "",
                "local_realizacao": local_realizacao if nucleo_atual == "IV" else "",
                "etapa_estagio": etapa_estagio if nucleo_atual == "IV" else "",
                "bloco": st.session_state.form_bloco if st.session_state.form_faz_parte_bloco else "",
                "observacoes": st.session_state.form_observacoes
            }
            
            valido, erros = validar_componente(componente)
            
            if valido:
                adicionar_componente(componente)
                st.success("Componente adicionado com sucesso!")
                valores_limpos = {
                    "form_nome": "",
                    "form_tipo": "",
                    "form_aulas_semanais": 0.0,
                    "form_ch_manual": 0.0,
                    "form_ch_teorica": 0.0,
                    "form_ch_pratica": 0.0,
                    "form_ch_extensao": 0.0,
                    "form_nucleo": "",
                    "form_temas_nucleo_i": [],
                    "form_diretrizes_nucleo_ii": "",
                    "form_descricao_extensao": "",
                    "form_local_realizacao": "",
                    "form_etapa_estagio_opcao": "",
                    "form_etapa_estagio_outro": "",
                    "form_bloco": "",
                    "form_faz_parte_bloco": False,
                    "form_observacoes": "",
                    "form_nucleo_selecionado": "",
                    "form_ch_preview": 0.0
                }
                st.session_state["limpar_formulario"] = True
                st.session_state["valores_limpos"] = valores_limpos
                st.rerun()
            else:
                st.error("Erros de validação:")
                for erro in erros:
                    st.error(f"• {erro}")
    
    with tab3:
        st.header("Componentes Cadastrados")
        st.info("**Como usar**: Visualize todos os componentes cadastrados. Use o botão de remover para excluir componentes. O resumo mostra a distribuição de carga horária por semestre e núcleo.")
        
        if st.session_state.componentes:
            st.subheader("Resumo por Semestre e Núcleo")
            df_resumo = gerar_resumo_por_semestre_nucleo(st.session_state.componentes)
            st.dataframe(df_resumo, width='stretch', hide_index=True)
            
            st.markdown("---")
            st.subheader("Lista de Componentes")
            
            dados_tabela = []
            for comp in st.session_state.componentes:
                linha = {
                    "ID": comp.get("id"),
                    "Semestre": comp.get("semestre"),
                    "Nome": comp.get("nome"),
                    "Tipo": comp.get("tipo"),
                    "CH Total": f"{comp.get('ch_total', 0):.0f}h",
                    "Núcleo": comp.get("nucleo"),
                    "Ações": comp.get("id")
                }
                dados_tabela.append(linha)
            
            df_componentes = pd.DataFrame(dados_tabela)
            
            for idx, row in df_componentes.iterrows():
                with st.container():
                    col_info, col_action = st.columns([6, 1])
                    with col_info:
                        st.write(f"**{row['Nome']}** ({row['Tipo']}) - Semestre {row['Semestre']} - Núcleo {row['Núcleo']} - {row['CH Total']}")
                    with col_action:
                        if st.button("Remover", key=f"remover_{row['ID']}", help="Remover componente"):
                            remover_componente(row['ID'])
                            st.rerun()
                    st.divider()
            
            st.caption(f"Total de componentes cadastrados: {len(st.session_state.componentes)}")
        else:
            st.info("Nenhum componente cadastrado. Use a aba 'Cadastrar Componente' para adicionar o primeiro.")
    
    with tab4:
        st.header("Prévia - Matriz Curricular por Período")
        
        if not st.session_state.componentes:
            st.info("**Nenhum componente cadastrado.** Use a aba 'Cadastrar' para adicionar componentes curriculares.")
            st.info("**Como usar**: Esta visualização mostra a matriz curricular organizada por período/semestre, com linha TOTAL por período.")
        else:
            st.info("**Como interpretar**: Esta matriz mostra todos os componentes organizados por período. A linha 'TOTAL DO PERÍODO' indica a carga horária total de cada semestre.")
            
            df_matriz = gerar_matriz_por_periodo(st.session_state.componentes)
            
            st.subheader("Matriz Curricular")
            st.dataframe(
                df_matriz,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Semestre": st.column_config.TextColumn("Período", width="small"),
                    "Nome": st.column_config.TextColumn("Nome do Componente", width="large"),
                    "Tipo": st.column_config.TextColumn("Tipo", width="small"),
                    "CH Semanal": st.column_config.NumberColumn("CH Semanal", width="small", format="%d"),
                    "CH Teórica": st.column_config.NumberColumn("CH Teórica", width="small", format="%.0fh"),
                    "CH Prática": st.column_config.NumberColumn("CH Prática", width="small", format="%.0fh"),
                    "CH Extensão": st.column_config.NumberColumn("CH Extensão", width="small", format="%.0fh"),
                    "CH Total": st.column_config.NumberColumn("CH Total", width="small", format="%.0fh"),
                    "Núcleo": st.column_config.TextColumn("Núcleo", width="small")
                }
            )
            
            ch_total_curso = calcular_ch_total_curso(st.session_state.componentes)
            ch_teorica_total = sum(c.get("ch_teorica", 0) for c in st.session_state.componentes)
            ch_pratica_total = sum(c.get("ch_pratica", 0) for c in st.session_state.componentes)
            ch_extensao_total = sum(c.get("ch_extensao", 0) for c in st.session_state.componentes)
            
            st.markdown("---")
            st.subheader("Resumo Geral do Curso")
            
            col_res1, col_res2, col_res3, col_res4 = st.columns(4)
            with col_res1:
                st.metric("CH Total do Curso", f"{ch_total_curso:.0f}h", delta="≥3200h mínimo", delta_color="normal")
            with col_res2:
                st.metric("CH Teórica Total", f"{ch_teorica_total:.0f}h")
            with col_res3:
                st.metric("CH Prática Total", f"{ch_pratica_total:.0f}h")
            with col_res4:
                st.metric("CH Extensão Total", f"{ch_extensao_total:.0f}h")
            
            componentes_globais = [c for c in st.session_state.componentes if c.get("tipo") in ["TCC", "Extensão"] and not c.get("semestre")]
            if componentes_globais:
                st.markdown("---")
                st.subheader("Componentes Globais (não vinculados a período)")
                for comp in componentes_globais:
                    st.write(f"**{comp.get('nome')}** ({comp.get('tipo')}) - {comp.get('ch_total', 0):.0f}h - Núcleo {comp.get('nucleo')}")
    
    with tab5:
        st.header("Prévia - Visão por Núcleo Curricular")
        
        if not st.session_state.componentes:
            st.info("**Nenhum componente cadastrado.** Use a aba 'Cadastrar' para adicionar componentes curriculares.")
            st.info("**Como usar**: Esta visualização mostra o quadro-resumo de carga horária por semestre e núcleo, além de listas de componentes agrupados por núcleo.")
        else:
            st.info("**Como interpretar**: O quadro mostra a distribuição de carga horária por período e núcleo. Use os expanders abaixo para ver detalhes de cada núcleo.")
            
            st.subheader("Quadro-Resumo: CH por Semestre e Núcleo")
            df_resumo = gerar_resumo_por_semestre_nucleo(st.session_state.componentes)
            st.dataframe(
                df_resumo,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Semestre": st.column_config.TextColumn("Semestre", width="medium"),
                    "CH Núc. I": st.column_config.NumberColumn("CH Núcleo I", width="medium", format="%.0fh"),
                    "CH Núc. II": st.column_config.NumberColumn("CH Núcleo II", width="medium", format="%.0fh"),
                    "CH Núc. III": st.column_config.NumberColumn("CH Núcleo III", width="medium", format="%.0fh"),
                    "CH Núc. IV": st.column_config.NumberColumn("CH Núcleo IV", width="medium", format="%.0fh"),
                    "Total": st.column_config.NumberColumn("Total Período", width="medium", format="%.0fh")
                }
            )
            
            st.markdown("---")
            st.subheader("Indicadores de Conformidade")
            
            ch_i = calcular_ch_por_nucleo(st.session_state.componentes, "I")
            ch_ii = calcular_ch_por_nucleo(st.session_state.componentes, "II")
            ch_iii = calcular_ch_por_nucleo(st.session_state.componentes, "III")
            ch_iv = calcular_ch_por_nucleo(st.session_state.componentes, "IV")
            ch_total = calcular_ch_total_curso(st.session_state.componentes)
            perc_extensao = calcular_percentual_extensao(st.session_state.componentes)
            perc_pratica = calcular_percentual_pratica_pedagogica(st.session_state.componentes)
            
            col_conf1, col_conf2, col_conf3, col_conf4 = st.columns(4)
            
            with col_conf1:
                valido_i, msg_i = validar_ch_minima_nucleo(ch_i, obter_ch_minima_por_nucleo("I"))
                if valido_i:
                    st.success(f"**Núcleo I**: {ch_i:.0f}h (Conforme)")
                else:
                    st.error(f"**Núcleo I**: {ch_i:.0f}h (Não conforme)")
            
            with col_conf2:
                valido_ii, msg_ii = validar_ch_minima_nucleo(ch_ii, obter_ch_minima_por_nucleo("II"))
                if valido_ii:
                    st.success(f"**Núcleo II**: {ch_ii:.0f}h (Conforme)")
                else:
                    st.error(f"**Núcleo II**: {ch_ii:.0f}h (Não conforme)")
            
            with col_conf3:
                valido_iii, msg_iii = validar_ch_minima_nucleo(ch_iii, obter_ch_minima_por_nucleo("III"))
                if valido_iii:
                    st.success(f"**Núcleo III**: {ch_iii:.0f}h (Conforme)")
                else:
                    st.error(f"**Núcleo III**: {ch_iii:.0f}h (Não conforme)")
            
            with col_conf4:
                valido_iv, msg_iv = validar_ch_minima_nucleo(ch_iv, obter_ch_minima_por_nucleo("IV"))
                if valido_iv:
                    st.success(f"**Núcleo IV**: {ch_iv:.0f}h (Conforme)")
                else:
                    st.error(f"**Núcleo IV**: {ch_iv:.0f}h (Não conforme)")
            
            st.markdown("---")
            st.write(f"**CH Total do Curso**: {ch_total:.0f}h ({'Conforme' if ch_total >= 3200 else 'Não conforme'}) - mínimo: 3200h")
            st.write(f"**Percentual de Extensão**: {perc_extensao:.2f}% ({'Conforme' if perc_extensao >= 10 else 'Não conforme'}) - mínimo: 10%")
            st.write(f"**Percentual de Prática Pedagógica**: {perc_pratica:.2f}%")
            
            st.markdown("---")
            st.subheader("Componentes por Núcleo")
            
            for nucleo in ["I", "II", "III", "IV"]:
                componentes_nucleo = [c for c in st.session_state.componentes if c.get("nucleo") == nucleo]
                ch_nucleo = calcular_ch_por_nucleo(st.session_state.componentes, nucleo)
                ch_minima = obter_ch_minima_por_nucleo(nucleo)
                valido, _ = validar_ch_minima_nucleo(ch_nucleo, ch_minima)
                
                with st.expander(f"**Núcleo {nucleo}** - {ch_nucleo:.0f}h / {ch_minima:.0f}h mínimo ({'Conforme' if valido else 'Não conforme'})", expanded=False):
                    if componentes_nucleo:
                        for comp in sorted(componentes_nucleo, key=lambda x: (x.get("semestre", 0), x.get("nome", ""))):
                            st.write(f"- **{comp.get('nome')}** - Semestre {comp.get('semestre')} - {comp.get('ch_total', 0):.0f}h - {comp.get('tipo')}")
                            if nucleo == "I" and comp.get("temas_nucleo_i"):
                                st.caption(f"  Temas: {', '.join([t.split(')')[0] + ')' for t in comp.get('temas_nucleo_i', [])])}")
                            elif nucleo == "III" and comp.get("descricao_extensao"):
                                st.caption(f"  Extensão: {comp.get('descricao_extensao')[:100]}...")
                            elif nucleo == "IV" and comp.get("local_realizacao"):
                                st.caption(f"  Local: {comp.get('local_realizacao')} - Etapa: {comp.get('etapa_estagio')}")
                    else:
                        st.info(f"Nenhum componente cadastrado no Núcleo {nucleo}.")


if __name__ == "__main__":
    main()










