"""RAG Document Copilot - Assistente de Leitura e Q&A sobre Documentos Técnicos.

Desenvolvido em Streamlit com busca vetorial local em Scikit-Learn (TF-IDF + Similaridade de Cosseno),
permite a operadores consultar contratos e manuais técnicos complexos em linguagem natural,
recuperando os trechos exatos (chunks) e sintetizando respostas contextualizadas e auditáveis.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st


# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="RAG Document Copilot",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# ESTRUTURA DE DADOS E BASE DE CONHECIMENTO EMBUTIDA
# ==============================================================================
@dataclass(frozen=True)
class DocumentChunk:
    """Representação de um fragmento (chunk) de documento indexado."""

    chunk_id: str
    doc_title: str
    doc_category: str
    section: str
    page: int
    content: str


def get_knowledge_base() -> List[DocumentChunk]:
    """Retorna os fragmentos estruturados dos contratos e manuais corporativos."""
    return [
        # ----------------------------------------------------------------------
        # DOCUMENTO 1: CONTRATO DE PRESTAÇÃO DE SERVIÇOS CLOUD & SAAS
        # ----------------------------------------------------------------------
        DocumentChunk(
            chunk_id="DOC-01-C01",
            doc_title="Contrato de Prestação de Serviços Cloud & SaaS",
            doc_category="Contratos Jurídicos",
            section="Cláusula 2.1 - Nível de Serviço e SLA de Disponibilidade",
            page=3,
            content=(
                "A CONTRATADA garante um nível de disponibilidade mensal de 99,95% (noventa e nove vírgula noventa e cinco por cento) "
                "para todos os serviços de infraestrutura cloud e banco de dados gerenciado. Caso a disponibilidade fique abaixo "
                "deste limiar em um determinado mês civil, a CONTRATANTE terá direito a crédito financeiro proporcional: 10% de crédito "
                "para SLA entre 99,00% e 99,94%, e 25% de crédito para SLA inferior a 99,00% sobre o valor da mensalidade."
            ),
        ),
        DocumentChunk(
            chunk_id="DOC-01-C02",
            doc_title="Contrato de Prestação de Serviços Cloud & SaaS",
            doc_category="Contratos Jurídicos",
            section="Cláusula 5.3 - Rescisão Antecipada e Multa Contratual",
            page=7,
            content=(
                "Qualquer das partes poderá rescindir o presente contrato mediante aviso prévio por escrito com antecedência mínima de 30 (trinta) dias. "
                "Em caso de rescisão imotivada por iniciativa da CONTRATANTE antes de completados os primeiros 12 (doze) meses de vigência, "
                "será aplicada multa rescisória compensatória equivalente a 20% (vinte por cento) do valor total das parcelas remanescentes "
                "até o encerramento do período contratual inicial."
            ),
        ),
        DocumentChunk(
            chunk_id="DOC-01-C03",
            doc_title="Contrato de Prestação de Serviços Cloud & SaaS",
            doc_category="Contratos Jurídicos",
            section="Cláusula 8.2 - Confidencialidade e Proteção de Dados (LGPD)",
            page=11,
            content=(
                "As partes concordam em manter estrita confidencialidade sobre todas as informações técnicas, comerciais e dados pessoais "
                "compartilhados durante a execução dos serviços, em conformidade com a Lei Federal nº 13.709/2018 (LGPD). O dever de sigilo "
                "e não divulgação permanecerá em vigor pelo período de 5 (cinco) anos subsequentes ao término ou rescisão do presente instrumento."
            ),
        ),
        DocumentChunk(
            chunk_id="DOC-01-C04",
            doc_title="Contrato de Prestação de Serviços Cloud & SaaS",
            doc_category="Contratos Jurídicos",
            section="Cláusula 4.4 - Janelas de Manutenção Programada",
            page=5,
            content=(
                "As janelas de manutenção preventiva programada serão realizadas exclusivamente aos domingos, no intervalo das 02h00 às 06h00 "
                "(Horário de Brasília), com notificação prévia à CONTRATANTE com no mínimo 72 (setenta e duas) horas de antecedência. "
                "As indisponibilidades ocorridas durante manutenções preventivas aprovadas não serão contabilizadas para penalidades de SLA."
            ),
        ),
        # ----------------------------------------------------------------------
        # DOCUMENTO 2: MANUAL TÉCNICO DE OPERAÇÃO E RECUPERAÇÃO DE SERVIDORES
        # ----------------------------------------------------------------------
        DocumentChunk(
            chunk_id="DOC-02-C01",
            doc_title="Manual Técnico de Operação de Servidores Cloud v2.4",
            doc_category="Manuais de Engenharia",
            section="Seção 3.2 - Procedimento de Boot em Modo de Recuperação (Rescue Mode)",
            page=14,
            content=(
                "Caso o servidor Linux não inicialize após corrupção do kernel ou falha no bootloader GRUB, o operador deve acessar o painel "
                "de controle do datacenter, selecionar o host afetado e acionar a opção 'Ativar Rescue Mode'. Em seguida, conecte-se via console "
                "serial VNC com as credenciais temporárias exibidas e execute o comando: 'mount /dev/sda1 /mnt && chroot /mnt' para montar "
                "as partições e reparar os pacotes do sistema."
            ),
        ),
        DocumentChunk(
            chunk_id="DOC-02-C02",
            doc_title="Manual Técnico de Operação de Servidores Cloud v2.4",
            doc_category="Manuais de Engenharia",
            section="Seção 4.1 - Política de Backups Automáticos e Snapshots",
            page=19,
            content=(
                "O sistema executa rotinas automáticas de snapshot a cada 4 (quatro) horas para volumes transacionais SSD, garantindo um RPO "
                "(Recovery Point Objective) máximo de 4 horas e RTO (Recovery Time Objective) de 45 minutos. Os snapshots diários são mantidos "
                "por 30 (trinta) dias e os backups mensais imutáveis são replicados geograficamente para outra região de disponibilidade."
            ),
        ),
        DocumentChunk(
            chunk_id="DOC-02-C03",
            doc_title="Manual Técnico de Operação de Servidores Cloud v2.4",
            doc_category="Manuais de Engenharia",
            section="Seção 5.3 - Troubleshooting de Falha de Conectividade e Firewall",
            page=26,
            content=(
                "Em caso de perda súbita de conectividade SSH ou timeout HTTP, verifique se a porta 22 ou 443 não foi bloqueada acidentalmente pelo "
                "serviço iptables/UFW. Execute 'ufw status verbose' para inspecionar as regras ativas. Para redefinir o firewall mantendo a segurança "
                "básica de emergência, execute 'ufw default deny incoming && ufw allow 22/tcp && ufw reload'."
            ),
        ),
        DocumentChunk(
            chunk_id="DOC-02-C04",
            doc_title="Manual Técnico de Operação de Servidores Cloud v2.4",
            doc_category="Manuais de Engenharia",
            section="Seção 6.2 - Redimensionamento e Escalonamento Vertical de Memória",
            page=31,
            content=(
                "O escalonamento vertical de memória RAM e vCPUs suporta Hot-Plug parcial nas instâncias da série Enterprise. No entanto, para "
                "instâncias Standard, a alteração de plano exige desligamento prévio (graceful shutdown) de 60 segundos antes de aplicar "
                "o novo perfil de hardware via comando CLI: 'cloud-cli server resize --id SRV-90 --plan c4.large'."
            ),
        ),
    ]


# ==============================================================================
# MOTOR DE BUSCA VETORIAL E RAG LOCAL (RETRIEVAL ENGINE)
# ==============================================================================
class LocalVectorRAGEngine:
    """Motor de indexação e busca vetorial local utilizando TF-IDF e Similaridade de Cosseno."""

    def __init__(self, chunks: List[DocumentChunk]) -> None:
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            stop_words=["a", "o", "de", "do", "da", "em", "para", "com", "na", "no", "se", "os", "as"],
        )
        self.corpus = [f"{c.doc_title} {c.section} {c.content}" for c in self.chunks]
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def retrieve(
        self, query: str, top_k: int = 3, min_similarity: float = 0.05
    ) -> List[Tuple[DocumentChunk, float]]:
        """Recupera os fragmentos mais relevantes com base na proximidade vetorial da consulta."""
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

        ranked_indices = np.argsort(similarities)[::-1]
        results: List[Tuple[DocumentChunk, float]] = []

        for idx in ranked_indices[:top_k]:
            sim = float(similarities[idx])
            if sim >= min_similarity:
                results.append((self.chunks[idx], round(sim, 4)))

        return results

    @staticmethod
    def generate_grounded_answer(
        query: str, retrieved: List[Tuple[DocumentChunk, float]]
    ) -> str:
        """Sintetiza uma resposta fundamentada estritamente nos trechos recuperados."""
        if not retrieved:
            return (
                "⚠️ **Nenhum trecho com relevância suficiente foi localizado** na base de documentos locais "
                "para responder à sua pergunta com segurança. Tente reformular usando termos técnicos presentes nos contratos ou manuais."
            )

        top_chunk, top_score = retrieved[0]
        confidence_label = "Alta" if top_score >= 0.25 else "Média" if top_score >= 0.12 else "Moderada"

        answer_parts = [
            f"Com base na análise documental do **{top_chunk.doc_title}** (*{top_chunk.section}*, pág. {top_chunk.page}), segue a resposta fundamentada:\n",
            f"> \"{top_chunk.content}\"\n",
            f"**Síntese Operacional:** A regra aplicável à sua consulta estabelece conformidade direta com a {top_chunk.section}. "
            f"A relevância da evidência recuperada possui grau de confiança **{confidence_label}** (Similaridade de Cosseno: {top_score * 100:.1f}%).",
        ]

        if len(retrieved) > 1:
            answer_parts.append(
                f"\n*Foram identificados outros {len(retrieved) - 1} trecho(s) correlato(s) complementar(es) detalhados abaixo.*"
            )

        return "\n".join(answer_parts)


@st.cache_resource
def get_rag_engine() -> LocalVectorRAGEngine:
    """Instancia e armazena em cache o motor de busca vetorial."""
    chunks = get_knowledge_base()
    return LocalVectorRAGEngine(chunks=chunks)


# ==============================================================================
# INTERFACE DO USUÁRIO STREAMLIT
# ==============================================================================
def main() -> None:
    rag_engine = get_rag_engine()

    # Inicialização do histórico de mensagens no Session State
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Olá! Sou seu **RAG Document Copilot**. Estou indexando localmente o "
                    "**Contrato de Prestação de Serviços Cloud & SaaS** e o "
                    "**Manual Técnico de Operação de Servidores v2.4**.\n\n"
                    "Faça qualquer pergunta sobre SLA, multas, modo de recuperação ou políticas de backup!"
                ),
                "sources": [],
            }
        ]

    # Barra Lateral
    with st.sidebar:
        st.title("📑 RAG Document Copilot")
        st.markdown(
            "Assistente de Q&A corporativo com **recuperação vetorial local (TF-IDF + Cosine Similarity)** "
            "e respostas fundamentadas (*Grounding*)."
        )
        st.divider()

        st.subheader("💡 Perguntas Frequentes (Atalhos)")
        exemplos = [
            "Qual o SLA de disponibilidade garantido?",
            "Qual a multa por rescisão antecipada?",
            "Qual é o dever de sigilo e prazo da LGPD?",
            "Como ativar o modo de recuperação (Rescue Mode)?",
            "Qual é o RPO e a política de backups?",
            "Quando ocorrem as janelas de manutenção?",
        ]

        for ex in exemplos:
            if st.button(f"📌 {ex}", use_container_width=True):
                st.session_state["prefill_query"] = ex

        st.divider()
        st.subheader("⚙️ Parâmetros de Recuperação")
        top_k = st.slider("Top-K Fragmentos Recuperados:", min_value=1, max_value=4, value=2)
        min_sim = st.slider("Limiar Mínimo de Similaridade:", min_value=0.01, max_value=0.30, value=0.05, step=0.01)

        with st.expander("📚 Base de Conhecimento Indexada (8 Chunks)"):
            for c in rag_engine.chunks:
                st.markdown(f"**{c.doc_title}**\n- *{c.section}* (Pág. {c.page})")

    # Cabeçalho da Área Principal
    st.markdown("## 🤖 RAG Document Copilot: Q&A sobre Manuais e Contratos")
    st.caption("Consulte cláusulas contratuais e procedimentos técnicos com citações auditáveis de páginas e seções.")

    # Exibição do Histórico de Chat
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("🔍 Evidências Documentais Recuperadas (Fontes Vetoriais)"):
                    for chunk, score in msg["sources"]:
                        st.markdown(
                            f"**Documento:** {chunk.doc_title} | **Página:** {chunk.page} | "
                            f"**Score de Similaridade:** `{score:.4f}`\n\n"
                            f"📌 **Seção:** `{chunk.section}`\n\n"
                            f"> {chunk.content}\n\n---"
                        )

    # Captura da Pergunta do Usuário
    prompt_from_button = st.session_state.pop("prefill_query", None)
    user_input = st.chat_input("Digite sua dúvida sobre os contratos ou manuais...") or prompt_from_button

    if user_input:
        # Registra a mensagem do usuário
        st.session_state["messages"].append({"role": "user", "content": user_input, "sources": []})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Processamento pelo RAG Engine
        with st.chat_message("assistant"):
            with st.spinner("Pesquisando embeddings e recuperando evidências textuais..."):
                time.sleep(0.3)  # Simula latência de inferência
                retrieved_chunks = rag_engine.retrieve(user_input, top_k=top_k, min_similarity=min_sim)
                bot_reply = rag_engine.generate_grounded_answer(user_input, retrieved_chunks)

                st.markdown(bot_reply)

                if retrieved_chunks:
                    with st.expander("🔍 Evidências Documentais Recuperadas (Fontes Vetoriais)", expanded=True):
                        for chunk, score in retrieved_chunks:
                            st.markdown(
                                f"**Documento:** {chunk.doc_title} | **Página:** {chunk.page} | "
                                f"**Score de Similaridade:** `{score:.4f}`\n\n"
                                f"📌 **Seção:** `{chunk.section}`\n\n"
                                f"> {chunk.content}\n\n---"
                            )

        # Salva resposta do assistente no histórico
        st.session_state["messages"].append(
            {"role": "assistant", "content": bot_reply, "sources": retrieved_chunks}
        )


if __name__ == "__main__":
    main()
