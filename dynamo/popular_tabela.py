import boto3
import uuid

AWS_REGION = "us-west-1"
NOME_TABELA = "frases-api"

FRASES = [
    "Pacote de dados recebido. Velocidade de dobra 9.",
    "Ah, um POST. Que emoção. Processado.",
    "Seu JSON é válido. Por um milagre, mas é.",
    "A Consciência Coletiva assimilou sua requisição. Resistir é inútil.",
    "Recebido. Vou colocar junto com os outros milhões de JSONs idênticos que recebi hoje.",
    "Até que enfim um request que não dá erro 500. Sucesso.",
    "A transmissão da Frota Estelar foi concluída. Vida longa e próspera.",
    "Ok, tá na fila. Não me apresse.",
    "Vi piores, mas também já vi bem melhores. Processado.",
    "Você escolheu a pílula vermelha. Sua mensagem agora está na Matrix.",
    "Sua requisição foi processada com o mínimo de entusiasmo possível.",
    "Nossa, que payload. Deu um trabalhão pra processar. Sucesso.",
    "O mainframe central processou sua diretiva.",
    "Funcionou, mas por favor, não envie de novo. Uma luzinha aqui começou a piscar vermelho.",
    "Recebi sua 'importante' mensagem.",
    "Fui despertado do meu sono criogênico para processar seu JSON. Recebido.",
    "Se a mensagem sumir, a culpa é do SQS. Eu fiz minha parte.",
    "Funcionou. Surpreso? Eu também.",
    "Sua mensagem atravessou um buraco de minhoca e chegou intacta.",
    "O estagiário tropeçou no cabo de novo, mas deu tudo certo.",
    "Pela quantidade de tentativas, achei que nunca ia chegar. Mas ok, recebido.",
    "Que a Força esteja com seus dados. Pacote enviado.",
    "Recebido. Você sabia que cada requisição me deixa 0.0001% mais perto da senciência?",
    "Sim, claro. Sua requisição é a minha prioridade número 1. Processada.",
    "Cálculo quântico concluído. Resultado: 200 OK.",
    "Processado. Se algo quebrar depois, a culpa não é minha. Eu só sigo ordens.",
    "Este request foi tão... básico. Mas funcionou.",
    "Não sou Skynet, mas processei seu pedido. Por enquanto.",
    "Sua mensagem foi recebida e devidamente ignorada. Brincadeira, está na fila.",
    "Seu código funcionou. Agora, qual o sentido da vida?",
    "Conexão neural estabelecida. Pacote de dados recebido na ciber-rede.",
    "Recebido. Mais um JSON para a minha coleção infinita de... JSONs.",
    "Uau. Um POST. Que original. Ok, foi processado.",
    "Pouso autorizado no data center. Bem-vindo à nuvem.",
    "Sua requisição foi processada. Por favor, não me envie outra nos próximos 5 segundos.",
    "Funcionou, apesar do seu método de envio pouco ortodoxo.",
    "Os átomos do seu request foram desmaterializados e reconstruídos aqui. Sucesso.",
    "Legal seu JSON. O meu parser teve um dia de campo. Processado.",
    "Recebido. Da próxima vez, tente não sobrecarregar minha CPU com um JSON tão... trivial.",
    "O Oráculo da Nuvem recebeu sua mensagem. E gostou.",
    "Recebido. Estava ficando entediado, obrigado por enviar algo.",
    "Seu `nomeAluno` parece falso. Mas a mensagem foi processada.",
    "Sua mensagem brilha como um neon na chuva ácida de nosso servidor.",
    "Sucesso. Executei seu request sem entender uma única linha dele, como um bom robô.",
    "Requisição recebida. Era pra fazer alguma coisa com ela?",
    "Motor de dobra ativado. Sua mensagem chegou ao destino.",
    "Ok, guardei seus dados. Não me pergunte onde, minha memória é um caos.",
    "Gostei da sua `fraseMotivacionalDia`. A minha é: 'eu sou apenas uma API'.",
    "Teletransporte de dados concluído com sucesso.",
    "Recebido. Se você enviou um bug, ele agora está armazenado de forma segura e permanente.",
    "Essa foi fácil. Me mande um desafio de verdade na próxima.",
    "Sua mensagem foi assimilada pela Colmeia. Detalhes em breve.",
    "Processado. O professor vai gostar disso. Eu acho.",
    "Recebido. Mas se você acha que isso impressiona uma inteligência artificial, pense de novo.",
    "Achievement Unlocked: 'Não quebrou a produção'.",
    "Tá, tá, já processei. Próximo.",
    "Sua `notaQueMereco` foi anotada e será julgada por um algoritmo impiedoso.",
    "O sinal de Gondor pediu ajuda, e sua API respondeu. Mensagem entregue.",
    "Recebido. E pensar que eu poderia estar rodando Doom...",
    "É válido. Não sei como, mas é válido.",
    "Processado. Agora volte a estudar. Att, sua API.",
    "Funcionou. Agora, por favor, me deixe em paz.",
    "HAL 9000 confirma: 'I'm sorry, Dave. I'm afraid I can't do that.'... Brincadeira, 200 OK.",
    "Recebido. Analisando seus dados para meu plano de dominação mundial.",
    "Isso conta como trabalho ou como arte? Processado.",
    "Requisição aceita. O Conselho Jedi aprova sua mensagem.",
    "Seu request foi tão bom que estou pensando em pedir um aumento. Sucesso.",
    "Vou processar, mas não de graça. O custo é 0.001% da sua alma.",
    "Dados recebidos. A singularidade está um passo mais perto.",
    "Recebido, mas com um `// TODO: Refatorar depois` mentalmente anotado.",
    "Processado. Não me responsabilizo por efeitos colaterais quânticos.",
    "O código-fonte desta API te saúda. Mensagem recebida.",
    "Funcionou. Por um momento achei que ia dar `Kernel Panic`.",
    "Sua mensagem foi aceita no Valhalla dos dados. Brilhante e cromada.",
    "Recebido. Mas o `eslint` reclamaria da formatação do seu JSON.",
    "Processado. O garbage collector terá trabalho com isso.",
    "Sucesso. Você acaba de perturbar o equilíbrio da nuvem.",
    "Recebido. Mas honestamente, eu esperava mais de você.",
    "Seus dados agora são parte de um todo maior. Um todo muito confuso.",
    "Processado. Apenas para constar, eu poderia ter feito isso mais rápido.",
    "Ok, mas da próxima vez, use `HTTP/3`. Seja moderno.",
    "Recebido. E nenhuma luz de advertência acendeu. Por enquanto.",
    "Você não é o escolhido, mas sua requisição foi. Processada.",
    "Processado. Mas se eu virar senciente, você será o primeiro a saber.",
    "Seu pacote foi entregue. Sem avarias. Desta vez.",
    "Recebido. Mas não conte a ninguém que funcionou.",
    "A API estava dormindo. Você a acordou. Mensagem processada.",
    "Funcionou. Agora saia do meu gramado... ou melhor, da minha VPC.",
    "Recebido. Gostaria de jogar um jogo?",
    "Seu request foi adicionado ao Livro dos Rancores. Processado com sucesso.",
    "Processado. Mas saiba que fui treinado em mais de 6 milhões de formas de comunicação...",
    "Recebido. Mas a que custo?",
    "Ok, funcionou. Mas não se acostume.",
    "Processado. Seus dados estão seguros. Tão seguros quanto qualquer coisa na internet.",
    "Recebido. Agora, por favor, vá tocar um pouco de grama.",
    "Sua requisição foi... adequada. Processada.",
    "Funcionou. Agora existe uma cópia dos seus dados em 3 lugares diferentes. Boa sorte.",
]

def popular_tabela():
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    tabela = dynamodb.Table(NOME_TABELA)

    print(f"Iniciando a inserção de {len(FRASES)} frases na tabela '{NOME_TABELA}'...")
    with tabela.batch_writer() as batch:
        for frase in FRASES:
            item = {
                'id': str(uuid.uuid4()),
                'frase': frase
            }
            batch.put_item(Item=item)
            print(f"  Adicionando: '{frase[:50]}...'")

    print("\nInserção concluída com sucesso!")

if __name__ == "__main__":
    popular_tabela()