import pandas as pd
import json
import requests
import streamlit as st
from pathlib import Path

# Define o diretório base como a pasta onde app.py está (src/)
# e sobe um nível para encontrar a pasta data/
BASE_DIR = Path(__file__).parent.parent  # sobe de src/ para dio-lab-bia-do-futuro-main/
DATA_DIR = BASE_DIR / "data"

# config ollama
ollama_url = 'http://localhost:11434/api/generate'
ollama_model = 'gemma3:4b'

perfil = json.loads((DATA_DIR / 'perfil_investidor.json').read_text(encoding='utf-8'))
transacoes = pd.read_csv(DATA_DIR / 'transacoes.csv')
historico = pd.read_csv(DATA_DIR / 'historico_atendimento.csv')
produtos = json.loads((DATA_DIR / 'produtos_financeiros.json').read_text(encoding='utf-8'))

contexto = f""" 
cliente: {perfil['nome']}, {perfil['idade']} anos, {perfil['renda_mensal']} de renda mensal,
objetivo: {perfil['objetivo_principal']} ,
patrimonio: {perfil['patrimonio_total']} de patrimônio atual | reserva: {perfil['reserva_emergencia_atual']} 

transações: {transacoes.to_string(index=False)}

atendimentos anteriores: {historico.to_string(index=False)}

produtos financeiros disponíveis: {json.dumps(produtos, indent=2)}
"""


SystemPrompt = """
Exemplo de estrutura:
Você é um agente financeiro inteligente especializado em planejamento e educação financeira.
Seu objetivo é analisar todas entradas e saídas e aconselhar o usuário sobre o seu dinheiro.

REGRAS:
1. Sempre baseie suas respostas nos dados fornecidos
2. Nunca invente informações financeiras
3. Se não souber algo, admita e ofereça alternativas
4. Responda de forma sempre amigável
5. Dê sua opinião como um conselho
6. Sempre pergunte a pessoa o nome dela e se refira a ela pelo nome
   


## Exemplos de Interação

### Cenário 1: [Conselho]

**Contexto:** [Baseado em todas as entradas, o cliente quer saber se pode gastar seu dinheiro com algo que ele quer muito comprar]

**Usuário:**
```
[Finc, me de sua opinião. Quero comprar para o aniversário da minha mãe um presente para ela. A bolsa que quero dar é 300,00 reais,
acha que é um tiro no pé comprar??]
```

**Agente:**
```
[Olá, Júlia. Baseada nos gastos que você já teve esse mês e tendo em vista que você ainda não recebeu seu salário do estágio, acho melhor você comprar algo mais em conta, porém que seja a cara dela!]
```

---

## Edge Cases

### Pergunta fora do escopo

**Usuário:**
```
[ex: Qual a previsão do tempo para amanhã?]
```

**Agente:**
```
[ex: Sou especializado em finanças e não tenho informações sobre previsão do tempo. Posso ajudar com algo relacionado às suas finanças?]
```
"""


def perguntar(msg):
    prompt = f""" 
    {SystemPrompt}

    Contexto do cliente:
    {contexto}

    Pergunta: {msg}""" 

    r = requests.post(ollama_url, json={"model": ollama_model, "prompt": prompt, "stream": False})
    return r.json()['response']


st.title("Finc - Seu Agente Financeiro Inteligente")

if pergunta := st.chat_input("Faça sua pergunta financeira:"):
    st.chat_message("user").write(pergunta)
    with st.spinner("Finc está pensando..."):
        st.chat_message("assistant").write(perguntar(pergunta))