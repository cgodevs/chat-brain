'''
DOING:
(4a) Atualizar a planilha de serviços (para consulta) com os dados do PDF
(5.?) NODE: Verificações de segurança (o usuário fez alguma pergunta sobre si mesmo, dentro do escopo de perguntas jurídicas?)

=================================================
DONE:
(0) Receber o perfil do usuário via requisição (id e número de protocolo por enquanto)
(b) NODE(?): A tool de consulta de API selecionada inicialmente utiliza os parâmetros encontrados para chamar a API. Criar uma tool para cada endpoint disponível no serviço de API X, a tool deve retornar os dados do endpoint para o próximo nó.
(5d) Criar tools que chamam as APIs do serviço de consultas processuais.

=================================================
TODO:
(1) NODE: Procurar pelo histórico deste protocolo no Redis, caso exista. Caso não, criar uma nova memória. A memória recuperada deve ser o novo estado da aplicação.
(1.?) NODE: Adicionar simplicidade de comunicação ao estilo de comunicação do SystemMessage de acordo com o perfil do usuário (haverá diferença na simplicidade de linguagem caso não seja magistrado)
(3) NODE: Filtro de segurança, utiliza de vários filtros para entender se a pergunta do usuário é maliciosa.
(4) NODE PRINCIPAL (assistant):
    (b) Analisar mensagem para retornar lista de intenções, impondo limite, para as quais cada uma dará origem à execução de um nó dedicado.
    (c) As intenções identificadas se encaixam em uma ou mais categorias de serviços disponíveis pela ferramenta? (Aqueles na planilha, que vamos trazer como texto para a IA mesmo, mais tarde é melhor tentar uma busca vetorial). Reuni-las em uma lista de objetos que tragam o id do serviço correspondente e a evidência na mensagem que permitem associar ao serviço, incluindo aquelas que não se identificam com nenhum
    (d) Para cada serviço identificado, iniciar a execução de um nó. Como um edge with condition pode retornar vários nós?
(5) NODE: Consulta de API. Seleciona tool necessária para retorno dos dados mais capazes para resposta da natureza da pergunta, mas não a chama ainda.
    (a) NODE(?): Uma tool auxiliar é chamada para identificar os dados necessários para a tool que chama o endpoint. Aqui poderemos usar dados do usuário no estado atual. Ela retorna um json com os parâmetros necessários para a função identificada.
        (a.1) NODE: Caso não tenha sido possível identificar todos os parametros necessários para a tool que será chamada, explicar seu entendimento sobre o que o usuário precisa e perguntar a ele se poderia fornecer mais informações (de movo que retornamos ao node anterior).
    (c) NODE: Análise dos dados (se possível como dataframe ou outro formato mais econômico) contra a pergunta do usuário
    (e) Criar cada uma das tools. Suas descrições são importantes. Cada uma fará uma busca em sua lista (variável) dedicadas, utilizando para isto os filtros recebidos como parâmetros deve fazer uma
    (f) Retornar para o nó assistente
(6) NODE: Consulta de dados. Consulta na base de documentações onde está a resposta.
    (a) Montar a base de documentos a partir dos links. Cada documento, ao entrar na base, deve receber uma lista de categorias nas quais estão capacitados a responder perguntas relacionadas aos serviços oferecidos. Ao tentarmos encontrar um documento capaz de responder a pergunta, iniciaremos a filtragem de documentos potenciais a partir destas listas, onde vamos procurar por aqueles com os quais a pergunta se encaixa. A segunda filtragem será feita a partir dos resumos de cada documento. E então a busca será de fato realizada sobre cada um daqueles filtrados.
    (b) Como fazer para que 2 ou mais documentos possam ser consultados? Chain of thought
(7) Em paralelo:
    (a) retornar mensagem da IA
    (b.1) NODE: adicionar nova mensagem ao estado de memória
    (b.2) NODE: verificar se o histórico de mensagens está muito grande. Caso sim: resumir um certo número de mensagens de acordo com um LIMITE1 de tokens até então e manter as últimas mensagens com base em um LIMITE2 de tokens.
    (b.3) NODE: atualizar histórico de mensagens no Redis para aquela função
'''

import api_tools.api_request as chat_app_tools
from langchain_core.messages import ( AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage )
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition

api_tools = [
    chat_app_tools.consultar_por_tipo,
    chat_app_tools.consultar_detalhes_por_tipo,
    chat_app_tools.download_tipo
]
sys_msg = SystemMessage(content=f"You are an useful assistent for retrieving the most assertive data only from available APIs, not based on your knowledge about the question.")
llm = ChatOpenAI(model="gpt-3.5-turbo-16k").bind_tools(api_tools, parallel_tool_calls=False)

# LANGCHAIN HELP =======================

def get_ai_message(message):
    gpt4o_chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    msg = HumanMessage(content=message)
    ai_message = gpt4o_chat.invoke([msg])
    print(ai_message.content)
    return ai_message.content

# CLASSES ==============================

class MessagesState(MessagesState):
    pass
    # Add any keys needed beyond messages, which is pre-built

class MaliciousContent:
    pass

# NODES ================================

def assistant(state: MessagesState):
   return {"messages": [llm.invoke([sys_msg] + state["messages"])]}

def call_api(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

def check_question_safety(state: MessagesState):
    # Check for malicious intent or out of scope questions
    user_input = state['messages'][-1].content
    print(f"User input: {user_input}")
    # implement validation
    is_question_outscoped = True
    if is_question_outscoped:
        return "feedback"
    else:
        return "assistant"

def greeting(state: MessagesState):
    return {"messages": [AIMessage(content="Hello!")]}

def feedback(state: MessagesState):
    default_message = AIMessage(content="Desculpe, você perguntou algo fora do meu escopo de apoio. Posso te ajudar com algo mais?")
    return {"messages": [default_message]}


# BUILD GRAPH ==========================

builder = StateGraph(MessagesState)
builder.add_node("assistant", call_api)
builder.add_node("tools", ToolNode(api_tools))
builder.add_node("greeting", greeting)
builder.add_node("feedback", feedback)

builder.add_conditional_edges(START, check_question_safety)  # routes to feedback or assistant
builder.add_edge("feedback", END)
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

graph = builder.compile()


# RUN TESTS =======================================

my_message = HumanMessage(content="Quanto são 2 + 2 ?")
# my_message = HumanMessage(content=f"Algum documento processual contém código com a sequência 123 em qualquer posição?")
# my_message = HumanMessage(content=f"Olá!")
messages = [sys_msg + my_message]
messages = graph.invoke({"messages": my_message})


for m in messages['messages']:
    m.pretty_print()