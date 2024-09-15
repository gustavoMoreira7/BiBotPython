import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt 
from sqlmodel import select
from database import create_db_and_tables,  get_session
from models import Registros,Ingressos
import openai
from dotenv import load_dotenv
import os

create_db_and_tables()

def fetch_Registros():
    with get_session() as session:
        registros  = session.exec(select(Registros)).all()
        return pd.DataFrame([l.model_dump() for l in registros])
    
def fetch_Ingressos():
    with get_session() as session:
        ingressos  = session.exec(select(Ingressos)).all()
        return pd.DataFrame([l.model_dump() for l in ingressos])
    

def process_data():
    ingressos_df = fetch_Ingressos()
    ingressos_df['data_ingresso'] = pd.to_datetime(ingressos_df['data_ingresso'], format='%Y-%m-%d')
    return ingressos_df

def filter_by_data(df):
    min_date = df['data_ingresso'].min()
    max_date = df['data_ingresso'].max()

    start_date, end_date = st.sidebar.date_input(
        "Selecione o intervalo de Datas",
        [min_date,max_date],
        min_value=min_date,
        max_value=max_date,
        key="date_filter"
    )

    filtered_df = df[(df['data_ingresso'] >= pd.to_datetime(start_date)) &
                     (df['data_ingresso'] <= pd.to_datetime(end_date))]
    
    return filtered_df

def ask_to_chat(pergunta, df):

    load_dotenv()

    openai.api_key = os.getenv('APIKEY')

    df = df.to_string(index=False)
    mensagem = f"Abaixo está a tabela com indicadores:\n\n{df}\n\n{pergunta}"

    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {'role':'user', 'content':mensagem}
        ]
    )

    resposta = response.choices[0].message.content
    return resposta

def display_coluns_graf(df):

    # Definir as variáveis para o gráfico
    df_grouped = df.groupby('data_ingresso').agg({'valor_ingressado': 'sum'}).reset_index()

    # Definir as variáveis para o gráfico
    datas = df_grouped['data_ingresso']
    valores = df_grouped['valor_ingressado']

    # Criar o gráfico de colunas
    fig, ax = plt.subplots(figsize=(12, 8))

    # Configurando o fundo preto e cor personalizada para as barras
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')

    # Cor das barras e bordas mais elegantes
    bars = ax.bar(datas, valores, color='#1f77b4', edgecolor='white', linewidth=0.7)

    # Adicionar título e rótulos aos eixos com estilo elegante
    plt.title('Soma dos Valores Ingressados por Data', fontsize=16, color='white', pad=20)
    plt.xlabel('Data de Ingresso', fontsize=12, color='white')
    plt.ylabel('Valor Ingressado (em milhares)', fontsize=12, color='white')

    # Melhorar a visualização das datas no eixo X (rotacionando os rótulos)
    plt.xticks(rotation=45, ha='right', fontsize=10, color='white')
    plt.yticks(color='white')

    # Remover as bordas ao redor do gráfico para um visual mais limpo
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')

    # Adicionar valores nas barras para melhor visualização
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:,.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', color='white', fontsize=10)

    # Ajustar o layout para evitar sobreposição
    plt.tight_layout()

    # Exibir o gráfico no Streamlit
    st.pyplot(fig)

def main():
    final_df = process_data()
    filtered_df = filter_by_data(final_df)
    display_coluns_graf(filtered_df)

    frame = pd.DataFrame(filtered_df)
    st.subheader("Tabela de ingressos")
    st.dataframe(frame)

    st.subheader("Pergunte ao chat GPT")
    pergunta = st.text_input('Digite sua pergunta com base nos dados:', '')

    if st.button("Enviar Pergunta"):
        if pergunta:
            resposta = ask_to_chat(pergunta, filtered_df)
            st.text_area("Resposta do ChatGPT", resposta, height=200)
        else:
            st.warning("Digite uma pergunta antes de enviar.")

main()