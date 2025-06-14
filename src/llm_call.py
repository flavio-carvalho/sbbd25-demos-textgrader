import json
import ollama
import sys

def avaliar_redacao(json_input: str) -> str:
    """
    Receives a JSON string with 'tema', 'texto', and 'competencias',
    and returns the textual evaluation generated by the Gemma model via Ollama.
    """
    # Parse JSON
    data = json.loads(json_input)
    redacao = data[0]

    # Obtém dados do dicionário da redação
    tema = redacao["tema"]
    texto = redacao["texto"]
    competencias_dados = redacao["competencias"]

    # Monta o system prompt com as competências
    competencias_str = "\n".join([
        f"- **{comp['competencia']}**: Nota {comp['nota']}"
        for comp in competencias_dados
    ])

    # Monta o system prompt
    system_prompt = (
        "Você é um avaliador pedagógico especialista em produção textual no contexto do ENEM. "
        "Sua tarefa é analisar uma redação escrita por um estudante, considerando as notas atribuídas "
        "a cada uma das cinco competências avaliativas do exame e também o tema (i.e., a proposta) da redação correspondente.\n\n"
        "Você deve gerar sugestões específicas de melhoria para o texto, sempre levando em conta:\n"
        "- O conteúdo integral da redação produzida.\n"
        "- As notas atribuídas em cada uma das cinco competências (0–200).\n"
        "- O tema da redação (proposta e/ou texto motivador).\n\n"
        f"**Competências Avaliadas:**\n{competencias_str}\n\n"
        "Apresente sua resposta no seguinte formato:\n\n"
        "**Sugestões de Melhoria (uma por competência):**\n"
        "**Competência 1** (Nota: [nota]): [Sugestão concisa]\n"
        "**Competência 2** (Nota: [nota]): [Sugestão concisa]\n"
        "**Competência 3** (Nota: [nota]): [Sugestão concisa]\n"
        "**Competência 4** (Nota: [nota]): [Sugestão concisa]\n"
        "**Competência 5** (Nota: [nota]): [Sugestão concisa]\n\n"
        "Guie-se pelas notas fornecidas e pelo conteúdo do texto para cada sugestão."
        "[Para cada competência, gere até 3 sugestões focadas nessa competência, levando em conta o conteúdo da redação, o escopo do tema e a nota recebida]\n"
        "---\n\n"
        "Importante: Use o tema da redação para avaliar a pertinência temática e o foco argumentativo do estudante. "
        "Se a proposta de intervenção for vaga, sugira maneiras de conectá-la melhor ao problema central. "
        "Não reescreva a redação nem emita julgamentos genéricos; concentre-se em orientar melhorias concretas."
    )

    # Monta o user prompt
    competencias_str_user = "\n".join([
        f"Competência {i+1}: Nota {comp['nota']} | {comp['competencia']}"
        for i, comp in enumerate(competencias_dados)
    ])

    user_prompt = (
        f"Tema da redação:\n{tema}\n\n"
        f"Texto da redação:\n{texto}\n\n"
        f"Notas por competência:\n{competencias_str_user}"
    )

    # Chamada ao modelo via Ollama
    response = ollama.chat(
        model="gemma:7b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response["message"]["content"]


## __main__
if __name__ == "__main__":
    try:
        # Obtém o nome do arquivo via argumento ou entrada do usuário
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        else:
            filename = input("Digite o nome do arquivo JSON a ser processado: ")

        # Lê o arquivo JSON
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Mostra opção de escolha da redação
        num_redacoes = len(data)
        if num_redacoes == 0:
            raise ValueError("O arquivo não contém redações válidas.")

        print(f"Existem {num_redacoes} redações no arquivo. Escolha um número entre 1 e {num_redacoes}:")

        while True:
            try:
                escolha = int(input("Número da redação: "))
                if 1 <= escolha <= num_redacoes:
                    redacao_index = escolha - 1
                    break
                else:
                    print("Número inválido. Tente novamente.")
            except ValueError:
                print("Digite um número válido.")

        # Seleciona a redação escolhida
        redacao = data[redacao_index]

        # Processa a redação escolhida
        json_input = json.dumps([redacao])  # Passa apenas a redação selecionada
        resultado = avaliar_redacao(json_input)

        # Atualiza o campo "cometarios"
        if not redacao.get("cometarios", "").strip():
            redacao["cometarios"] = resultado
        else:
            redacao["cometarios"] += "\n\n" + resultado

        # Exibe o resultado final
        print("Resultado da avaliação:")
        print(json.dumps(redacao, indent=4, ensure_ascii=False))

    except FileNotFoundError:
        print(f"Erro: O arquivo '{filename}' não foi encontrado. [[1]]")
    except json.JSONDecodeError:
        print(f"Erro: O conteúdo do arquivo '{filename}' não é um JSON válido. [[1]]")
    except ValueError as e:
        print(f"Erro: {str(e)}. [[2]]")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}. [[2]]")

    print(resultado)

