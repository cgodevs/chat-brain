'''
DOING:
(4a) Atualizar a planilha de serviços (para consulta) com os dados do PDF
(5d) Criar mocks de dados vindos da API para cada tool. Teremos um arquivo python armazenando como variáveis várias listas de variações de jsons (dicionários) para cada endpoint.

=================================================
DONE:
(0) Receber o perfil do usuário via requisição (id e número de protocolo por enquanto)

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
    (5.?) NODE: Verificações de segurança (o usuário fez alguma pergunta sobre si mesmo, dentro do escopo de perguntas jurídicas?)
    (a) NODE(?): Uma tool auxiliar é chamada para identificar os dados necessários para a tool que chama o endpoint. Aqui poderemos usar dados do usuário no estado atual. Ela retorna um json com os parâmetros necessários para a função identificada.
        (a.1) NODE: Caso não tenha sido possível identificar todos os parametros necessários para a tool que será chamada, explicar seu entendimento sobre o que o usuário precisa e perguntar a ele se poderia fornecer mais informações (de movo que retornamos ao node anterior).
    (b) NODE(?): A tool de consulta de API selecionada inicialmente utiliza os parâmetros encontrados para chamar a API. Criar uma tool para cada endpoint disponível no serviço de API X, a tool deve retornar os dados do endpoint para o próximo nó
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
