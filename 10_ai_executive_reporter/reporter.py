"""AI Executive Reporter - Gerador Automatizado de Relatórios Executivos em Markdown.

Consolida indicadores-chave de desempenho empresarial (receita, crescimento MoM,
taxa de conversão de funil, unit economics e métricas de retenção), processa os
dados estruturados e gera dinamicamente um briefing executivo de alto padrão
para tomada de decisão de C-Levels e Conselho de Administração.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class FinancialMetrics:
    """Indicadores financeiros consolidados."""

    current_revenue: float
    previous_revenue: float
    gross_margin_pct: float
    target_revenue: float

    @property
    def mom_growth_pct(self) -> float:
        """Calcula a taxa de crescimento Month-over-Month (MoM)."""
        if self.previous_revenue == 0:
            return 0.0
        return ((self.current_revenue - self.previous_revenue) / self.previous_revenue) * 100.0

    @property
    def target_achievement_pct(self) -> float:
        """Calcula o percentual de atingimento da meta mensal."""
        if self.target_revenue == 0:
            return 0.0
        return (self.current_revenue / self.target_revenue) * 100.0

    @property
    def projected_arr(self) -> float:
        """Projeta o ARR (Annual Recurring Revenue) anualizado."""
        return self.current_revenue * 12.0


@dataclass(frozen=True)
class CommercialFunnelMetrics:
    """Indicadores de funil comercial e eficiência de vendas."""

    total_leads: int
    qualified_leads_sql: int
    deals_closed: int
    average_ticket: float

    @property
    def global_conversion_rate_pct(self) -> float:
        """Taxa de conversão global de Leads para Clientes Fechados."""
        if self.total_leads == 0:
            return 0.0
        return (self.deals_closed / self.total_leads) * 100.0

    @property
    def sales_qualified_conversion_pct(self) -> float:
        """Taxa de conversão de Oportunidades Qualificadas (SQL) para Fechamento."""
        if self.qualified_leads_sql == 0:
            return 0.0
        return (self.deals_closed / self.qualified_leads_sql) * 100.0


@dataclass(frozen=True)
class UnitEconomicsMetrics:
    """Métricas de sustentabilidade financeira e saúde de base."""

    cac: float
    ltv: float
    monthly_churn_pct: float
    net_revenue_retention_pct: float

    @property
    def ltv_to_cac_ratio(self) -> float:
        """Relação LTV / CAC."""
        if self.cac == 0:
            return 0.0
        return self.ltv / self.cac


@dataclass
class BusinessUnitPerformance:
    """Desempenho por unidade de negócio ou categoria de produto."""

    unit_name: str
    revenue: float
    mom_growth_pct: float
    target_pct: float
    status: str


class ExecutiveReportGenerator:
    """Motor de geração dinâmica de relatórios executivos em Markdown."""

    def __init__(
        self,
        company_name: str = "Enterprise Cloud & Analytics S.A.",
        reference_period: str = "Outubro / 2026",
    ) -> None:
        self.company_name = company_name
        self.reference_period = reference_period

    def build_sample_data(
        self,
    ) -> Tuple[
        FinancialMetrics,
        CommercialFunnelMetrics,
        UnitEconomicsMetrics,
        List[BusinessUnitPerformance],
    ]:
        """Gera um conjunto corporativo realista e consistente de indicadores."""
        financials = FinancialMetrics(
            current_revenue=1_854_200.00,
            previous_revenue=1_618_500.00,
            gross_margin_pct=72.4,
            target_revenue=1_750_000.00,
        )

        funnel = CommercialFunnelMetrics(
            total_leads=4_820,
            qualified_leads_sql=940,
            deals_closed=178,
            average_ticket=10_416.85,
        )

        unit_econ = UnitEconomicsMetrics(
            cac=2_180.00,
            ltv=10_650.00,
            monthly_churn_pct=1.45,
            net_revenue_retention_pct=114.2,
        )

        business_units = [
            BusinessUnitPerformance(
                unit_name="Plataforma SaaS & Cloud Analytics",
                revenue=985_000.00,
                mom_growth_pct=18.2,
                target_pct=108.5,
                status="🟢 Superou Meta",
            ),
            BusinessUnitPerformance(
                unit_name="Serviços Profissionais & Consultoria IA",
                revenue=490_200.00,
                mom_growth_pct=14.5,
                target_pct=104.2,
                status="🟢 Superou Meta",
            ),
            BusinessUnitPerformance(
                unit_name="Integrações & Conectores de Dados",
                revenue=245_000.00,
                mom_growth_pct=8.1,
                target_pct=98.0,
                status="🟡 Dentro do Esperado",
            ),
            BusinessUnitPerformance(
                unit_name="Suporte Técnico Enterprise 24/7",
                revenue=134_000.00,
                mom_growth_pct=3.4,
                target_pct=92.5,
                status="🔴 Abaixo da Meta",
            ),
        ]

        return financials, funnel, unit_econ, business_units

    def generate_markdown_report(self) -> str:
        """Constrói o relatório executivo completo em sintaxe Markdown profissional."""
        financials, funnel, unit_econ, units = self.build_sample_data()
        now_str = datetime.now().strftime("%d/%m/%Y às %H:%M")

        # Avaliação geral de status executivo
        overall_badge = "🟢 FORTE EXPANSÃO" if financials.mom_growth_pct >= 10.0 else "🟡 ESTÁVEL"

        lines: List[str] = [
            f"# 📑 Executive Performance Briefing: {self.company_name}",
            "",
            f"> **Período de Referência:** {self.reference_period} | **Data de Emissão:** {now_str} | **Status Global:** {overall_badge}",
            "",
            "---",
            "",
            "## 1. 🎯 Executive Scorecard (Resumo em Alto Nível)",
            "",
            "O mês consolidou resultados expressivos com aceleração de receita acima do planejado no orçamento anual.",
            "",
            "| Indicador Chave (KPI) | Resultado Atual | Meta Mensal | Crescimento MoM | Status Executivo |",
            "| :--- | :---: | :---: | :---: | :---: |",
            f"| **Faturamento Líquido** | **R$ {financials.current_revenue:,.2f}** | R$ {financials.target_revenue:,.2f} | **{financials.mom_growth_pct:+.2f}%** | 🟢 Superou Meta ({financials.target_achievement_pct:.1f}%) |",
            f"| **ARR Anualizado (Run-Rate)** | **R$ {financials.projected_arr:,.2f}** | R$ 21,000,000.00 | {financials.mom_growth_pct:+.2f}% | 🟢 Ritmo Acelerado |",
            f"| **Margem Bruta Operacional** | **{financials.gross_margin_pct:.1f}%** | 70.0% | +2.4 p.p. | 🟢 Rentabilidade Saudável |",
            f"| **Taxa de Conversão Global** | **{funnel.global_conversion_rate_pct:.2f}%** | 3.20% | +0.49 p.p. | 🟢 Alta Eficiência |",
            f"| **Relação LTV / CAC** | **{unit_econ.ltv_to_cac_ratio:.2f}x** | 3.00x | +0.6x | 🟢 Unidades Econômicas Excelentes |",
            f"| **Churn Mensal de Receita** | **{unit_econ.monthly_churn_pct:.2f}%** | < 2.00% | -0.3 p.p. | 🟢 Retenção Controlada |",
            "",
            "---",
            "",
            "## 2. 💰 Performance Financeira & Tração de Receita",
            "",
            f"- **Receita Realizada:** **R$ {financials.current_revenue:,.2f}**, representando um incremento líquido de **R$ {financials.current_revenue - financials.previous_revenue:,.2f}** frente ao mês anterior (**{financials.mom_growth_pct:+.2f}% MoM**).",
            f"- **Atingimento Orçamentário:** O faturamento alcançou **{financials.target_achievement_pct:.1f}% da meta**, consolidando o quarto mês consecutivo de superação de forecast.",
            f"- **Margem de Contribuição:** A margem bruta fixou-se em **{financials.gross_margin_pct:.1f}%**, favorecida pelo ganho de escala da infraestrutura de servidores em nuvem.",
            "",
            "---",
            "",
            "## 3. 🚀 Eficiência Comercial & Conversão de Funil de Vendas",
            "",
            "| Etapa do Funil Comercial | Volume Absoluto | Taxa de Conversão | Benchmark Setorial |",
            "| :--- | :---: | :---: | :---: |",
            f"| **1. Leads Totais Gerados** | {funnel.total_leads:,} contatos | 100.0% | Topo de Funil |",
            f"| **2. Oportunidades Qualificadas (SQL)** | {funnel.qualified_leads_sql:,} SQLs | {(funnel.qualified_leads_sql / funnel.total_leads) * 100:.1f}% (Leads -> SQL) | Saudável (> 15%) |",
            f"| **3. Novos Contratos Fechados (Deals)** | **{funnel.deals_closed:,} clientes** | **{funnel.sales_qualified_conversion_pct:.1f}% (SQL -> Deals)** | Acima da Média (> 15%) |",
            f"| **Ticket Médio por Novo Cliente** | **R$ {funnel.average_ticket:,.2f}** | N/A | Ticket Enterprise Médio |",
            "",
            f"> **Insight de Vendas:** A conversão de SQL para fechamento (**{funnel.sales_qualified_conversion_pct:.1f}%**) reflete excelente qualificação pelo time de pré-vendas (SDRs) e alta aderência da proposta de valor.",
            "",
            "---",
            "",
            "## 4. 📊 Desempenho Segmentado por Unidade de Negócio",
            "",
            "| Unidade de Negócio / Produto | Faturamento (R$) | Crescimento MoM | Atingimento da Meta | Situação Operacional |",
            "| :--- | :---: | :---: | :---: | :---: |",
        ]

        total_u_rev = sum(u.revenue for u in units)
        for u in units:
            share = (u.revenue / total_u_rev) * 100
            lines.append(
                f"| **{u.unit_name}** | R$ {u.revenue:,.2f} ({share:.1f}%) | "
                f"{u.mom_growth_pct:+.1f}% | {u.target_pct:.1f}% | {u.status} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 5. 🔬 Unit Economics & Sustentabilidade de Escala",
            "",
            f"1. **Relação LTV / CAC ({unit_econ.ltv_to_cac_ratio:.2f}x):** Cada R$ 1,00 investido na aquisição de clientes gera R$ {unit_econ.ltv_to_cac_ratio:.2f} em retorno ao longo do ciclo de vida, bem acima da regra de ouro do mercado (3.0x).",
            f"2. **Custo de Aquisição (CAC: R$ {unit_econ.cac:,.2f}):** Payback estimado em apenas **{ (unit_econ.cac / (funnel.average_ticket * 0.40)) :.1f} meses**, permitindo reinvestimento agressivo em canais de mídia paga.",
            f"3. **Net Revenue Retention (NRR: {unit_econ.net_revenue_retention_pct:.1f}%):** O faturamento da base existente cresceu **14,2%** mesmo desconsiderando novos clientes, demonstrando forte tração de expansão e up-selling.",
            "",
            "---",
            "",
            "## 6. 📌 Recomendações Estratégicas para o Próximo Mês",
            "",
            f"1. **Expansão Comercial:** Alocar 15% a mais de verba no canal Inbound/Mídia para capitalizar sobre a taxa de conversão elevada (**{funnel.global_conversion_rate_pct:.2f}%**).",
            "2. **Atenção ao Suporte Enterprise:** A unidade de Suporte 24/7 fechou abaixo da meta (92,5%). Recomenda-se empacotar o suporte como diferencial embutido em planos anuais antecipados.",
            "3. **Retenção & CS:** Manter a rotina de Quarterly Business Reviews (QBRs) para blindar clientes de maior porte e sustentar o Churn abaixo de 1,5%.",
            "",
            "---",
            "*Relatório gerado de forma autônoma pelo motor `10_ai_executive_reporter`.*",
        ])

        return "\n".join(lines)

    def export_report(self, output_path: Path | str) -> Path:
        """Gera e salva o relatório em arquivo Markdown."""
        report_text = self.generate_markdown_report()
        target_file = Path(output_path)
        target_file.write_text(report_text, encoding="utf-8")
        return target_file


def main() -> None:
    """Execução do gerador de relatórios executivos."""
    base_dir = Path(__file__).resolve().parent

    print("=" * 80)
    print("🚀 INICIANDO AI EXECUTIVE REPORTER - GERAÇÃO AUTOMATIZADA DE BRIEFING")
    print("=" * 80)
    print(f"📁 Diretório de Trabalho: {base_dir.name}\n")

    reporter = ExecutiveReportGenerator(
        company_name="Enterprise Cloud & Analytics S.A.",
        reference_period="Outubro / 2026",
    )

    # 1. Geração do relatório em Markdown
    markdown_content = reporter.generate_markdown_report()

    # 2. Exibição da versão prévia diretamente no terminal
    print(markdown_content)

    # 3. Exportação do arquivo executive_briefing.md
    output_briefing = base_dir / "executive_briefing.md"
    reporter.export_report(output_briefing)

    print("\n" + "=" * 80)
    print(f"✅ Relatório executivo consolidado com sucesso em: {output_briefing.name}")
    print("=" * 80)


if __name__ == "__main__":
    main()
