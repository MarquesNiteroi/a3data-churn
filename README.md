# A3Data Churn

## Objetivo
Este repositório contém uma análise completa de churn para uma empresa de telecomunicações, com foco em:
1. Identificar os principais fatores associados ao churn
2. Treinar um modelo preditivo para priorizar ações de retenção
3. Traduzir os achados em recomendações acionáveis para o time de negócio

## Dados
• Base com cerca de 7 mil registros  
• 21 variáveis no total, sendo 20 explicativas e 1 alvo  
• Variável alvo: `Churn`  
• Taxa global de churn aproximada: 26.5%

## Entregáveis
1. Apresentação para o time de negócio na pasta `slides`
2. Relatórios e outputs na pasta `reports`
3. Código e notebooks reprodutíveis neste repositório

## Estrutura do repositório
• `notebooks/`  
  Notebooks com EDA, feature engineering, treino e avaliação

• `src/`  
  Código utilitário para carregar dados, preparar features, treinar e avaliar modelos

• `artifacts/`  
  Artefatos gerados durante treino e validação, por exemplo modelos serializados e métricas

• `reports/`  
  Tabelas, figuras e outputs exportáveis para leitura rápida

• `slides/`  
  Apresentação final

• `requirements.txt`  
  Dependências do projeto

• `.env.example`  
  Exemplo de variáveis de ambiente, se aplicável

## Como reproduzir localmente no Windows
### 1. Preparar ambiente Python
Abra um PowerShell no diretório do repositório e rode:

```powershell
Set-Location "C:\Repos\a3data-churn"; if (!(Test-Path ".\.venv")) { py -m venv .venv }; try { . .\.venv\Scripts\Activate.ps1 } catch { Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force; . .\.venv\Scripts\Activate.ps1 }; py -m pip install --upgrade pip; py -m pip install -r .\requirements.txt