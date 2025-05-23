import tiktoken
import html2text
from typing import Dict, Any, List

def get_model_context_window(model_name: str) -> int:
    """
    Returns the maximum context window size for a given model
    """
    context_window_size = {
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "text-davinci-003": 4097,
        "text-davinci-002": 4097
    }
    return context_window_size.get(model_name, 0)

LLM_MODEL = "gpt-3.5-turbo-16k"
TOKEN_LIMIT_RULE = get_model_context_window(LLM_MODEL) // 2


def clean_html_item(key, item):
    # Criar o conversor
    converter = html2text.HTML2Text()
    converter.ignore_links = True       # remove os links
    converter.body_width = 0            # evita quebras de linha automáticas

    # Converter HTML do texto parametrizado em texto legível
    html_content = item[key]
    if html_content:
        clean_text = converter.handle(html_content)
        item[key] = clean_text


def filter_results(results: List[Dict[str, Any]], filtro: List[str]) -> List[Dict[str, Any]]:
    """
    Filtra os campos de cada item do resultado, mantendo apenas as chaves especificadas na lista de filtro.

    Args:
        results (List[Dict[str, Any]]): Lista de dicionários contendo os resultados a serem filtrados
        filtro (List[str]): Lista de chaves que devem ser mantidas em cada item do resultado

    Returns:
        List[Dict[str, Any]]: Lista com os mesmos itens, mas contendo apenas as chaves especificadas
    """
    if not filtro or not results:
        return results

    # Verifica quais chaves do filtro existem no primeiro item
    first_item_keys = results[0].keys()
    valid_keys = [key for key in filtro if key in first_item_keys]

    # Se nenhuma chave for válida, retorna os resultados originais
    if not valid_keys:
        return results

    try:
        filtered_results = []
        for item in results:
            filtered_item = {key: item[key] for key in valid_keys}
            filtered_results.append(filtered_item)
    except Exception as e:
        print(f"Erro ao filtrar os resultados: {str(e)}. Retornando a lista sem filtros.")
        return results
    return filtered_results


def has_nested_data(item: Dict[str, Any]) -> bool:
    """Check if dictionary has nested structures (dicts, lists)."""
    return any(isinstance(value, dict) for value in item.values())


def transform_to_table_structure(results: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    """Transform list of dicts into a table-like dictionary structure."""
    table = {}
    # Get all unique keys from all items
    all_keys = set().union(*(item.keys() for item in results))
    # Initialize lists for each key
    for key in all_keys:
        table[key] = [item.get(key) for item in results]
    return table


def count_tokens(data: Any) -> int:
    encoding = tiktoken.encoding_for_model(LLM_MODEL)
    return len(encoding.encode(str(data)))


def binary_search_valid_rows(table_results: Dict[str, List[Any]]) -> int:
    """
    Use binary search to find the maximum number of rows that fit within token limit.
    Returns the number of rows that can be included while staying under token limit.
    """
    left = 1  # Minimum 1 row
    right = len(next(iter(table_results.values())))  # Maximum number of rows
    max_valid_rows = 0

    while left <= right:
        mid = (left + right) // 2
        truncated = {k: v[:mid] for k, v in table_results.items()}
        current_tokens = count_tokens(truncated)

        if current_tokens <= TOKEN_LIMIT_RULE:
            max_valid_rows = mid  # Store this valid row count
            left = mid + 1  # Try to find a larger valid value
        else:
            right = mid - 1  # Need to reduce rows

    return max_valid_rows


def cut_down_on_tokens(results: List[Dict[str, Any]]):
    """
    Cut down results to fit within token limit, with careful token counting
    for both regular and table-structured data.
    """

    # Check for nested data and transform if possible
    results_string = str(results)
    use_table_structure = not any(has_nested_data(item) for item in results)

    if use_table_structure:
        print("Original structure changes to table format table")
        table_results = transform_to_table_structure(results)

    if count_tokens(results_string) > TOKEN_LIMIT_RULE:
        if use_table_structure:
            # Handle table structure
            if count_tokens(table_results) <= TOKEN_LIMIT_RULE:
                print("Returning table format of items with no cropping")
                return table_results
            else:
                max_rows = binary_search_valid_rows(table_results)
                cropped_table = {key: values[:max_rows] for key, values in table_results.items()}
                print(f"Maximum token size limit reached. Keeping {max_rows}/{len(next(iter(table_results.values())))} rows.")
                return cropped_table
        else:
            # Handle regular structure
            chopped_results = []
            current_tokens = 0
            for item in results:
                current_tokens += count_tokens(item)
                if current_tokens > TOKEN_LIMIT_RULE:
                    break
                chopped_results.append(item)
            print(f"Maximum token size limit reached. Results chopped to: {len(chopped_results)} items")
            return chopped_results
    else:
        if use_table_structure:
            print("Returning table format of items with no cropping")
            return table_results
        print("Results fit within token size limit!")
        return results

