import streamlit as st
import pandas as pd
import numpy as np

# 🔹 Carregar os dados
# O arquivo dados_modelo.csv contém as colunas originais mais 'IAN_categoria', 'prob_risco' e 'nivel_risco'.
# Ele será usado para exibir todas as informações solicitadas.
try:
    df = pd.read_csv("dados_modelo.csv")
except FileNotFoundError:
    st.error("O arquivo 'dados_modelo.csv' não foi encontrado. Por favor, certifique-se de que o dataframe foi processado e salvo.")
    st.stop()

st.set_page_config(layout="wide", page_title="Ficha Detalhada do Aluno")

st.title("Ficha de Avaliação e Análise de Risco de Alunos")
st.markdown("---")

# 🔹 Entrada para busca de aluno por Nome ou RA
student_search_query = st.text_input(
    "🔍 Buscar aluno por Nome ou RA",
    placeholder="Ex: Aluno-1 ou RA-1...",
    help="Digite o nome completo ou parcial, ou o RA do aluno para pesquisar."
)

selected_student_data = None

if student_search_query:
    # Converter para minúsculas para busca case-insensitive e tratar valores NaN
    search_lower = student_search_query.lower()
    
    matching_students = df[
        df['Nome'].fillna('').str.lower().str.contains(search_lower, na=False) |
        df['RA'].fillna('').str.lower().str.contains(search_lower, na=False)
    ]

    if not matching_students.empty:
        if len(matching_students) > 1:
            st.subheader(f"Foram encontrados {len(matching_students)} alunos. Por favor, selecione um:")
            
            # Criar uma lista de opções formatadas para o selectbox
            student_options = matching_students.apply(
                lambda row: f"{row['Nome']} (RA: {row['RA']})", axis=1
            ).tolist()
            
            selected_option = st.selectbox("Selecione o aluno", student_options, index=0)
            
            if selected_option:
                # Extrair o RA da opção selecionada para encontrar a linha correspondente no DataFrame
                ra_from_option = selected_option.split('(RA: ')[-1][:-1]
                selected_student_data = matching_students[matching_students['RA'] == ra_from_option].iloc[0]
        else:
            selected_student_data = matching_students.iloc[0]
            st.success(f"Aluno '{selected_student_data['Nome']} (RA: {selected_student_data['RA']})' selecionado automaticamente.")
    else:
        st.warning("Nenhum aluno encontrado com o nome ou RA fornecido. Tente novamente.")
else:
    st.info("💡 Digite o nome ou RA de um aluno na caixa de busca acima para visualizar sua ficha detalhada.")

# 🔹 Exibir ficha detalhada do aluno selecionado
if selected_student_data is not None:
    st.markdown("---")
    st.header(f"Ficha Detalhada: {selected_student_data['Nome']} (RA: {selected_student_data['RA']})")

    # Função auxiliar para formatar valores, lidando com NaN
    def format_display_value(value, decimal_places=2, is_percentage=False):
        if pd.isna(value):
            return "Não disponível"
        if isinstance(value, (int, float)):
            if is_percentage:
                return f"{value:.{decimal_places}f}%"
            return f"{value:.{decimal_places}f}".replace('.', ',') # Use comma as decimal separator
        return str(value)

    # Layout de colunas para informações gerais e trajetória
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📜 Informações Gerais do Aluno")
        st.write(f"**Nome:** {format_display_value(selected_student_data['Nome'], 0)}")
        st.write(f"**RA:** {format_display_value(selected_student_data['RA'], 0)}")
        st.write(f"**Gênero:** {format_display_value(selected_student_data['Gênero'], 0)}")
        st.write(f"**Ano de Nascimento:** {format_display_value(selected_student_data['Ano nasc'], 0)}")
        st.write(f"**Idade (2022):** {format_display_value(selected_student_data['Idade 22'], 0)}")
        st.write(f"**Instituição de Ensino:** {format_display_value(selected_student_data['Instituição de ensino'], 0)}")

    with col2:
        st.subheader("🎓 Trajetória Acadêmica")
        st.write(f"**Ano de Ingresso:** {format_display_value(selected_student_data['Ano ingresso'], 0)}")
        st.write(f"**Fase Atual:** {format_display_value(selected_student_data['Fase'], 0)}")
        st.write(f"**Fase Ideal:** {format_display_value(selected_student_data['Fase ideal'], 0)}")
        st.write(f"**Defasagem Acadêmica:** {format_display_value(selected_student_data['Defas'], 0)}")
        
        # Exibindo 'Pedra' (Fase do Programa) e lidando com a limitação de dados anuais
        st.markdown("**Pedra (Fase do Programa):**")
        pedra_found = False
        for year in [20, 21, 22]: # Check for potential 'Pedra' columns (e.g., Pedra 20, Pedra 21, Pedra 22)
            col_name = f'Pedra {year}'
            if col_name in df.columns:
                pedra_value = selected_student_data[col_name]
                if pd.notna(pedra_value):
                    st.markdown(f"  - **{year}:** {pedra_value}")
                    pedra_found = True
        
        if not pedra_found:
            st.markdown("  - Não disponível.")
        
        # Clarificação sobre dados anuais da 'Pedra'
        if 'Pedra 20' in df.columns and 'Pedra 21' not in df.columns and 'Pedra 22' not in df.columns:
            st.info("⚠️ Informações detalhadas da 'Pedra' estão disponíveis apenas para o ano 2020 no dataset atual. Dados anuais podem não estar completos.")

    st.markdown("---")
    st.subheader("📊 Indicadores de Performance e Desenvolvimento")

    # Utilizando métricas para indicadores chave
    col_ida, col_ieg, col_iaa = st.columns(3)
    with col_ida:
        st.metric("IDA (Desempenho Acadêmico)", format_display_value(selected_student_data['IDA']))
    with col_ieg:
        st.metric("IEG (Engajamento)", format_display_value(selected_student_data['IEG']))
    with col_iaa:
        st.metric("IAA (Autoavaliação)", format_display_value(selected_student_data['IAA']))

    col_ipv, col_ian, col_ips = st.columns(3)
    with col_ipv:
        st.metric("IPV (Ponto de Virada)", format_display_value(selected_student_data['IPV']))
    with col_ian:
        st.metric("IAN (Adequação)", format_display_value(selected_student_data['IAN']))
    with col_ips:
        st.metric("IPS (Psicossocial)", format_display_value(selected_student_data['IPS']))

    st.markdown(f"**Categoria IAN:** {format_display_value(selected_student_data['IAN_categoria'], 0)}")

    st.markdown("---")
    st.subheader("🚨 Análise de Risco")
    
    col_risk_prob, col_risk_level = st.columns(2)
    with col_risk_prob:
        st.metric("Probabilidade de Risco", format_display_value(selected_student_data['prob_risco'] * 100, is_percentage=True))
    with col_risk_level:
        st.metric("Nível de Risco", format_display_value(selected_student_data['nivel_risco'], 0))

    st.markdown("---")
    st.subheader("⭐ Destaques (Melhorias e Pontos Fortes)")
    
    # Usar expanders para os destaques qualitativos
    with st.expander("Destaque IEG (Engajamento)"):
        st.write(format_display_value(selected_student_data['Destaque IEG'], 0))
    with st.expander("Destaque IDA (Desempenho Acadêmico)"):
        st.write(format_display_value(selected_student_data['Destaque IDA'], 0))
    with st.expander("Destaque IPV (Ponto de Virada)"):
        st.write(format_display_value(selected_student_data['Destaque IPV'], 0))
