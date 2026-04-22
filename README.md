# Knowledge RAG - The Myriad Veil Cosmos

Este projeto é um sistema de **RAG (Retrieval-Augmented Generation)** projetado para atuar como um assistente especializado no universo fictício "The Myriad Veil Cosmos". Ele utiliza uma base de conhecimento local para garantir que as respostas sejam precisas e fundamentadas exclusivamente na lore (história) fornecida.

## 🚀 Tecnologias

- **[Agno](https://agno.com/)**: Framework para construção de agentes de IA (anteriormente Phidata).
- **OpenRouter**: Interface para modelos de linguagem (configurado para usar `gpt-oss-120b`).
- **ChromaDB**: Banco de dados vetorial para armazenamento e busca de documentos.
- **Sentence Transformers**: Utiliza o modelo local `all-MiniLM-L6-v2` da Hugging Face para gerar embeddings.
- **Python 3.11+** com gerenciamento de dependências via **uv**.

## 🛠️ Configuração

1.  **Instale o `uv`** (caso não possua):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Sincronize o ambiente**:
    ```bash
    uv sync
    ```

3.  **Configure as variáveis de ambiente**:
    Crie um arquivo `.env` na raiz do projeto com sua chave da OpenRouter:
    ```text
    OPENROUTER_API_KEY=sua_chave_aqui
    ```

4.  **Adicione seus documentos**:
    Coloque os arquivos de texto ou manuais da lore na pasta `docs/`. O sistema irá indexar esses arquivos automaticamente.

## 📖 Como Usar

Para iniciar o agente e fazer uma consulta, execute:

```bash
uv run src/agent.py
```

O agente está configurado com restrições rigorosas para:
- Responder **apenas** com base no conhecimento recuperado dos seus documentos.
- Recusar-se a inventar detalhes ou usar conhecimentos externos ao "Myriad Veil Cosmos".
- Fornecer respostas detalhadas e estruturadas.

## 📁 Estrutura do Projeto

- `src/agent.py`: Configuração principal do Agente, Embedder e Banco de Dados.
- `docs/`: Repositório de documentos para a base de conhecimento.
- `tmp/chromadb/`: Pasta local onde os dados vetoriais são salvos.
- `.env`: Arquivo para chaves de API (não versionado).

---
Criado para exploração imersiva de lore.
