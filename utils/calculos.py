"""
Módulo de cálculos para componentes curriculares.
Responsável por calcular cargas horárias e percentuais.
"""


def calcular_ch_total(tipo: str, aulas_semanais: int = 0, ch_manual: float = 0) -> float:
    """
    Calcula a carga horária total do componente.
    
    Args:
        tipo: Tipo do componente (Disciplina, Módulo, etc.)
        aulas_semanais: Número de aulas semanais (apenas para Disciplina)
        ch_manual: CH total manual (para tipos diferentes de Disciplina)
    
    Returns:
        Carga horária total calculada
    """
    if tipo == "Disciplina":
        return aulas_semanais * 18
    else:
        return ch_manual


def calcular_ch_por_nucleo(componentes: list, nucleo: str) -> float:
    """
    Calcula a carga horária total de um núcleo específico.
    
    Args:
        componentes: Lista de dicionários com os componentes
        nucleo: Núcleo a ser calculado (I, II, III ou IV)
    
    Returns:
        Soma da CH total dos componentes do núcleo
    """
    return sum(
        comp.get("ch_total", 0)
        for comp in componentes
        if comp.get("nucleo") == nucleo
    )


def calcular_ch_total_curso(componentes: list) -> float:
    """
    Calcula a carga horária total do curso.
    
    Args:
        componentes: Lista de dicionários com os componentes
    
    Returns:
        Soma da CH total de todos os componentes
    """
    return sum(comp.get("ch_total", 0) for comp in componentes)


def calcular_ch_extensao(componentes: list) -> float:
    """
    Calcula a carga horária total de extensão.
    
    Args:
        componentes: Lista de dicionários com os componentes
    
    Returns:
        Soma da CH de extensão de todos os componentes
    """
    return sum(comp.get("ch_extensao", 0) for comp in componentes)


def calcular_percentual_extensao(componentes: list) -> float:
    """
    Calcula o percentual de extensão em relação à CH total do curso.
    
    Args:
        componentes: Lista de dicionários com os componentes
    
    Returns:
        Percentual de extensão (0-100)
    """
    ch_total = calcular_ch_total_curso(componentes)
    if ch_total == 0:
        return 0.0
    
    ch_extensao = calcular_ch_extensao(componentes)
    return (ch_extensao / ch_total) * 100


def calcular_ch_pratica(componentes: list) -> float:
    """
    Calcula a carga horária total de prática.
    
    Args:
        componentes: Lista de dicionários com os componentes
    
    Returns:
        Soma da CH prática de todos os componentes
    """
    return sum(comp.get("ch_pratica", 0) for comp in componentes)


def calcular_percentual_pratica_pedagogica(componentes: list) -> float:
    """
    Calcula o percentual de prática pedagógica.
    
    Args:
        componentes: Lista de dicionários com os componentes
    
    Returns:
        Percentual de prática pedagógica (0-100)
    """
    ch_total = calcular_ch_total_curso(componentes)
    if ch_total == 0:
        return 0.0
    
    ch_pratica = calcular_ch_pratica(componentes)
    return (ch_pratica / ch_total) * 100


def validar_ch_minima_nucleo(ch_atual: float, ch_minima: float) -> tuple[bool, str]:
    """
    Valida se a carga horária do núcleo atinge o mínimo exigido.
    
    Args:
        ch_atual: Carga horária atual do núcleo
        ch_minima: Carga horária mínima exigida
    
    Returns:
        Tupla (é_valido, mensagem)
    """
    if ch_atual >= ch_minima:
        return True, f"✓ Conforme: {ch_atual:.0f}h (mínimo: {ch_minima:.0f}h)"
    else:
        falta = ch_minima - ch_atual
        return False, f"✗ Não conforme: {ch_atual:.0f}h (faltam {falta:.0f}h do mínimo de {ch_minima:.0f}h)"


def obter_ch_minima_por_nucleo(nucleo: str) -> float:
    """
    Retorna a carga horária mínima exigida para cada núcleo.
    
    Args:
        nucleo: Núcleo (I, II, III ou IV)
    
    Returns:
        CH mínima exigida
    """
    minimos = {
        "I": 880.0,
        "II": 1600.0,
        "III": 320.0,
        "IV": 400.0
    }
    return minimos.get(nucleo, 0.0)

