"""
Módulo de exportações para componentes curriculares.
Responsável por gerar arquivos CSV, XLSX e PDF.
"""

import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def exportar_csv(componentes: list, caminho_arquivo: str) -> str:
    """
    Exporta os componentes curriculares para arquivo CSV (formato para migração SIGAA).
    
    Args:
        componentes: Lista de dicionários com os componentes
        caminho_arquivo: Caminho onde o arquivo será salvo
    
    Returns:
        Caminho do arquivo salvo
    """
    # Preparar dados para CSV (formato SIGAA)
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


def exportar_xlsx(componentes: list, caminho_arquivo: str) -> str:
    """
    Exporta os componentes curriculares para arquivo XLSX (planilha de verificação).
    Cria múltiplas abas: Matriz (por período), Por Núcleo (resumo), Componentes (lista completa).
    
    Args:
        componentes: Lista de dicionários com os componentes
        caminho_arquivo: Caminho onde o arquivo será salvo
    
    Returns:
        Caminho do arquivo salvo
    """
    from openpyxl.utils import get_column_letter
    
    # Criar arquivo XLSX com múltiplas abas
    with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
        # ABA 1: Matriz por Período
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
        
        # ABA 2: Por Núcleo (resumo)
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
        
        # ABA 3: Componentes (lista completa para auditoria)
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


def exportar_pdf(componentes: list, caminho_arquivo: str) -> str:
    """
    Exporta um relatório em PDF com quadro-resumo de CH por semestre e núcleo.
    
    Args:
        componentes: Lista de dicionários com os componentes
        caminho_arquivo: Caminho onde o arquivo será salvo
    
    Returns:
        Caminho do arquivo salvo
    """
    from utils.calculos import (
        calcular_ch_total_curso,
        calcular_ch_por_nucleo,
        calcular_percentual_extensao,
        calcular_percentual_pratica_pedagogica
    )
    
    # Criar documento PDF
    doc = SimpleDocTemplate(caminho_arquivo, pagesize=landscape(A4))
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12
    )
    
    # Título
    story.append(Paragraph("Relatório de Carga Horária - Componentes Curriculares", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Matriz Curricular Principal por Período
    story.append(Paragraph("Matriz Curricular por Período", heading_style))
    df_matriz = gerar_matriz_por_periodo(componentes)
    
    # Preparar dados da tabela matriz (limitar colunas para melhor visualização)
    colunas_matriz = ["Semestre", "Nome", "CH Semanal", "CH Teórica", "CH Prática", "CH Extensão", "CH Total"]
    dados_tabela_matriz = [colunas_matriz]
    
    for _, row in df_matriz.iterrows():
        linha_matriz = []
        for col in colunas_matriz:
            valor = row[col] if col in df_matriz.columns else ""
            if isinstance(valor, (int, float)) and col != "Semestre":
                if col == "CH Semanal" and valor == "":
                    linha_matriz.append("")
                else:
                    linha_matriz.append(f"{valor:.0f}h" if valor != "" else "")
            else:
                linha_matriz.append(str(valor))
        dados_tabela_matriz.append(linha_matriz)
    
    # Criar tabela matriz (ajustar tamanhos)
    tabela_matriz = Table(dados_tabela_matriz, repeatRows=1, colWidths=[2*cm, 6*cm, 2*cm, 2*cm, 2*cm, 2*cm, 2*cm])
    tabela_matriz.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(tabela_matriz)
    story.append(Spacer(1, 0.5*cm))
    story.append(PageBreak())
    
    # Resumo por semestre e núcleo
    story.append(Paragraph("Quadro-Resumo: CH por Semestre e Núcleo", heading_style))
    
    df_resumo = gerar_resumo_por_semestre_nucleo(componentes)
    
    # Preparar dados da tabela
    dados_tabela = [df_resumo.columns.tolist()]
    for _, row in df_resumo.iterrows():
        linha = []
        for col in df_resumo.columns:
            valor = row[col]
            if isinstance(valor, (int, float)) and col != "Semestre":
                linha.append(f"{valor:.0f}h")
            else:
                linha.append(str(valor))
        dados_tabela.append(linha)
    
    # Criar tabela
    tabela = Table(dados_tabela, repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(tabela)
    story.append(Spacer(1, 0.5*cm))
    
    # Resumo geral
    story.append(Paragraph("Resumo Geral do Curso", heading_style))
    
    ch_total = calcular_ch_total_curso(componentes)
    ch_i = calcular_ch_por_nucleo(componentes, "I")
    ch_ii = calcular_ch_por_nucleo(componentes, "II")
    ch_iii = calcular_ch_por_nucleo(componentes, "III")
    ch_iv = calcular_ch_por_nucleo(componentes, "IV")
    perc_extensao = calcular_percentual_extensao(componentes)
    perc_pratica = calcular_percentual_pratica_pedagogica(componentes)
    
    resumo_geral = [
        ["Carga Horária Total do Curso", f"{ch_total:.0f}h"],
        ["CH Núcleo I", f"{ch_i:.0f}h"],
        ["CH Núcleo II", f"{ch_ii:.0f}h"],
        ["CH Núcleo III", f"{ch_iii:.0f}h"],
        ["CH Núcleo IV", f"{ch_iv:.0f}h"],
        ["Percentual de Extensão", f"{perc_extensao:.2f}%"],
        ["Percentual de Prática Pedagógica", f"{perc_pratica:.2f}%"]
    ]
    
    tabela_resumo = Table(resumo_geral, colWidths=[8*cm, 4*cm])
    tabela_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    
    story.append(tabela_resumo)
    story.append(Spacer(1, 0.5*cm))
    
    # Resumo de Conformidade
    story.append(Paragraph("Resumo de Conformidade", heading_style))
    from utils.validacoes import validar_curso_completo
    from utils.calculos import obter_ch_minima_por_nucleo, validar_ch_minima_nucleo
    
    resultado_validacao = validar_curso_completo(componentes)
    
    conformidade_itens = []
    
    # CH mínima por núcleo
    for nucleo in ["I", "II", "III", "IV"]:
        ch_atual = calcular_ch_por_nucleo(componentes, nucleo)
        ch_minima = obter_ch_minima_por_nucleo(nucleo)
        valido, mensagem = validar_ch_minima_nucleo(ch_atual, ch_minima)
        status = "✓" if valido else "✗"
        conformidade_itens.append([f"{status} Núcleo {nucleo} (mín. {ch_minima:.0f}h)", f"{ch_atual:.0f}h"])
    
    # CH total do curso
    status_total = "✓" if ch_total >= 3200 else "✗"
    conformidade_itens.append([f"{status_total} CH Total do Curso (mín. 3200h)", f"{ch_total:.0f}h"])
    
    # Percentual extensão
    status_ext = "✓" if perc_extensao >= 10 else "✗"
    conformidade_itens.append([f"{status_ext} Percentual de Extensão (mín. 10%)", f"{perc_extensao:.2f}%"])
    
    tabela_conformidade = Table(conformidade_itens, colWidths=[10*cm, 4*cm])
    tabela_conformidade.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    
    story.append(tabela_conformidade)
    
    # Gerar PDF
    doc.build(story)
    
    return caminho_arquivo

