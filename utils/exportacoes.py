"""
Módulo de exportações para componentes curriculares.
Responsável por gerar arquivos CSV, XLSX e PDF.
"""

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def exportar_csv(componentes: list, caminho_arquivo: str, tabela: str = "componentes") -> str:
    """
    Exporta dados para CSV, permitindo escolher qual tabela será gerada.
    
    Args:
        componentes: Lista de dicionários com os componentes
        caminho_arquivo: Caminho onde o arquivo será salvo
        tabela: Nome da tabela desejada (componentes, matriz, resumo_nucleo)
    
    Returns:
        Caminho do arquivo salvo
    """
    tabela_normalizada = (tabela or "componentes").lower()
    
    if tabela_normalizada == "matriz":
        df = gerar_matriz_por_periodo(componentes)
    elif tabela_normalizada in {"resumo", "resumo_nucleo", "por_nucleo"}:
        df = gerar_resumo_por_semestre_nucleo(componentes)
    else:
        dados_csv = []
        for comp in componentes:
            linha = {
                "Semestre": comp.get("semestre", ""),
                "Nome": comp.get("nome", ""),
                "Tipo": comp.get("tipo", ""),
                "Aulas Semanais": comp.get("aulas_semanais", ""),
                "CH Total": comp.get("ch_total", ""),
                "CH Teórica": comp.get("ch_teorica", ""),
                "CH Prática": comp.get("ch_pratica", ""),
                "CH Extensão": comp.get("ch_extensao", ""),
                "Núcleo": comp.get("nucleo", ""),
                "Temas Núcleo I": "; ".join(comp.get("temas_nucleo_i", [])) if comp.get("temas_nucleo_i") else "",
                "Diretrizes Núcleo II": comp.get("diretrizes_nucleo_ii", ""),
                "Descrição Extensão": comp.get("descricao_extensao", ""),
                "Local Realização": comp.get("local_realizacao", ""),
                "Etapa Estágio": comp.get("etapa_estagio", ""),
                "Bloco": comp.get("bloco", ""),
                "Observações": comp.get("observacoes", "")
            }
            dados_csv.append(linha)
        df = pd.DataFrame(dados_csv)
    
    df.to_csv(caminho_arquivo, index=False, encoding="utf-8-sig", sep=";")
    
    return caminho_arquivo


def exportar_xlsx(componentes: list, caminho_arquivo: str, abas: list[str] | None = None) -> str:
    """
    Exporta dados para arquivo XLSX, permitindo selecionar quais abas devem ser geradas.
    
    Args:
        componentes: Lista de dicionários com os componentes
        caminho_arquivo: Caminho onde o arquivo será salvo
        abas: Lista de abas desejadas (matriz, resumo_nucleo, componentes)
    
    Returns:
        Caminho do arquivo salvo
    """
    from openpyxl.utils import get_column_letter
    
    abas_padrao = ["matriz", "resumo_nucleo", "componentes"]
    abas_normalizadas = [aba.lower() for aba in (abas or abas_padrao) if aba]
    
    if not abas_normalizadas:
        raise ValueError("Selecione ao menos uma aba para exportação.")
    
    with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
        if "matriz" in abas_normalizadas:
            df_matriz = gerar_matriz_por_periodo(componentes)
            df_matriz.to_excel(writer, sheet_name="Matriz", index=False)
            worksheet_matriz = writer.sheets["Matriz"]
            for idx, col in enumerate(df_matriz.columns, 1):
                max_length = max(
                    df_matriz[col].astype(str).apply(len).max() if len(df_matriz) > 0 else 0,
                    len(col)
                )
                col_letter = get_column_letter(idx)
                worksheet_matriz.column_dimensions[col_letter].width = min(max_length + 2, 50)
        
        if "resumo_nucleo" in abas_normalizadas or "por_nucleo" in abas_normalizadas:
            df_nucleo = gerar_resumo_por_semestre_nucleo(componentes)
            df_nucleo.to_excel(writer, sheet_name="Por Núcleo", index=False)
            worksheet_nucleo = writer.sheets["Por Núcleo"]
            for idx, col in enumerate(df_nucleo.columns, 1):
                max_length = max(
                    df_nucleo[col].astype(str).apply(len).max() if len(df_nucleo) > 0 else 0,
                    len(col)
                )
                col_letter = get_column_letter(idx)
                worksheet_nucleo.column_dimensions[col_letter].width = min(max_length + 2, 50)
        
        if "componentes" in abas_normalizadas:
            dados_componentes = []
            for comp in componentes:
                linha = {
                    "Semestre": comp.get("semestre", ""),
                    "Nome": comp.get("nome", ""),
                    "Tipo": comp.get("tipo", ""),
                    "Aulas Semanais": comp.get("aulas_semanais", ""),
                    "CH Total": comp.get("ch_total", ""),
                    "CH Teórica": comp.get("ch_teorica", ""),
                    "CH Prática": comp.get("ch_pratica", ""),
                    "CH Extensão": comp.get("ch_extensao", ""),
                    "Núcleo": comp.get("nucleo", ""),
                    "Temas Núcleo I": "; ".join(comp.get("temas_nucleo_i", [])) if comp.get("temas_nucleo_i") else "",
                    "Diretrizes Núcleo II": comp.get("diretrizes_nucleo_ii", ""),
                    "Descrição Extensão": comp.get("descricao_extensao", ""),
                    "Local Realização": comp.get("local_realizacao", ""),
                    "Etapa Estágio": comp.get("etapa_estagio", ""),
                    "Bloco": comp.get("bloco", ""),
                    "Observações": comp.get("observacoes", "")
                }
                dados_componentes.append(linha)
            
            df_componentes = pd.DataFrame(dados_componentes)
            df_componentes.to_excel(writer, sheet_name="Componentes", index=False)
            worksheet_comp = writer.sheets["Componentes"]
            for idx, col in enumerate(df_componentes.columns, 1):
                max_length = max(
                    df_componentes[col].astype(str).apply(len).max() if len(df_componentes) > 0 else 0,
                    len(col)
                )
                col_letter = get_column_letter(idx)
                worksheet_comp.column_dimensions[col_letter].width = min(max_length + 2, 50)
    
    return caminho_arquivo


def gerar_matriz_por_periodo(componentes: list) -> pd.DataFrame:
    """
    Gera a matriz curricular principal organizada por período/semestre.
    Inclui componentes, linha TOTAL por período e prepara rodapé.
    
    Args:
        componentes: Lista de dicionários com os componentes
    
    Returns:
        DataFrame com matriz por período (colunas: Nome, CH Semanal, CH Teórica, CH Prática, CH Extensão, CH Total)
    """
    # Ordenar componentes por semestre
    componentes_ordenados = sorted(componentes, key=lambda x: (x.get("semestre", 0), x.get("nome", "")))
    
    dados_matriz = []
    
    # Agrupar por semestre
    semestre_atual = None
    for comp in componentes_ordenados:
        semestre = comp.get("semestre", 0)
        
        # Se mudou de semestre, adicionar linha TOTAL do semestre anterior
        if semestre_atual is not None and semestre != semestre_atual:
            # Calcular totais do semestre anterior
            comps_sem_anterior = [c for c in componentes_ordenados if c.get("semestre") == semestre_atual]
            ch_total_sem = sum(c.get("ch_total", 0) for c in comps_sem_anterior)
            ch_teorica_sem = sum(c.get("ch_teorica", 0) for c in comps_sem_anterior)
            ch_pratica_sem = sum(c.get("ch_pratica", 0) for c in comps_sem_anterior)
            ch_extensao_sem = sum(c.get("ch_extensao", 0) for c in comps_sem_anterior)
            
            # Adicionar linha TOTAL
            dados_matriz.append({
                "Semestre": f"{semestre_atual}",
                "Nome": "TOTAL DO PERÍODO",
                "Tipo": "",
                "CH Semanal": "",
                "CH Teórica": ch_teorica_sem,
                "CH Prática": ch_pratica_sem,
                "CH Extensão": ch_extensao_sem,
                "CH Total": ch_total_sem,
                "Núcleo": ""
            })
        
        # Adicionar componente
        aulas_semanais_val = comp.get("aulas_semanais", "")
        if aulas_semanais_val == "" or aulas_semanais_val is None:
            aulas_semanais_display = ""
        else:
            try:
                aulas_semanais_display = int(aulas_semanais_val) if isinstance(aulas_semanais_val, (int, float)) else ""
            except:
                aulas_semanais_display = ""
        
        dados_matriz.append({
            "Semestre": f"{semestre}",
            "Nome": comp.get("nome", ""),
            "Tipo": comp.get("tipo", ""),
            "CH Semanal": aulas_semanais_display,
            "CH Teórica": comp.get("ch_teorica", 0),
            "CH Prática": comp.get("ch_pratica", 0),
            "CH Extensão": comp.get("ch_extensao", 0),
            "CH Total": comp.get("ch_total", 0),
            "Núcleo": comp.get("nucleo", "")
        })
        
        semestre_atual = semestre
    
    # Adicionar linha TOTAL do último semestre
    if semestre_atual is not None:
        comps_sem = [c for c in componentes_ordenados if c.get("semestre") == semestre_atual]
        if comps_sem:
            ch_total_sem = sum(c.get("ch_total", 0) for c in comps_sem)
            ch_teorica_sem = sum(c.get("ch_teorica", 0) for c in comps_sem)
            ch_pratica_sem = sum(c.get("ch_pratica", 0) for c in comps_sem)
            ch_extensao_sem = sum(c.get("ch_extensao", 0) for c in comps_sem)
            
            dados_matriz.append({
                "Semestre": f"{semestre_atual}",
                "Nome": "TOTAL DO PERÍODO",
                "Tipo": "",
                "CH Semanal": "",
                "CH Teórica": ch_teorica_sem,
                "CH Prática": ch_pratica_sem,
                "CH Extensão": ch_extensao_sem,
                "CH Total": ch_total_sem,
                "Núcleo": ""
            })
    
    return pd.DataFrame(dados_matriz)


def gerar_resumo_por_semestre_nucleo(componentes: list) -> pd.DataFrame:
    """
    Gera um resumo da carga horária por semestre e núcleo.
    
    Args:
        componentes: Lista de dicionários com os componentes
    
    Returns:
        DataFrame com resumo por semestre e núcleo
    """
    from utils.calculos import calcular_ch_por_nucleo
    
    # Obter todos os semestres únicos
    semestres = sorted(set(comp.get("semestre", 0) for comp in componentes if comp.get("semestre")))
    
    dados_resumo = []
    
    for semestre in semestres:
        # Filtrar componentes do semestre
        comps_semestre = [c for c in componentes if c.get("semestre") == semestre]
        
        # Calcular CH por núcleo neste semestre
        ch_i = sum(c.get("ch_total", 0) for c in comps_semestre if c.get("nucleo") == "I")
        ch_ii = sum(c.get("ch_total", 0) for c in comps_semestre if c.get("nucleo") == "II")
        ch_iii = sum(c.get("ch_total", 0) for c in comps_semestre if c.get("nucleo") == "III")
        ch_iv = sum(c.get("ch_total", 0) for c in comps_semestre if c.get("nucleo") == "IV")
        ch_total_semestre = ch_i + ch_ii + ch_iii + ch_iv
        
        dados_resumo.append({
            "Semestre": str(semestre),  # Converter para string para evitar conflito de tipos
            "CH Núc. I": ch_i,
            "CH Núc. II": ch_ii,
            "CH Núc. III": ch_iii,
            "CH Núc. IV": ch_iv,
            "Total": ch_total_semestre
        })
    
    # Linha de totais
    if dados_resumo:
        total_i = sum(r["CH Núc. I"] for r in dados_resumo)
        total_ii = sum(r["CH Núc. II"] for r in dados_resumo)
        total_iii = sum(r["CH Núc. III"] for r in dados_resumo)
        total_iv = sum(r["CH Núc. IV"] for r in dados_resumo)
        total_geral = sum(r["Total"] for r in dados_resumo)
        
        dados_resumo.append({
            "Semestre": "TOTAL",
            "CH Núc. I": total_i,
            "CH Núc. II": total_ii,
            "CH Núc. III": total_iii,
            "CH Núc. IV": total_iv,
            "Total": total_geral
        })
    
    return pd.DataFrame(dados_resumo)


def _agrupar_componentes_por_semestre(componentes: list) -> list[dict]:
    """
    Agrupa componentes por semestre, ordenando e calculando totais auxiliares.
    """
    grupos: dict[int | str, list[dict]] = {}
    
    for comp in componentes:
        semestre_val = comp.get("semestre")
        if isinstance(semestre_val, (int, float)) and semestre_val > 0:
            chave = int(semestre_val)
        else:
            chave = "Sem período"
        grupos.setdefault(chave, []).append(comp)
    
    resultado = []
    for chave in sorted(grupos, key=lambda c: (9999 if isinstance(c, str) else c, c)):
        componentes_semestre = sorted(grupos[chave], key=lambda x: (x.get("nome") or "").lower())
        ch_total = sum(c.get("ch_total", 0) for c in componentes_semestre)
        ch_teorica = sum(c.get("ch_teorica", 0) for c in componentes_semestre)
        ch_pratica = sum(c.get("ch_pratica", 0) for c in componentes_semestre)
        ch_extensao = sum(c.get("ch_extensao", 0) for c in componentes_semestre)
        resultado.append({
            "rotulo": str(chave),
            "componentes": componentes_semestre,
            "totais": {
                "ch_total": ch_total,
                "ch_teorica": ch_teorica,
                "ch_pratica": ch_pratica,
                "ch_extensao": ch_extensao
            }
        })
    return resultado


def _formatar_carga_horaria(valor: float | int | str | None) -> str:
    if valor in (None, "", 0):
        return ""
    try:
        return f"{float(valor):.0f}h"
    except (ValueError, TypeError):
        return str(valor)


def _formatar_aulas_semanais(valor: float | int | None) -> str:
    if isinstance(valor, (int, float)) and valor > 0:
        return f"{int(valor)}"
    return ""


def exportar_pdf(componentes: list, caminho_arquivo: str, secoes: list[str] | None = None) -> str:
    """
    Exporta um relatório em PDF configurável, com possibilidade de escolher seções.
    
    Args:
        componentes: Lista de dicionários com os componentes
        caminho_arquivo: Caminho onde o arquivo será salvo
        secoes: Lista de seções desejadas (matriz, resumo_nucleo, resumo_geral, conformidade)
    
    Returns:
        Caminho do arquivo salvo
    """
    from utils.calculos import (
        calcular_ch_total_curso,
        calcular_ch_por_nucleo,
        calcular_percentual_extensao,
        calcular_percentual_pratica_pedagogica,
        obter_ch_minima_por_nucleo,
        validar_ch_minima_nucleo
    )
    from utils.validacoes import validar_curso_completo
    
    secoes_padrao = ["matriz", "resumo_nucleo", "resumo_geral", "conformidade"]
    secoes_normalizadas = [sec.lower() for sec in (secoes or secoes_padrao) if sec]
    
    if not secoes_normalizadas:
        raise ValueError("Selecione ao menos uma seção para exportação.")
    
    doc = SimpleDocTemplate(
        caminho_arquivo,
        pagesize=A4,
        leftMargin=1.4 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.4 * cm
    )
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#0B5FA5'),
        spaceAfter=18,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#0B5FA5'),
        spaceAfter=10,
        leading=14
    )
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#1F2A37'),
        spaceAfter=6,
        leading=13
    )
    table_text_style = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_LEFT
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.whitesmoke
    )
    
    story.append(Paragraph("Relatório de Carga Horária - Componentes Curriculares", title_style))
    story.append(Spacer(1, 0.25 * cm))
    
    if "matriz" in secoes_normalizadas:
        story.append(Paragraph("Matriz Curricular por Período", heading_style))
        for bloco in _agrupar_componentes_por_semestre(componentes):
            story.append(Paragraph(f"Período {bloco['rotulo']}", subheading_style))
            dados_tabela = [
                ["", Paragraph("Nome do Componente", table_header_style), Paragraph("Tipo", table_header_style),
                 Paragraph("CH Semanal", table_header_style), Paragraph("CH Teórica", table_header_style),
                 Paragraph("CH Prática", table_header_style), Paragraph("CH Extensão", table_header_style),
                 Paragraph("CH Total", table_header_style)]
            ]
            
            for comp in bloco["componentes"]:
                dados_tabela.append([
                    "",
                    Paragraph(comp.get("nome", "") or "-", table_text_style),
                    Paragraph(comp.get("tipo", "") or "-", table_text_style),
                    _formatar_aulas_semanais(comp.get("aulas_semanais")),
                    _formatar_carga_horaria(comp.get("ch_teorica")),
                    _formatar_carga_horaria(comp.get("ch_pratica")),
                    _formatar_carga_horaria(comp.get("ch_extensao")),
                    _formatar_carga_horaria(comp.get("ch_total"))
                ])
            
            totais = bloco["totais"]
            dados_tabela.append([
                "",
                Paragraph("<b>TOTAL DO PERÍODO</b>", table_text_style),
                "",
                "",
                _formatar_carga_horaria(totais["ch_teorica"]),
                _formatar_carga_horaria(totais["ch_pratica"]),
                _formatar_carga_horaria(totais["ch_extensao"]),
                _formatar_carga_horaria(totais["ch_total"])
            ])
            
            tabela_matriz = Table(
                dados_tabela,
                repeatRows=1,
                colWidths=[0.4 * cm, 7.2 * cm, 2.2 * cm, 1.6 * cm, 1.6 * cm, 1.6 * cm, 1.6 * cm, 1.8 * cm]
            )
            tabela_matriz.setStyle(TableStyle([
                ('BACKGROUND', (1, 0), (-1, 0), colors.HexColor('#0B5FA5')),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#DDE7F5')),
                ('TEXTCOLOR', (1, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -2), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (1, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (1, 1), (-1, -2), [colors.white, colors.HexColor('#F6F8FC')]),
                ('BACKGROUND', (1, -1), (-1, -1), colors.HexColor('#E5EDF9')),
                ('LINEBEFORE', (0, 0), (0, -1), 3, colors.HexColor('#0B5FA5')),
                ('GRID', (1, 0), (-1, -1), 0.5, colors.HexColor('#B5C6E0')),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            story.append(tabela_matriz)
            story.append(Spacer(1, 0.35 * cm))
    
    if "resumo_nucleo" in secoes_normalizadas or "por_nucleo" in secoes_normalizadas:
        story.append(Paragraph("Quadro-Resumo: CH por Semestre e Núcleo", heading_style))
        df_resumo = gerar_resumo_por_semestre_nucleo(componentes)
        dados_resumo = [list(df_resumo.columns)]
        for _, row in df_resumo.iterrows():
            dados_resumo.append([
                str(row["Semestre"]),
                _formatar_carga_horaria(row["CH Núc. I"]),
                _formatar_carga_horaria(row["CH Núc. II"]),
                _formatar_carga_horaria(row["CH Núc. III"]),
                _formatar_carga_horaria(row["CH Núc. IV"]),
                _formatar_carga_horaria(row["Total"])
            ])
        
        tabela_resumo_nucleo = Table(
            dados_resumo,
            repeatRows=1,
            colWidths=[2.5 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm]
        )
        tabela_resumo_nucleo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B5FA5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F6F8FC')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E5EDF9')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#B5C6E0')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(tabela_resumo_nucleo)
        story.append(Spacer(1, 0.35 * cm))
    
    if "resumo_geral" in secoes_normalizadas:
        story.append(Paragraph("Resumo Geral do Curso", heading_style))
        ch_total = calcular_ch_total_curso(componentes)
        ch_i = calcular_ch_por_nucleo(componentes, "I")
        ch_ii = calcular_ch_por_nucleo(componentes, "II")
        ch_iii = calcular_ch_por_nucleo(componentes, "III")
        ch_iv = calcular_ch_por_nucleo(componentes, "IV")
        perc_extensao = calcular_percentual_extensao(componentes)
        perc_pratica = calcular_percentual_pratica_pedagogica(componentes)
        
        resumo_geral = [
            ["Carga Horária Total do Curso", _formatar_carga_horaria(ch_total)],
            ["CH Núcleo I", _formatar_carga_horaria(ch_i)],
            ["CH Núcleo II", _formatar_carga_horaria(ch_ii)],
            ["CH Núcleo III", _formatar_carga_horaria(ch_iii)],
            ["CH Núcleo IV", _formatar_carga_horaria(ch_iv)],
            ["Percentual de Extensão", f"{perc_extensao:.2f}%"],
            ["Percentual de Prática Pedagógica", f"{perc_pratica:.2f}%"]
        ]
        
        tabela_resumo = Table(resumo_geral, colWidths=[9.0 * cm, 5.0 * cm])
        tabela_resumo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B5FA5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#B5C6E0')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(tabela_resumo)
        story.append(Spacer(1, 0.35 * cm))
    else:
        # Necessário para cálculo de conformidade
        ch_total = calcular_ch_total_curso(componentes)
        ch_i = calcular_ch_por_nucleo(componentes, "I")
        ch_ii = calcular_ch_por_nucleo(componentes, "II")
        ch_iii = calcular_ch_por_nucleo(componentes, "III")
        ch_iv = calcular_ch_por_nucleo(componentes, "IV")
        perc_extensao = calcular_percentual_extensao(componentes)
    
    if "conformidade" in secoes_normalizadas:
        story.append(Paragraph("Resumo de Conformidade", heading_style))
        resultado_validacao = validar_curso_completo(componentes)
        conformidade_itens = []
        
        for nucleo in ["I", "II", "III", "IV"]:
            ch_atual = calcular_ch_por_nucleo(componentes, nucleo)
            ch_minima = obter_ch_minima_por_nucleo(nucleo)
            valido, _ = validar_ch_minima_nucleo(ch_atual, ch_minima)
            status = "✓" if valido else "✗"
            conformidade_itens.append([f"{status} Núcleo {nucleo} (mín. {ch_minima:.0f}h)", _formatar_carga_horaria(ch_atual)])
        
        status_total = "✓" if ch_total >= 3200 else "✗"
        status_ext = "✓" if perc_extensao >= 10 else "✗"
        
        conformidade_itens.extend([
            [f"{status_total} CH Total do Curso (mín. 3200h)", _formatar_carga_horaria(ch_total)],
            [f"{status_ext} Percentual de Extensão (mín. 10%)", f"{perc_extensao:.2f}%"]
        ])
        
        if resultado_validacao["erros"]:
            conformidade_itens.append([f"✗ Pendências detectadas ({len(resultado_validacao['erros'])})", ""])
        else:
            conformidade_itens.append(["✓ Curso conforme com todas as validações principais", ""])
        
        tabela_conformidade = Table(conformidade_itens, colWidths=[9.0 * cm, 5.0 * cm])
        tabela_conformidade.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B5FA5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#B5C6E0')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(tabela_conformidade)
    
    doc.build(story)
    return caminho_arquivo

