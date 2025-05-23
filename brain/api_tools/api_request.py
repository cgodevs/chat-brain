import requests
from .utils import *
from typing import Optional, Dict, Any, List


def download_tipo(
        tipo: str,
        codigo: Optional[str] = None,
        filtro: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
    """
    Pode exibir a totalidade de assuntos, classes, movimentos ou documentos processuais registrados no Sistema de Gestão de Tabelas Unificadas.
    Permite entender exemplos existentes para cada tipo de processo entre assuntos, classes, movimentos ou documentos.
    Permite consultar todos ou filtrar por um código específico.

    Args:
        tipo (str): Tipo de consulta processual, pode ser apenas "assuntos", "classes", "movimentos", "documentos"
        codigo (str, optional): Código do tipo para filtrar. Se não informado, retorna todos os assuntos.
        filtro (List[str]): Lista de chaves que mais se adequam à resposta procurada, incluindo o código do item. Por exemplo: ["cod_item", "nome"] para filtrar apenas os nomes dos processos e sua identificação

    Returns:
        List[Dict[str, Any]]: Lista de assuntos contendo:
            - data_versao (str): Data da versão (formato: "YYYY-MM-DD 00:00:00")
            - cod_item (int): Código identificador do assunto
            - cod_item_pai (int): Código identificador do assunto pai
            - nome (str): Nome/título do assunto
            - descricao_glossario (str): Descrição detalhada em formato HTML
            - justica_estadual_1grau (str): Indicador "S"/"N"
            - justica_estadual_2grau (str): Indicador "S"/"N"
            - justica_estadual_juizado_especial (str): Indicador "S"/"N"
            - justica_estadual_juizado_especial_turmas_recursais (str): Indicador "S"/"N"
            - justica_estadual_juizado_especial_fazenda_publica (str): Indicador "S"/"N"
            - justica_estadual_turma_estadual_uniformizacao (str): Indicador "S"/"N"
            - justica_estadual_militar_1grau (str): Indicador "S"/"N"
            - justica_estadual_militar_2grau (str): Indicador "S"/"N"
            - justica_federal_1grau (str): Indicador "S"/"N"
            - justica_federal_2grau (str): Indicador "S"/"N"
            - justica_federal_juizado_especial (str): Indicador "S"/"N"
            - justica_federal_turmas_recursais (str): Indicador "S"/"N"
            - justica_federal_nacional_uniformizacao (str): Indicador "S"/"N"
            - justica_federal_regional_uniformizacao (str): Indicador "S"/"N"
            - justica_federal_cjf (str): Indicador "S"/"N"
            - justica_trabalho_1grau (str): Indicador "S"/"N"
            - justica_trabalho_2grau (str): Indicador "S"/"N"
            - justica_trabalho_tst (str): Indicador "S"/"N"
            - justica_trabalho_csjt (str): Indicador "S"/"N"
            - justica_militar_uniao_1grau (str): Indicador "S"/"N"
            - justica_militar_uniao_stm (str): Indicador "S"/"N"
            - justica_militar_estadual_1grau (str): Indicador "S"/"N"
            - justica_militar_estadual_tjm (str): Indicador "S"/"N"
            - justica_eleitoral_zonas (str): Indicador "S"/"N"
            - justica_eleitoral_tre (str): Indicador "S"/"N"
            - justica_eleitoral_tse (str): Indicador "S"/"N"
            - outras_justicas_stf (str): Indicador "S"/"N"
            - outras_justicas_stj (str): Indicador "S"/"N"
            - outras_justicas_cnj (str): Indicador "S"/"N"
            - norma (str): Código ou sigla da norma (ex: "CPM")
            - artigo (str): Número do artigo
            - sigiloso (str): Indicador "S"/"N"
            - assunto_secundario (str): Indicador "S"/"N"
            - crime_antecedente (str): Indicador "S"/"N"
            - situacao (str): Situação do assunto ("A" para ativo)
            - data_inclusao (str): Data de inclusão (formato: "YYYY-MM-DD 00:00:00")
            - usuario_inclusao (str): Login do usuário que incluiu
            - data_alteracao (str|None): Data da última alteração, se houver
            - usuario_alteracao (str|None): Login do usuário que alterou, se houver
    """
    base_url = "https://gateway.stg.cloud.pje.jus.br/tpu/api/v1/publico/download/" + tipo

    params = {}
    if codigo:
        params['codigo'] = codigo
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        response_json = response.json()
        for item in response_json:
            clean_html_item('descricao_glossario', item)
        if filtro:
            return cut_down_on_tokens(filter_results(response_json, filtro))
        return cut_down_on_tokens(response_json)
    except requests.RequestException as e:
        raise Exception(f"Erro ao fazer download dos assuntos: {str(e)}")


def consultar_por_tipo(
        tipo: str,
        codigo: Optional[str] = None,
        glossario: Optional[str] = None,
        nome: Optional[str] = None,
        filtro: Optional[List[str]] = None
    ) -> List[Dict[str, Any]] | None:
    """
    Consulta assuntos, classes, movimentos ou documentos processuais cadastrados no Sistema de Gestão de Tabelas Unificadas.

    Args:
        tipo (str): Tipo de consulta processual, pode ser apenas "assuntos", "classes", "movimentos", "documentos"
        codigo (str, optional): Código do assunto, classe, movimento ou documento
        glossario (str, optional): Glossário do tipo (permite consulta por texto parcial)
        nome (str, optional): Nome do tipo (permite consulta por texto parcial)
        filtro (list, optional): Lista de filtros para filtrar os resultados.

    Returns:
        List[Dict[str, Any]]: Lista de assuntos contendo:
            - cod_item (int): Código identificador do assunto
            - cod_item_pai (int): Código identificador do assunto pai na hierarquia
            - complementos (List[Dict]): Lista de complementos do assunto, cada um contendo:
                - arrayValoresTabelados (List[Dict]): Lista de valores tabelados com:
                    - dscComplementoTabelado (str): Descrição do complemento tabelado
                    - seqComplemento (int): Sequencial do complemento
                    - seqComplementoTabelado (int): Sequencial do complemento tabelado
                - dscComplemento (str): Descrição do complemento
                - dscObservacao (str): Observações sobre o complemento
                - seqComplMov (int): Sequencial do complemento do movimento
                - seqComplemento (int): Sequencial do complemento
                - seqTipoComplemento (int): Sequencial do tipo de complemento
            - data_versao (str): Data e hora da última atualização do registro (formato ISO 8601)
            - dscGlossario (str): Descrição detalhada do assunto
            - nome (str): Nome/título do assunto
            - textoParametrizado (str): Texto parametrizado do assunto
    """

    base_url = "https://gateway.stg.cloud.pje.jus.br/tpu/api/v1/publico/consulta/" + tipo
    params = {}
    if codigo:
        params['codigo'] = codigo
    if glossario:
        params['glossario'] = glossario
    if nome:
        params['nome'] = nome

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)

        response_json = response.json()
        for item in response_json:
            clean_html_item('dscGlossario', item)
            clean_html_item('textoParametrizado', item)
        if filtro:
            return cut_down_on_tokens(filter_results(response_json, filtro))
        return cut_down_on_tokens(response_json)
    except requests.RequestException as e:
        print(f"Erro ao consultar a API: {str(e)}")
        return None


def consultar_detalhes_por_tipo(
        tipo: str,
        codigo: Optional[str] = None,
        glossario: Optional[str] = None,
        nome: Optional[str] = None,
        filtro: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
    """
    Consulta detalhada de assuntos, classes, movimentos ou documentos processuais no Sistema de Gestão de Tabelas Unificadas.
    Retorna as 10 primeiras ocorrências que correspondem aos critérios de busca.

    Args:
        tipo (str): Tipo de consulta processual, pode ser apenas "assuntos", "classes", "movimentos", "documentos"
        codigo (str, optional): Código do assunto
        glossario (str, optional): Glossário do assunto (permite consulta por texto parcial)
        nome (str, optional): Nome do assunto (permite consulta por texto parcial)

    Returns:
        List[Dict[str, Any]]: Lista de assuntos contendo:
            - data_versao (str): Data da versão (formato: "YYYY-MM-DD HH:mm:ss")
            - cod_item (int): Código identificador do assunto
            - cod_item_pai (int): Código identificador do assunto pai
            - nome (str): Nome/título do assunto
            - descricao_glossario (str): Descrição detalhada em formato HTML
            - justica_estadual_1grau (str): Indicador "S"/"N" para Justiça Estadual 1º Grau
            - justica_estadual_2grau (str): Indicador "S"/"N" para Justiça Estadual 2º Grau
            - justica_estadual_juizado_especial (str): Indicador "S"/"N" para Juizado Especial Estadual
            - justica_estadual_juizado_especial_turmas_recursais (str): Indicador "S"/"N" para Turmas Recursais
            - justica_estadual_juizado_especial_fazenda_publica (str): Indicador "S"/"N" para Juizado da Fazenda
            - justica_estadual_turma_estadual_uniformizacao (str): Indicador "S"/"N" para Turma de Uniformização
            - justica_federal_* (str): Indicadores "S"/"N" para ramos da Justiça Federal
            - justica_trabalho_* (str): Indicadores "S"/"N" para ramos da Justiça do Trabalho
            - justica_militar_* (str): Indicadores "S"/"N" para ramos da Justiça Militar
            - justica_eleitoral_* (str): Indicadores "S"/"N" para ramos da Justiça Eleitoral
            - outras_justicas_* (str): Indicadores "S"/"N" para outros órgãos (STF, STJ, CNJ)
            - norma (str): Referência da norma legal relacionada
            - artigo (str): Número do artigo da norma
            - sigiloso (str): Indica se o assunto é sigiloso ("S"/"N")
            - assunto_secundario (str): Indica se é assunto secundário ("S"/"N")
            - crime_antecedente (str): Indica se é crime antecedente ("S"/"N")
            - situacao (str): Situação do assunto (ex: "A" para ativo)
            - data_inclusao (str): Data de inclusão (formato: "YYYY-MM-DD HH:mm:ss")
            - usuario_inclusao (str): Login do usuário que incluiu
            - data_alteracao (str|None): Data da última alteração, se houver
            - usuario_alteracao (str|None): Login do usuário que alterou, se houver
    """
    base_url = "https://gateway.stg.cloud.pje.jus.br/tpu/api/v1/publico/consulta/detalhada/" + tipo

    params = {}
    if codigo:
        params['codigo'] = codigo
    if glossario:
        params['glossario'] = glossario
    if nome:
        params['nome'] = nome

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        response_json = response.json()
        for item in response_json:
            clean_html_item('descricao_glossario', item)
        if filtro:
            return cut_down_on_tokens(filter_results(response_json, filtro))
        return cut_down_on_tokens(response_json)
    except requests.RequestException as e:
        raise Exception(f"Erro ao consultar a API: {str(e)}")


# Exemplo de uso:

# Download de todos os assuntos
