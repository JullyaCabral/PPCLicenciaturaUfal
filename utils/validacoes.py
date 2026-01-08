"""
Módulo de validações para componentes curriculares.
Responsável por validar regras de negócio e conformidade.
"""


def validar_componente(componente: dict) -> tuple[bool, list[str]]:
    """
    Valida um componente curricular conforme as regras de negócio.
    
    Args:
        componente: Dicionário com os dados do componente
    
    Returns:
        Tupla (é_valido, lista_de_erros)
    """
    erros = []
    
    # Validações básicas
    if not componente.get("nome"):
        erros.append("Nome do componente é obrigatório")
    
    if not componente.get("tipo"):
        erros.append("Tipo do componente é obrigatório")
    
    if not componente.get("nucleo"):
        erros.append("Núcleo é obrigatório")
    
    tipo = componente.get("tipo", "")
    nucleo = componente.get("nucleo", "")
    ch_extensao = componente.get("ch_extensao", 0)
    ch_pratica = componente.get("ch_pratica", 0)
    ch_total = componente.get("ch_total", 0)
    
    # Validação: Se CH de extensão > 0, deve ser Núcleo III
    if ch_extensao > 0 and nucleo != "III":
        erros.append("Componentes com CH de extensão devem pertencer ao Núcleo III")
    
    # Validação: Estágio deve ser Núcleo IV
    if tipo == "Estágio" and nucleo != "IV":
        erros.append("Componentes do tipo Estágio devem pertencer ao Núcleo IV")
    
    # Validação: Disciplina precisa de aulas semanais
    if tipo == "Disciplina":
        if not componente.get("aulas_semanais") or componente.get("aulas_semanais", 0) <= 0:
            erros.append("Disciplinas devem ter número de aulas semanais maior que zero")
    
    # Validações específicas por núcleo
    if nucleo == "I":
        temas_selecionados = componente.get("temas_nucleo_i", [])
        if not temas_selecionados or len(temas_selecionados) == 0:
            erros.append("Núcleo I requer seleção de pelo menos um tema do Art. 13")
    
    if nucleo == "II":
        if not componente.get("diretrizes_nucleo_ii"):
            erros.append("Núcleo II requer indicação das diretrizes específicas da área")
    
    if nucleo == "III":
        if tipo != "Extensão":
            erros.append("Núcleo III aceita apenas componentes do tipo Extensão")
        if not componente.get("descricao_extensao"):
            erros.append("Núcleo III requer indicação do vínculo com projeto extensionista")
        if ch_extensao != ch_total:
            erros.append("No Núcleo III, toda a carga horária deve ser registrada como Extensão")
    
    if nucleo == "IV":
        if tipo != "Estágio":
            erros.append("Núcleo IV aceita apenas componentes do tipo Estágio")
        if not componente.get("local_realizacao"):
            erros.append("Núcleo IV requer local de realização")
        if not componente.get("etapa_estagio"):
            erros.append("Núcleo IV requer etapa do estágio")
        # Validação específica: Estágios devem ter pelo menos 400h
        if tipo == "Estágio" and ch_total < 400:
            erros.append("Estágios devem ter carga horária mínima de 400h")
        if ch_pratica != ch_total:
            erros.append("No Núcleo IV, a carga horária deve ser integralmente prática")
    
    return len(erros) == 0, erros


def validar_curso_completo(componentes: list) -> dict:
    """
    Valida a conformidade do curso completo com todas as regras.
    
    Args:
        componentes: Lista de dicionários com os componentes
    
    Returns:
        Dicionário com status de validações e mensagens
    """
    resultado = {
        "valido": True,
        "erros": [],
        "avisos": []
    }
    
    # Importar aqui para evitar circular
    from utils.calculos import (
        calcular_ch_total_curso,
        calcular_ch_por_nucleo,
        calcular_percentual_extensao,
        obter_ch_minima_por_nucleo,
        validar_ch_minima_nucleo
    )
    
    # Validar cada componente individualmente
    for i, comp in enumerate(componentes, 1):
        valido, erros = validar_componente(comp)
        if not valido:
            resultado["valido"] = False
            resultado["erros"].append(f"Componente {i} ({comp.get('nome', 'sem nome')}): {', '.join(erros)}")
    
    # Validar CH total do curso
    ch_total = calcular_ch_total_curso(componentes)
    if ch_total < 3200:
        resultado["valido"] = False
        resultado["erros"].append(f"CH total do curso ({ch_total:.0f}h) está abaixo do mínimo exigido (3200h)")
    
    # Validar CH mínima por núcleo
    for nucleo in ["I", "II", "III", "IV"]:
        ch_atual = calcular_ch_por_nucleo(componentes, nucleo)
        ch_minima = obter_ch_minima_por_nucleo(nucleo)
        valido, mensagem = validar_ch_minima_nucleo(ch_atual, ch_minima)
        if not valido:
            resultado["valido"] = False
            resultado["erros"].append(f"Núcleo {nucleo}: {mensagem}")
    
    # Validar percentual de extensão (10% mínimo)
    percentual_extensao = calcular_percentual_extensao(componentes)
    if percentual_extensao < 10:
        resultado["valido"] = False
        resultado["erros"].append(f"Percentual de extensão ({percentual_extensao:.2f}%) está abaixo do mínimo exigido (10%)")
    
    return resultado

