# Sistema de Componentes Curriculares

Sistema web para cadastro, validação e organização de componentes curriculares de cursos de Licenciatura, desenvolvido para auxiliar professores e coordenadores de curso na construção de Projetos Pedagógicos de Curso (PPC) conforme a Resolução CNE/CP nº 4/2024.

## Sobre o Sistema

O Sistema de Componentes Curriculares foi desenvolvido pela equipe de bolsistas de Computação da PROGRAD/UFAL para facilitar o processo de estruturação curricular de cursos de Licenciatura. O sistema oferece uma interface intuitiva para cadastro de componentes, validação automática de conformidade com as normas, visualização da matriz curricular organizada e exportação de relatórios.

## Funcionalidades Principais

### Cadastro de Componentes
- Formulário intuitivo para registro de disciplinas, módulos, estágios, TCC, extensão e outros componentes
- Cálculo automático de carga horária para disciplinas (aulas semanais × 18h)
- Validação em tempo real de campos obrigatórios e regras específicas por núcleo

### Validações Automáticas
- Validação de carga horária mínima por núcleo (I: 880h, II: 1600h, III: 320h, IV: 400h)
- Verificação de CH total do curso (mínimo 3200h)
- Validação de percentual de extensão (mínimo 10%)
- Alertas visuais de conformidade (verde/vermelho)

### Visualizações
- **Matriz Curricular**: Organização completa por período/semestre com totais por período
- **Visão por Núcleo**: Quadro-resumo de CH por semestre e núcleo, com detalhamento por componente
- **Componentes Cadastrados**: Lista completa com opção de remoção

### Exportações
- **CSV**: Formato para migração no sistema SIGAA (UTF-8 com BOM, delimitador ponto e vírgula)
- **XLSX**: Planilha Excel com múltiplas abas (Matriz, Por Núcleo, Componentes)
- **PDF**: Relatório completo com matriz curricular, resumo por núcleo e conformidade

## Estrutura dos Núcleos Curriculares

O sistema organiza os componentes em quatro núcleos obrigatórios conforme a Resolução CNE/CP nº 4/2024:

- **Núcleo I - Formação Pedagógica**: Mínimo de 880h. Exige seleção de pelo menos um tema do Art. 13 (a-i).
- **Núcleo II - Formação Específica da Área**: Mínimo de 1600h. Exige indicação de vinculação com Diretrizes da área.
- **Núcleo III - Atividades de Extensão**: Mínimo de 320h e pelo menos 10% da CH total. Exige vínculo com projeto extensionista.
- **Núcleo IV - Estágios Supervisionados**: Mínimo de 400h. Exige local de realização e etapa do estágio.

## Como Usar

O sistema oferece uma aba "Como Usar" com instruções detalhadas passo a passo sobre como criar um PPC utilizando a plataforma. Consulte essa aba no próprio sistema para obter orientações completas sobre o processo de cadastro e validação.

## Tecnologias Utilizadas

- **Streamlit**: Framework web para interface interativa
- **Pandas**: Manipulação e análise de dados
- **OpenPyXL**: Geração de arquivos Excel
- **ReportLab**: Geração de relatórios em PDF
- **Python 3.8+**: Linguagem de programação

## Base Legal

Este sistema foi desenvolvido com base na Resolução CNE/CP nº 4/2024, que estabelece as Diretrizes Curriculares Nacionais para os cursos de licenciatura.

## Estrutura do Projeto

```
projeto_curriculo/
├── app.py                 # Aplicação principal Streamlit
├── requirements.txt       # Dependências do projeto
├── README.md             # Este arquivo
├── assets/               # Recursos visuais (logos, imagens)
├── utils/                # Módulos auxiliares
│   ├── __init__.py
│   ├── calculos.py       # Funções de cálculo de CH
│   ├── validacoes.py     # Funções de validação
│   └── exportacoes.py    # Funções de exportação (CSV, XLSX, PDF)
└── exportacoes/          # Diretório onde os arquivos exportados são salvos
```

## Notas Importantes

### ⚠️ Backup Manual Obrigatório

**IMPORTANTE**: O sistema **não salva seus dados automaticamente**. Todos os dados são mantidos apenas durante a sessão do navegador. 

**Recomendação**: Sempre realize o backup manual dos seus dados na aba "Exportar" após cadastrar componentes. Caso feche o site sem fazer backup, os dados serão perdidos e não poderão ser restaurados.

## Público-Alvo

Professores e coordenadores de curso universitário que precisam:
- Cadastrar componentes curriculares de forma organizada
- Validar conformidade com normas acadêmicas
- Gerar relatórios para documentação e migração de sistemas

## Contribuindo

Este é um projeto acadêmico desenvolvido para uso institucional. Para sugestões ou melhorias, entre em contato com a coordenação responsável.

## Licença

Este projeto é destinado ao uso acadêmico e institucional da Universidade Federal de Alagoas.

## Contato

Para dúvidas ou suporte, entre em contato com a coordenação do curso ou o suporte técnico da universidade.

